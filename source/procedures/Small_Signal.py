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
	ss_parameters = parameters['runConfigs']['SmallSignal']

	# Print the starting message
	print('Applying sinusoidal small-signal: V_GS='+str(ss_parameters['gateVoltageSetPoint'])+'V, v_gs='+str(ss_parameters['gateVoltageAmplitude'])+'V, V_DS='+str(ss_parameters['drainVoltageSetPoint'])+'V, v_ds='+str(ss_parameters['drainVoltageAmplitude'])+'V.')
	smu_instance.setComplianceCurrent(ss_parameters['complianceCurrent'])

	# === START ===
	# Apply bias voltages (or change channels to high-resistance mode)
	print('Applying bias voltages.')
	if(ss_parameters['supplyDrainVoltage']):
		smu_instance.rampDrainVoltageTo(ss_parameters['drainVoltageSetPoint'])
		print('Applied drain voltage.')
	else:
		smu_instance.setChannel1SourceMode(mode='current')
		smu_instance.setId(0)
	
	if(ss_parameters['supplyGateVoltage']):
		smu_instance.rampGateVoltageTo(ss_parameters['gateVoltageSetPoint'])
		print('Applied gate voltage.')
	else:
		smu_instance.setChannel2SourceMode(mode='current')
		smu_instance.setIg(0)	

	# Delay to allow start-up transients to settle to the DC operating point
	time.sleep(0.1)

	print('Beginning to measure sinusoidal small-signal response.')
	results = runSmallSignal( smu_instance,
							gateVoltageSetPoint=ss_parameters['gateVoltageSetPoint'],
							drainVoltageSetPoint=ss_parameters['drainVoltageSetPoint'],
							gateVoltageAmplitude=ss_parameters['gateVoltageAmplitude'],
							drainVoltageAmplitude=ss_parameters['drainVoltageAmplitude'],
							frequencies=ss_parameters['frequencies'],
							stepsPerPeriod=ss_parameters['stepsPerPeriod'],
							supplyGateVoltage=ss_parameters['supplyGateVoltage'],
							supplyDrainVoltage=ss_parameters['supplyDrainVoltage'],
							share=share)
	
	# Ramp down channels
	smu_instance.rampDownVoltages()
	# === COMPLETE ===

	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']

	# Print the metrics
	print('Drain current amplitudes: ' + str(results['Computed']['id_amplitudes']))
	print('Gate current amplitudes: ' + str(results['Computed']['ig_amplitudes']))

	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']

	# Save results as a JSON object
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), ss_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))

	return jsonData

# === Data Collection ===
def runSmallSignal(smu_instance, gateVoltageSetPoint, drainVoltageSetPoint, gateVoltageAmplitude, drainVoltageAmplitude, frequencies, stepsPerPeriod, supplyGateVoltage, supplyDrainVoltage, share=None):
	vds_data   = [[] for i in range(len(frequencies))]
	id_data    = [[] for i in range(len(frequencies))]
	vgs_data   = [[] for i in range(len(frequencies))]
	ig_data    = [[] for i in range(len(frequencies))]
	timestamps = [[] for i in range(len(frequencies))]
	
	# Generate list of sinusoidal gate and drain voltages to apply
	gateVoltages  = [dgu.sineValues(gateVoltageSetPoint, gateVoltageAmplitude, periods=6, points=stepsPerPeriod*6)   for i in range(len(frequencies))]
	drainVoltages = [dgu.sineValues(drainVoltageSetPoint, drainVoltageAmplitude, periods=6, points=stepsPerPeriod*6) for i in range(len(frequencies))]

	for frequencyIndex in range(len(frequencies)):
		for voltageIndex in range(len(gateVoltages[frequencyIndex])):
			# Send a progress message
			pipes.progressUpdate(share, 'Small-Signal Point', start=0, current=frequencyIndex*len(gateVoltages[0])+voltageIndex+1, end=len(gateVoltages)*len(gateVoltages[0]))

			gateVoltage = gateVoltages[frequencyIndex][voltageIndex]
			drainVoltage = drainVoltages[frequencyIndex][voltageIndex]
			delayBetweenMeasurements = max(0, (1/(frequencies[frequencyIndex]*stepsPerPeriod)) - (1/smu_instance.measurementsPerSecond))

			# Apply V_GS and V_DS (only issue commands that affect the voltage)
			if(supplyGateVoltage and ((voltageIndex == 0) or (gateVoltage != gateVoltages[frequencyIndex][voltageIndex-1]))):
				smu_instance.setVgs(gateVoltage)
			if(supplyDrainVoltage and ((voltageIndex == 0) or (drainVoltage != drainVoltages[frequencyIndex][voltageIndex-1]))):
				smu_instance.setVds(drainVoltage)

			# Wait for the appropriate time step
			time.sleep(delayBetweenMeasurements)

			# Take Measurement and save it
			measurement = smu_instance.takeMeasurement()

			timestamp = time.time()

			vds_data[frequencyIndex].append(measurement['V_ds'])
			id_data[frequencyIndex].append(measurement['I_d'])
			vgs_data[frequencyIndex].append(measurement['V_gs'])
			ig_data[frequencyIndex].append(measurement['I_g'])
			timestamps[frequencyIndex].append(timestamp)

			# Send a data message
			pipes.livePlotUpdate(share, plots=
			[livePlotter.createLiveDataPoint(plotID='Response vs. Time', 
											labels=['Drain Current', 'Gate Current'],
											xValues=[timestamp, timestamp], 
											yValues=[measurement['I_d'], measurement['I_g']], 
											#colors=['', '#4FB99F'],
											xAxisTitle='Time (s)', 
											yAxisTitle='Current (A)', 
											yscale='linear', 
											plotMode='lines',
											enumerateLegend=True,
											timeseries=True),
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
			'id_amplitudes':[max(segment) - min(segment) for segment in id_data],
			'ig_amplitudes':[max(segment) - min(segment) for segment in ig_data],
		}
	}




	