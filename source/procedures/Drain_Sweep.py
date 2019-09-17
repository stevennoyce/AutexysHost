# === Imports ===
import time
import numpy as np

import pipes
#from procedures import Device_History as deviceHistoryScript
from utilities import DataLoggerUtility as dlu
from utilities import SequenceGeneratorUtility as dgu



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]
	
	# Get shorthand name to easily refer to configuration parameters
	ds_parameters = parameters['runConfigs']['DrainSweep']

	# Print the starting message
	print('Sweeping the drain: V_GS='+str(ds_parameters['gateVoltageSetPoint'])+'V, min V_DS='+str(ds_parameters['drainVoltageMinimum'])+'V, max V_DS='+str(ds_parameters['drainVoltageMaximum'])+'V')
	smu_instance.setComplianceCurrent(ds_parameters['complianceCurrent'])	

	# === START ===
	# Apply drain voltage
	print('Ramping gate voltage.')
	smu_instance.rampGateVoltageTo(ds_parameters['gateVoltageSetPoint'])
	
	print('Beginning to sweep drain voltage.')
	results = runDrainSweep(smu_instance, 
							isFastSweep=ds_parameters['isFastSweep'],
							fastSweepSpeed=ds_parameters['fastSweepSpeed'],
							gateVoltageSetPoint=ds_parameters['gateVoltageSetPoint'],
							drainVoltageMinimum=ds_parameters['drainVoltageMinimum'], 
							drainVoltageMaximum=ds_parameters['drainVoltageMaximum'], 
							stepsInVDSPerDirection=ds_parameters['stepsInVDSPerDirection'],
							pointsPerVDS=ds_parameters['pointsPerVDS'],
							drainVoltageRamps=ds_parameters['drainVoltageRamps'],
							delayBetweenMeasurements=ds_parameters['delayBetweenMeasurements'],
							share=share)
	smu_instance.rampDownVoltages()
	# === COMPLETE ===

	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']
	
	# Print the metrics
	print('Max conductance: {:.4e}'.format(results['Computed']['G_max']))
	print('Max drain current: {:.4e}'.format(results['Computed']['id_max']))
	print('Max gate current: {:.4e}'.format(results['Computed']['ig_max']))
	

	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
		
	# Save results as a JSON object
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), ds_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))
		
	return jsonData

# === Data Collection ===
def runDrainSweep(smu_instance, isFastSweep, fastSweepSpeed, gateVoltageSetPoint, drainVoltageMinimum, drainVoltageMaximum, stepsInVDSPerDirection, pointsPerVDS, drainVoltageRamps, delayBetweenMeasurements, share=None):
	# Generate list of drain voltages to apply
	drainVoltages = dgu.sweepValuesWithDuplicates(drainVoltageMinimum, drainVoltageMaximum, stepsInVDSPerDirection*2*pointsPerVDS, pointsPerVDS, ramps=drainVoltageRamps)
	
	vds_data   = [[] for i in range(len(drainVoltages))]
	id_data    = [[] for i in range(len(drainVoltages))]
	vgs_data   = [[] for i in range(len(drainVoltages))]
	ig_data    = [[] for i in range(len(drainVoltages))]
	timestamps = [[] for i in range(len(drainVoltages))]
	
	# Ramp drain and wait a second for everything to settle down
	smu_instance.rampDrainVoltageTo(drainVoltageMinimum)
	time.sleep(1)

	if(isFastSweep):
		triggerInterval = 1/fastSweepSpeed
		
		# Convert drain and gate voltages into 1-D arrays that the SMU can read
		gateVoltageList = [gateVoltageSetPoint]
		drainVoltageList = []
		for i in range(len(drainVoltages)):
			drainVoltageList.extend(drainVoltages[i])
		
		# Use SMU built-in sweep to sweep the gate forwards and backwards
		measurements = smu_instance.takeSweep(None, None, None, None, points=stepsInVDSPerDirection*2*pointsPerVDS, triggerInterval=triggerInterval, src1vals=drainVoltageList, src2vals=gateVoltageList)

		# Save forward measurements
		vds_data[0]   = measurements['Vds_data'][0:stepsInVDSPerDirection*pointsPerVDS]
		id_data[0]    = measurements['Id_data'][0:stepsInVDSPerDirection*pointsPerVDS]
		vgs_data[0]   = measurements['Vgs_data'][0:stepsInVDSPerDirection*pointsPerVDS]
		ig_data[0]    = measurements['Ig_data'][0:stepsInVDSPerDirection*pointsPerVDS]
		timestamps[0] = measurements['timestamps'][0:stepsInVDSPerDirection*pointsPerVDS]

		# Save reverse measurements
		vds_data[1]   = measurements['Vds_data'][stepsInVDSPerDirection*pointsPerVDS:]
		id_data[1]    = measurements['Id_data'][stepsInVDSPerDirection*pointsPerVDS:]
		vgs_data[1]   = measurements['Vgs_data'][stepsInVDSPerDirection*pointsPerVDS:]
		ig_data[1]    = measurements['Ig_data'][stepsInVDSPerDirection*pointsPerVDS:]
		timestamps[1] = measurements['timestamps'][stepsInVDSPerDirection*pointsPerVDS:]
	else:
		for direction in range(len(drainVoltages)):
			for Vdi, drainVoltage in enumerate(drainVoltages[direction]):
				# Send a progress message
				pipes.progressUpdate(share, 'Drain Sweep Point', start=1, current=direction*len(drainVoltages[0])+Vdi+1, end=len(drainVoltages)*len(drainVoltages[0]))
					
				# Apply V_DS
				smu_instance.setVds(drainVoltage)

				# If delayBetweenMeasurements is non-zero, wait before taking the measurement
				if(delayBetweenMeasurements > 0):
					time.sleep(delayBetweenMeasurements)

				# Take Measurement and save it
				measurement = smu_instance.takeMeasurement()

				timestamp = time.time()
				
				vds_data[direction].append(measurement['V_ds'])
				id_data[direction].append(measurement['I_d'])
				vgs_data[direction].append(measurement['V_gs'])
				ig_data[direction].append(measurement['I_g'])
				timestamps[direction].append(timestamp)

				# Send a data message
				pipes.livePlotUpdate(share,
						xData={'Drain Voltage [V]': drainVoltage if abs((drainVoltage - measurement['V_ds'])) < abs(0.1*drainVoltage) else measurement['V_ds'],
						'Time [s]': timestamp - timestamps[0][0]},
						yData={'Drain Current {} [A]'.format(direction + 1): measurement['I_d'],
						'Gate Current {} [A]'.format(direction + 1): measurement['I_g']})

	return {
		'Raw':{
			'vds_data':vds_data,
			'id_data':id_data,
			'vgs_data':vgs_data,
			'ig_data':ig_data,
			'timestamps':timestamps,
			'drainVoltages':drainVoltages,
		},
		'Computed':{
			'id_max':max(abs(np.array(id_data[0] + id_data[1]))),
			'G_max':max(abs(np.array(id_data[0] + id_data[1]) / np.array(vds_data[0] + vds_data[1]))),
			'ig_max':max(abs(np.array(ig_data[0] + ig_data[1])))
		}
	}

	