# === Imports ===
import time
import numpy as np

import pipes
import Live_Plot_Data_Point as livePlotter
from utilities import DataLoggerUtility as dlu
from procedures import Gate_Sweep as gateSweepScript



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses two SMUs, one for applying the power supply and one for measuring VIN/VOUT
	smu_sweep = smu_systems['sweepSMU']
	smu_vdd = smu_systems['powerSupplySMU']
	
	# Get shorthand name to easily refer to configuration parameters
	is_parameters = parameters['runConfigs']['InverterSweep']

	# Translate configuration parameters to perform the input voltage sweep as a gate sweep
	gateSweepParameters = dict(parameters)
	gateSweepParameters['runType'] = 'GateSweep'
	gateSweepParameters['runConfigs']['GateSweep']['gateVoltageMinimum']       = is_parameters['inputVoltageMinimum']
	gateSweepParameters['runConfigs']['GateSweep']['gateVoltageMaximum']       = is_parameters['inputVoltageMaximum']
	gateSweepParameters['runConfigs']['GateSweep']['drainVoltageSetPoint']     = 0
	gateSweepParameters['runConfigs']['GateSweep']['complianceCurrent']        = is_parameters['complianceCurrent']
	gateSweepParameters['runConfigs']['GateSweep']['stepsInVGSPerDirection']   = is_parameters['stepsInVINPerDirection']
	gateSweepParameters['runConfigs']['GateSweep']['pointsPerVGS']             = is_parameters['pointsPerVIN']
	gateSweepParameters['runConfigs']['GateSweep']['gateVoltageRamps']         = is_parameters['inputVoltageRamps']
	gateSweepParameters['runConfigs']['GateSweep']['delayBetweenMeasurements'] = is_parameters['delayBetweenMeasurements']
	gateSweepParameters['runConfigs']['GateSweep']['isFastSweep']              = False
	gateSweepParameters['runConfigs']['GateSweep']['supplyDrainVoltage']       = False

	# Print the starting message
	print('Sweeping the inverter: V_DD='+str(is_parameters['vddSupplyVoltageSetPoint'])+'V, min V_IN='+str(is_parameters['inputVoltageMinimum'])+'V, max V_IN='+str(is_parameters['inputVoltageMaximum'])+'V')
	smu_vdd.setComplianceCurrent(is_parameters['complianceCurrent'])	

	# === START ===
	# Apply V_DD to the inverter
	print('Ramping supply voltage (VDD).')
	smu_vdd.rampDrainVoltageTo(is_parameters['vddSupplyVoltageSetPoint'])
	
	# Switch Sweep SMU into voltage-measurement mode
	smu_sweep.setChannel1SourceMode(mode='current')
	smu_sweep.setId(0)
	
	print('Beginning to sweep input voltage.')
	gateSweepResults = gateSweepScript.run(gateSweepParameters, {'SMU':smu_sweep}, arduino_systems, share=share)
	
	print('Ramping down supply voltage (VDD).')
	smu_vdd.rampDownVoltages()
	# === COMPLETE ===

	# Translate data format from gate sweep to inverter sweep
	results = convertToInverterFormat(gateSweepResults)

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
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), is_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))

	return jsonData

# === Data Format ===
def convertToInverterFormat(gateSweepResults):
	vin_data = gateSweepResults['Results']['vgs_data']
	iin_data = gateSweepResults['Results']['ig_data']
	vout_data = gateSweepResults['Results']['vds_data']
	iout_data = gateSweepResults['Results']['id_data']
	timestamps = gateSweepResults['Results']['timestamps']
	inputVoltages = gateSweepResults['Results']['gateVoltages']
	
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
			'iin_max':  np.max(np.abs(iin_data)),
			'iin_min':  np.min(np.abs(iin_data)),
			'iout_max': np.max(np.abs(iout_data)),
			'iout_min': np.min(np.abs(iout_data)),
		}
	}


	