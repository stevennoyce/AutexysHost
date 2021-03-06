# === Imports ===
import time
import numpy as np

import pipes
import Live_Plot_Data_Point as livePlotter
from utilities import DataLoggerUtility as dlu
from utilities import SequenceGeneratorUtility as dgu



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]

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
							delayBetweenMeasurements=gs_parameters['delayBetweenMeasurements'],
							share=share)
	
	# Ramp down channels
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
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), gs_parameters['saveFileName'], jsonData, subDirectory=parameters['experimentSubFolder']+str(parameters['startIndexes']['experimentNumber']))

	return jsonData

# === Data Collection ===
def runGateSweep(smu_instance, isFastSweep, fastSweepSpeed, drainVoltageSetPoint, gateVoltageMinimum, gateVoltageMaximum, stepsInVGSPerDirection, pointsPerVGS, gateVoltageRamps, delayBetweenMeasurements, share=None):
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
		measurements = smu_instance.takeSweep(drainVoltageSetPoint, drainVoltageSetPoint, gateVoltageMinimum, gateVoltageMaximum, points=stepsInVGSPerDirection*2*pointsPerVGS, triggerInterval=triggerInterval, src1vals=drainVoltageList, src2vals=gateVoltageList)

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
				pipes.progressUpdate(share, 'Gate Sweep Point', start=0, current=direction*len(gateVoltages[0])+Vgi+1, end=len(gateVoltages)*len(gateVoltages[0]))

				# Apply V_GS
				smu_instance.setVgs(gateVoltage)

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
				preppedGateVoltage = gateVoltage if abs((gateVoltage - measurement['V_gs'])) < abs(0.1*gateVoltage) else measurement['V_gs']
				pipes.livePlotUpdate(share, plots=
				[livePlotter.createLiveDataPoint(plotID='Transfer Curve', 
												labels=['Drain Current', 'Gate Current'],
												xValues=[preppedGateVoltage, preppedGateVoltage], 
												yValues=[measurement['I_d'], measurement['I_g']], 
												#colors=['', '#4FB99F'],
												xAxisTitle='Gate Voltage (V)', 
												yAxisTitle='Current (A)', 
												yscale='linear', 
												plotMode='lines',
												enumerateLegend=True,
												timeseries=False),
				 livePlotter.createLiveDataPoint(plotID='Subthreshold Curve', 
												labels=['Drain Current', 'Gate Current'],
												xValues=[preppedGateVoltage, preppedGateVoltage], 
												yValues=[abs(measurement['I_d']), abs(measurement['I_g'])], 
												#colors=['', '#4FB99F'],
												xAxisTitle='Gate Voltage (V)', 
												yAxisTitle='Current (A)', 
												yscale='log', 
												plotMode='lines',
												enumerateLegend=True,
												timeseries=False),
				])
			livePlotter.incrementActivePlots()
			
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
			'ig_max':np.max(np.abs(ig_data))
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

	