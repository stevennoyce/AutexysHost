# === Imports ===
import time
import numpy as np

import pipes
import Live_Plot_Data_Point as livePlotter
from utilities import DataLoggerUtility as dlu
from procedures import Static_Bias as staticBiasScript



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses two SMUs, one for applying the power supply and one for measuring VIN/VOUT
	smu_bias = smu_systems['logicSignalSMU']
	smu_vdd = smu_systems['powerSupplySMU']
	
	# Get shorthand name to easily refer to configuration parameters
	ib_parameters = parameters['runConfigs']['InverterBias']

	# Translate configuration parameters to perform the input voltage sweep as a gate sweep
	staticBiasParameters = dict(parameters)
	staticBiasParameters['runType'] = 'StaticBias'
	staticBiasParameters['runConfigs']['StaticBias']['gateVoltageSetPoint']          = ib_parameters['inputVoltageSetPoint']
	staticBiasParameters['runConfigs']['StaticBias']['drainVoltageSetPoint']         = 0
	staticBiasParameters['runConfigs']['StaticBias']['totalBiasTime']                = ib_parameters['totalBiasTime']
	staticBiasParameters['runConfigs']['StaticBias']['measurementTime']              = ib_parameters['measurementTime']
	staticBiasParameters['runConfigs']['StaticBias']['complianceCurrent']            = ib_parameters['complianceCurrent']
	staticBiasParameters['runConfigs']['StaticBias']['delayBeforeMeasurementsBegin'] = ib_parameters['delayBeforeMeasurementsBegin']
	staticBiasParameters['runConfigs']['StaticBias']['gateVoltageWhenDone']          = 0
	staticBiasParameters['runConfigs']['StaticBias']['drainVoltageWhenDone']         = 0
	staticBiasParameters['runConfigs']['StaticBias']['floatChannelsWhenDone']        = False
	staticBiasParameters['runConfigs']['StaticBias']['delayWhenDone']                = 0
	staticBiasParameters['runConfigs']['StaticBias']['supplyGateVoltage']            = True
	staticBiasParameters['runConfigs']['StaticBias']['supplyDrainVoltage']           = False

	# Print the starting message
	print('Biasing the inverter: V_DD='+str(ib_parameters['vddSupplyVoltageSetPoint'])+'V, V_IN='+str(ib_parameters['inputVoltageSetPoint'])+'V')
	smu_vdd.setComplianceCurrent(ib_parameters['complianceCurrent'])	

	# === START ===
	# Apply V_DD to the inverter
	print('Ramping supply voltage (VDD).')
	smu_vdd.rampDrainVoltageTo(ib_parameters['vddSupplyVoltageSetPoint'])
	
	print('Beginning to bias inverter.')
	staticBiasResults = staticBiasScript.run(staticBiasParameters, {'SMU':smu_bias}, arduino_systems, share=share)
	
	print('Ramping down supply voltage (VDD).')
	smu_vdd.rampDownVoltages()
	# === COMPLETE ===

	return staticBiasResults

	# === Optional: Save in Inverter Format ===

	# Translate data format from gate sweep to inverter sweep
	results = convertToInverterFormat(staticBiasResults)

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
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), ib_parameters['saveFileName'], jsonData, subDirectory=parameters['experimentSubFolder']+str(parameters['startIndexes']['experimentNumber']))

	return jsonData

# === Data Format ===
def convertToInverterFormat(originalResults):
	vin_data = originalResults['Results']['vgs_data']
	iin_data = originalResults['Results']['ig_data']
	vout_data = originalResults['Results']['vds_data']
	iout_data = originalResults['Results']['id_data']
	timestamps = originalResults['Results']['timestamps']
	inputVoltages = originalResults['Results']['gateVoltages']
	
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


	