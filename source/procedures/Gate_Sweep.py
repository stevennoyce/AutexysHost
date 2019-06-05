# === Imports ===
import time
import numpy as np

import pipes
from procedures import Device_History as deviceHistoryScript
from utilities import DataLoggerUtility as dlu
from utilities import SequenceGeneratorUtility as dgu



# === Main ===
def run(parameters, smu_instance, isSavingResults=True, isPlottingResults=False, communication_pipe=None):
	# Create distinct parameters for plotting the results
	dh_parameters = {}
	dh_parameters['Identifiers'] = dict(parameters['Identifiers'])
	dh_parameters['dataFolder'] = parameters['dataFolder']
	dh_parameters['plotGateSweeps'] = True
	dh_parameters['plotBurnOuts'] = False
	dh_parameters['plotStaticBias'] = False
	dh_parameters['excludeDataBeforeJSONExperimentNumber'] = parameters['startIndexes']['experimentNumber']
	dh_parameters['excludeDataAfterJSONExperimentNumber'] =  parameters['startIndexes']['experimentNumber']

	# Get shorthand name to easily refer to configuration parameters
	gs_parameters = parameters['runConfigs']['GateSweep']

	# Print the starting message
	print('Sweeping the gate: V_DS='+str(gs_parameters['drainVoltageSetPoint'])+'V, min V_GS='+str(gs_parameters['gateVoltageMinimum'])+'V, max V_GS='+str(gs_parameters['gateVoltageMaximum'])+'V')
	smu_instance.setComplianceCurrent(gs_parameters['complianceCurrent'])	

	# === START ===
	# Apply drain voltage
	print('Ramping drain voltage.')
	smu_instance.rampDrainVoltageTo(gs_parameters['drainVoltageSetPoint'])
	
	print('Beginning to sweep gate voltage.')
	results = runGateSweep( smu_instance, 
							isFastSweep=gs_parameters['isFastSweep'],
							fastSweepSpeed=gs_parameters['fastSweepSpeed'],
							drainVoltageSetPoint=gs_parameters['drainVoltageSetPoint'],
							gateVoltageMinimum=gs_parameters['gateVoltageMinimum'], 
							gateVoltageMaximum=gs_parameters['gateVoltageMaximum'], 
							stepsInVGSPerDirection=gs_parameters['stepsInVGSPerDirection'],
							pointsPerVGS=gs_parameters['pointsPerVGS'],
							gateVoltageRamps=gs_parameters['gateVoltageRamps'],
							communication_pipe=communication_pipe)
	smu_instance.rampDownVoltages()
	# === COMPLETE ===

	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']
	
	# Print the metrics
	print('On/Off ratio: {:.4f}'.format(results['Computed']['onOffRatio']))
	print('On current: {:.4e}'.format(results['Computed']['onCurrent']))
	print('Off current: {:.4e}'.format(results['Computed']['offCurrent']))
	print('Max gate current: {:.4e}'.format(results['Computed']['ig_max']))

	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
		
	# Save results as a JSON object
	if(isSavingResults):
		print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
		dlu.saveJSON(dlu.getDeviceDirectory(parameters), gs_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))

	# Show plots to the user
	if(isPlottingResults):
		deviceHistoryScript.run(dh_parameters)
		
	return jsonData

# === Data Collection ===
def runGateSweep(smu_instance, isFastSweep, fastSweepSpeed, drainVoltageSetPoint, gateVoltageMinimum, gateVoltageMaximum, stepsInVGSPerDirection, pointsPerVGS, gateVoltageRamps, communication_pipe=None):
	# Generate list of gate voltages to apply
	gateVoltages = dgu.sweepValuesWithDuplicates(gateVoltageMinimum, gateVoltageMaximum, stepsInVGSPerDirection*2*pointsPerVGS, pointsPerVGS, ramps=gateVoltageRamps)
	
	vds_data   = [[] for i in range(len(gateVoltages))]
	id_data    = [[] for i in range(len(gateVoltages))]
	vgs_data   = [[] for i in range(len(gateVoltages))]
	ig_data    = [[] for i in range(len(gateVoltages))]
	timestamps = [[] for i in range(len(gateVoltages))]
	
	# Ramp gate and wait a second for everything to settle down
	smu_instance.rampGateVoltageTo(gateVoltageMinimum)
	time.sleep(1)
	
	if(isFastSweep):
		triggerInterval = 1/fastSweepSpeed
		
		# Convert drain and gate voltages into 1-D arrays that the SMU can read
		drainVoltageList = [drainVoltageSetPoint]
		gateVoltageList = []
		for i in range(len(gateVoltages)):
			gateVoltageList.extend(gateVoltages[i])
		
		# Use SMU built-in sweep to sweep the gate forwards and backwards
		measurements = smu_instance.takeSweep(None, None, None, None, points=stepsInVGSPerDirection*2*pointsPerVGS, triggerInterval=triggerInterval, src1vals=drainVoltageList, src2vals=gateVoltageList)

		# Save forward measurements
		vds_data[0]   = measurements['Vds_data'][0:stepsInVGSPerDirection*pointsPerVGS]
		id_data[0]    = measurements['Id_data'][0:stepsInVGSPerDirection*pointsPerVGS]
		vgs_data[0]   = measurements['Vgs_data'][0:stepsInVGSPerDirection*pointsPerVGS]
		ig_data[0]    = measurements['Ig_data'][0:stepsInVGSPerDirection*pointsPerVGS]
		timestamps[0] = measurements['timestamps'][0:stepsInVGSPerDirection*pointsPerVGS]

		# Save reverse measurements
		vds_data[1]   = measurements['Vds_data'][stepsInVGSPerDirection*pointsPerVGS:]
		id_data[1]    = measurements['Id_data'][stepsInVGSPerDirection*pointsPerVGS:]
		vgs_data[1]   = measurements['Vgs_data'][stepsInVGSPerDirection*pointsPerVGS:]
		ig_data[1]    = measurements['Ig_data'][stepsInVGSPerDirection*pointsPerVGS:]
		timestamps[1] = measurements['timestamps'][stepsInVGSPerDirection*pointsPerVGS:]
	else:
		for direction in range(len(gateVoltages)):
			for Vgi, gateVoltage in enumerate(gateVoltages[direction]):
				# Send a progress message
				pipes.send(communication_pipe, {
					'destination':'UI',
					'type':'Progress',
					'progress': {
						'Gate Sweep Point': {
							'start': 1,
							'current': direction*len(gateVoltages[0])+Vgi+1,
							'end': len(gateVoltages)*len(gateVoltages[0])
						}
					}
				})
				
				# Apply V_GS
				smu_instance.setVgs(gateVoltage)

				# Take Measurement and save it
				measurement = smu_instance.takeMeasurement()

				timestamp = time.time()
				
				vds_data[direction].append(measurement['V_ds'])
				id_data[direction].append(measurement['I_d'])
				vgs_data[direction].append(measurement['V_gs'])
				ig_data[direction].append(measurement['I_g'])
				timestamps[direction].append(timestamp)

	return {
		'Raw':{
			'vds_data':vds_data,
			'id_data':id_data,
			'vgs_data':vgs_data,
			'ig_data':ig_data,
			'timestamps':timestamps,
			'gateVoltages':gateVoltages,
		},
		'Computed':{
			'onOffRatio':onOffRatio(id_data),
			'onCurrent':onCurrent(id_data),
			'offCurrent':offCurrent(id_data),
			'ig_max':max(abs(np.array(ig_data[0] + ig_data[1])))
		}
	}

def onOffRatio(drainCurrent):
	return onCurrent(drainCurrent)/offCurrent(drainCurrent)

def onCurrent(drainCurrent):
	absDrainCurrent = abs(np.array(drainCurrent))
	return np.percentile(absDrainCurrent, 99)

def offCurrent(drainCurrent):
	absDrainCurrent = abs(np.array(drainCurrent))
	return (np.percentile(absDrainCurrent, 5))

	