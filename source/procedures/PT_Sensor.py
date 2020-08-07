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
	results = runPTSensor( arduino_reference,
							totalSensingTime=pt_parameters['totalSensingTime'],
							delayBetweenMeasurements=pt_parameters['delayBetweenMeasurements'],
							share=share)
	
	# === COMPLETE ===

	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']

	# Print the metrics
	print('Max Impedance: {:.4f}'.format(results['Computed']['maxImpedance']))
	print('Max Impedance Time: {:.4e}'.format(results['Computed']['maxImpedanceTime']))

	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']

	# Save results as a JSON object
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), pt_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))

	return jsonData

# === Data Collection ===
def runPTSensor(arduino_reference, totalSensingTime, delayBetweenMeasurements, share=None):
	impedance_data = []
	timestamps     = []
	
	index = 0
	startTime = time.time()
	
	while((time.time() - startTime) < totalSensingTime):
		# Send a progress message
		pipes.progressUpdate(share, 'Impedance Point', start=0, current=index, end=int(index * totalSensingTime / (time.time() - startTime)), enableAbort=True)
		index += 1

		# If delayBetweenMeasurements is non-zero, wait before taking the measurement
		if(delayBetweenMeasurements > 0):
			time.sleep(delayBetweenMeasurements)

		# Take Measurement and timestamp it
		measurement = arduino_reference.takeMeasurement()
		timestamp = time.time()
		
		# Ensure measurement is in array format
		measurement_points = []
		if(isinstance(measurement['impedance'], list)):
			measurement_points = measurement['impedance']
		else:
			measurement_points = [measurement['impedance']]

		# Save measurement
		impedance_data.append(measurement_points)
		timestamps.append(timestamp)

		# Send a data message (for each point the the 'impedance' array)
		for i, value in enumerate(measurement_points):
			pipes.livePlotUpdate(share, plots=
			[livePlotter.createLiveDataPoint(plotID='Impedance', 
											labels=['Impedance ' + str(i+1)],
											xValues=[timestamp], 
											yValues=[value], 
											xAxisTitle='Time (s)', 
											yAxisTitle='Impedance (Ohms)', 
											yscale='linear', 
											plotMode='lines',
											enumerateLegend=False,
											timeseries=True),
			])
			
	return {
		'Raw':{
			'impedance_data':impedance_data,
			'timestamps':timestamps,
		},
		'Computed':{
			'maxImpedance': extractMaximum(impedance_data),
			'maxImpedanceTime': 0,
		}
	}


def extractMaximum(values):
	absValues = abs(np.array(values))
	return np.percentile(absValues, 99)


	