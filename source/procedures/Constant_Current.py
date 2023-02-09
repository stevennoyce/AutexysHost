# === Imports ===
import time
import numpy as np

import pipes
import Live_Plot_Data_Point as livePlotter
from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]
	
	# Get shorthand name to easily refer to configuration parameters
	cc_parameters = parameters['runConfigs']['ConstantCurrent']
	
	# Print the starting message
	print('Constant Current is starting.')
	
	# === START ===
	smu_instance.setChannel1SourceMode(mode='current')
	smu_instance.setChannel2SourceMode(mode='voltage')
	smu_instance.setParameter(":sense1:volt:prot {}".format(cc_parameters['complianceVoltage']))
	smu_instance.setParameter(":sense2:curr:prot {}".format(100e-6))
	
	results = runConstantCurrent(smu_instance,
								 currentApplied=cc_parameters['currentApplied'],
								 currentDuration=cc_parameters['currentDuration'],
								 currentDataInterval=cc_parameters['currentDataInterval'],
								 enableSweep=cc_parameters['enableSweep'],
								 sweepStart=cc_parameters['sweepStart'],
								 sweepEnd=cc_parameters['sweepEnd'],
								 sweepSteps=cc_parameters['sweepSteps'],
								 sweepDelayBetweenMeasurements=cc_parameters['sweepDelayBetweenMeasurements'],
								 sweepFrequency=cc_parameters['sweepFrequency'])
	# === COMPLETE ===
	
	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
	
	# Save results as a JSON object
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), cc_parameters['saveFileName'], jsonData, subDirectory=parameters['experimentSubFolder']+str(parameters['startIndexes']['experimentNumber']))
	
	return jsonData

def runConstantCurrent(smu_instance, currentApplied, currentDuration, currentDataInterval, enableSweep, sweepStart, sweepEnd, sweepSteps, sweepDelayBetweenMeasurements, sweepFrequency):
	voltage_data = []
	current_data = []
	timestamps = []
	sweep_voltage_data = []
	sweep_current_data = []
	sweep_timestamps = []
	sweep_number = []
	
	# TODO - fill in details of when to apply channels and taking measurements
	
	return {
		'Raw': {
			'voltage_data':voltage_data,
			'current_data':current_data,
			'timestamps':timestamps,
			'sweep_voltage_data':sweep_voltage_data,
			'sweep_current_data':sweep_current_data,
			'sweep_timestamps':sweep_timestamps,
			'sweep_number':sweep_number,
		}
	}
	
	
	
	
	
	
	
	
	
	
	
	