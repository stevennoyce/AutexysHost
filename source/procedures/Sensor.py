# === Imports ===
import time
import numpy as np

import pipes
import Live_Plot_Data_Point as livePlotter
from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses the default Arduino, which is the first one in the list of SMU systems
	arduino_names = list(arduino_systems.keys())
	arduino_reference = arduino_systems[arduino_names[0]]

	# Get shorthand name to easily refer to configuration parameters
	pt_parameters = parameters['runConfigs']['PTSensor']

	# Print the starting message
	print('Measuring prothrombin time sensor, with parameters: ' + str(pt_parameters))

	# === START ===	

	print('Starting prothrombin time measurements.')
	results = runSensor( arduino_reference,
							total_duration=pt_parameters['totalSensingTime'],
							delay_between_measurements=pt_parameters['delayBetweenMeasurements'],
							share=share)
	
	# === COMPLETE ===

	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']

	# Print the metrics
	for metric, value in results['Computed'].items():
		print(f"'{metric}': {value}")

	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']

	# Save results as a JSON object
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), pt_parameters['saveFileName'], jsonData, subDirectory=parameters['experimentSubFolder']+str(parameters['startIndexes']['experimentNumber']))

	return jsonData

# === Data Collection ===
def runSensor(arduino_reference, total_duration, delay_between_measurements, share=None):
	data = {}
	timestamps  = []
	start_time = time.time()
	
	while(time.time() < start_time + total_duration):
		# Send a progress message
		index = len(timestamps)
		pipes.progressUpdate(share, 'Sensor Data', start=0, current=index, end=int(index * total_duration / (time.time() - start_time)), enableAbort=True)

		if(delay_between_measurements > 0):
			time.sleep(delay_between_measurements)

		# Take Measurement and timestamp it
		measurement = arduino_reference.takeMeasurement()
		timestamp = time.time()
		
		for key, value in measurement.items():
			if(key not in data): 
				data[key] = []
			data[key].append(value)
		timestamps.append(timestamp)

		# Send a data message
		for key, value in measurement.items():
			points = [value] if(not isinstance(value, list)) else value
			
			pipes.livePlotUpdate(share, plots=
			[livePlotter.createLiveDataPoint(plotID=key, 
											labels=[f"{key}{i+1 if(len(points) > 1) else ''}" for i in range(len(points))],
											xValues=[timestamp]*len(points), 
											yValues=points, 
											xAxisTitle='Time (s)', 
											yAxisTitle='Sensor', 
											yscale='linear', 
											plotMode='lines',
											enumerateLegend=False,
											timeseries=True),
			])
			
	return {
		'Raw': {'timestamps':timestamps, **data},
		'Computed':{}
	}


	