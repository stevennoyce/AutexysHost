# === Imports ===
import time
import numpy as np

from procedures import Device_History as deviceHistoryScript
from utilities import DataLoggerUtility as dlu
from utilities import SequenceGeneratorUtility as dgu


# === Main ===
def run(parameters, smu_instance, isSavingResults=True, isPlottingResults=False):
	# Get shorthand name to easily refer to configuration parameters
	rt_params = parameters['runConfigs']['NoiseCollection']
	
	# Print the starting message
	print('Starting Noise Collection')
	smu_instance.setComplianceCurrent(rt_params['complianceCurrent'])	
	
	# === START ===
	print('Ramping drain voltage.')
	smu_instance.rampDrainVoltageTo(rt_params['drainVoltage'])
	smu_instance.rampGateVoltageTo(rt_params['gateVoltage'])
	
	results = runNoiseCollection(smu_instance, 
								measurementSpeed=rt_params['measurementSpeed'],
								drainVoltage=rt_params['drainVoltage'],
								gateVoltage=rt_params['gateVoltage'], 
								points=rt_params['points'])
	
	smu_instance.rampDownVoltages()
	
	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']
	
	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
	
	# Save results as a JSON object
	if(isSavingResults):
		print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
		dlu.saveJSON(dlu.getDeviceDirectory(parameters), rt_params['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))
	
	return jsonData

# === Data Collection ===
def runNoiseCollection(smu_instance, measurementSpeed, drainVoltage, gateVoltage, points):
	triggerInterval = 1/measurementSpeed
	points = min(points, 100e3)
	
	measurements = smu_instance.takeSweep(drainVoltage, drainVoltage, gateVoltage, gateVoltage, points, triggerInterval=triggerInterval)
	
	return {
		'Raw':{
			'vds_data': measurements['Vds_data'],
			'id_data': measurements['Id_data'],
			'vgs_data':measurements['Vgs_data'],
			'ig_data': measurements['Ig_data'],
			'timestamps': measurements['timestamps']
		},
		'Computed':{
			
		}
	}


	