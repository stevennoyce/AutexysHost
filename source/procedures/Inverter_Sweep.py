# === Imports ===
import time
import numpy as np

from utilities import DataLoggerUtility as dlu
from utilities import SequenceGeneratorUtility as dgu



# === Main ===
def run(parameters, smu_systems, isSavingResults=True):
	# Get shorthand name to easily refer to configuration parameters
	is_parameters = parameters['runConfigs']['GateSweep']

	smu_sweep = smu_systems['sweepSMU']
	smu_vdd = smu_systems['powerSupplySMU']

	# Print the starting message
	print('Sweeping the inverter: V_DD='+str(is_parameters['vddSupplyVoltageSetPoint'])+'V, min V_IN='+str(is_parameters['inputVoltageMinimum'])+'V, max V_IN='+str(is_parameters['inputVoltageMaximum'])+'V')
	smu_sweep.setComplianceCurrent(is_parameters['complianceCurrent'])	
	smu_vdd.setComplianceVoltage(is_parameters['complianceCurrent'])	

	# === START ===
	# Apply drain voltage
	print('Ramping supply voltage (VDD).')
	smu_vdd.rampDrainVoltageTo(is_parameters['vddSupplyVoltageSetPoint'])
	
	# Switch Channel 2 of smu_sweep into current-sourcing mode so that it can measure V_OUT without applying a voltage to the output side
	smu_sweep.setChannel2SourceMode(mode="current")
	smu_sweep.setParameter(":source2:current 0.0")
	
	print('Beginning to sweep input voltage.')
	results = runInverterSweep( smu_sweep, 
							isFastSweep=is_parameters['isFastSweep'],
							inputVoltageMinimum=is_parameters['inputVoltageMinimum'], 
							inputVoltageMaximum=is_parameters['inputVoltageMaximum'], 
							stepsInVINPerDirection=is_parameters['stepsInVINPerDirection'],
							pointsPerVIN=is_parameters['pointsPerVIN'])
	
	smu_vdd.rampDownVoltages()
	#smu_instance.rampDownVoltages()
	# === COMPLETE ===

	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']
	
	# Print the metrics
	print('Max input current: {:.4e}'.format(results['Computed']['iin_max']))
	print('Min input current: {:.4e}'.format(results['Computed']['iin_min']))
	print('Max output current: {:.4e}'.format(results['Computed']['iout_max']))
	print('Min output current: {:.4e}'.format(results['Computed']['iout_min']))

	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
		
	# Save results as a JSON object
	if(isSavingResults):
		print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
		dlu.saveJSON(dlu.getDeviceDirectory(parameters), is_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))

	return jsonData

# === Data Collection ===
def runInverterSweep(smu_sweep, inputVoltageMinimum, inputVoltageMaximum, stepsInVINPerDirection, pointsPerVIN):
	vin_data = [[],[]]
	iin_data = [[],[]]
	vout_data = [[],[]]
	iout_data = [[],[]]
	timestamps = [[],[]]

	# Generate list of input voltages to apply
	inputVoltages = dgu.sweepValuesWithDuplicates(inputVoltageMinimum, inputVoltageMaximum, stepsInVINPerDirection*2*pointsPerVIN, pointsPerVIN)
	
	# Ramp V_IN and wait a second for everything to settle down
	smu_sweep.rampDrainVoltageTo(inputVoltageMinimum)
	#time.sleep(1)

	for direction in [0,1]:
		for inputVoltage in inputVoltages[direction]:
			# Apply V_IN
			smu_sweep.setVds(inputVoltage)

			# Take Measurement and save it
			measurement = smu_sweep.takeMeasurement()

			timestamp = time.time()
			
			vin_data[direction].append(measurement['V_ds'])
			iin_data[direction].append(measurement['I_d'])
			vout_data[direction].append(measurement['V_gs'])
			iout_data[direction].append(measurement['I_g'])
			timestamps[direction].append(timestamp)

	# Ramp V_IN down to zero
	smu_sweep.rampDrainVoltageDown()

	return {
		'Raw':{
			'vin_data':vin_data,
			'iin_data':iin_data,
			'vout_data':vout_data,
			'iout_data':iout_data,
			'timestamps':timestamps,
			'inputVoltages':inputVoltages,
		},
		'Computed':{
			'iin_max':  max(abs(np.array(iin_data[0] + iin_data[1]))),
			'iin_min':  min(abs(np.array(iin_data[0] + iin_data[1]))),
			'iout_max': max(abs(np.array(iout_data[0] + iout_data[1]))),
			'iout_min': min(abs(np.array(iout_data[0] + iout_data[1]))),
		}
	}


	