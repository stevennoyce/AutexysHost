# === Imports ===
import time
import numpy as np

import pipes
#from procedures import Device_History as deviceHistoryScript
from Live_Plot_Data_Point import Live_Plot_Data_Point
from Live_Plot_Series_Data_Point import Live_Plot_Series_Data_Point
from utilities import DataLoggerUtility as dlu
from utilities import SequenceGeneratorUtility as dgu


# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]
	
	# Get shorthand name to easily refer to configuration parameters
	rt_params = parameters['runConfigs']['NoiseCollection']
	
	smu_instance.setBinaryDataTransfer(True)
	smu_instance.setComplianceCurrent(rt_params['complianceCurrent'])
	
	# === START ===
	# Apply voltages
	print('Ramping Voltages')
	smu_instance.rampDrainVoltageTo(rt_params['drainVoltage'])
	smu_instance.rampGateVoltageTo(rt_params['gateVoltage'])
	
	print('Starting Noise Collection.')
	results = runNoiseCollection(smu_instance, 
								measurementSpeed=rt_params['measurementSpeed'],
								drainVoltage=rt_params['drainVoltage'],
								gateVoltage=rt_params['gateVoltage'], 
								points=rt_params['points'],
								share=share)
	smu_instance.rampDownVoltages()
	# === COMPLETE ===
	
	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']
	
	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
	
	# Save results as a JSON object
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), rt_params['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))
	
	return jsonData

# === Data Collection ===
def runNoiseCollection(smu_instance, measurementSpeed, drainVoltage, gateVoltage, points, share=None):
	triggerInterval = 1/measurementSpeed
	points = min(points, 100e3)
	startTime = time.time()

	pipes.progressUpdate(share, 'Noise Collection', start=0, current=0, end=1)
	measurements = smu_instance.takeSweep(drainVoltage, drainVoltage, gateVoltage, gateVoltage, points, triggerInterval=triggerInterval, includeVoltages=False)
	pipes.progressUpdate(share, 'Noise Collection', start=0, current=1, end=1)

	print('Time elapsed is {} s'.format(time.time() - startTime))

	return {
		'Raw':{
			'id_data': measurements['Id_data'],
			'ig_data': measurements['Ig_data'],
			'timestamps': [t + startTime for t in measurements['timestamps']]
		},
		'Computed':{
			
		}
	}


	