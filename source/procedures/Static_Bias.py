# === Imports ===
import time
import numpy as np

from procedures import Device_History as deviceHistoryScript
from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_instance, arduino_instance, isSavingResults=True, isPlottingResults=False):
	# Create distinct parameters for plotting the results
	dh_parameters = {}
	dh_parameters['Identifiers'] = dict(parameters['Identifiers'])
	dh_parameters['dataFolder'] = parameters['dataFolder']
	dh_parameters['plotGateSweeps'] = False
	dh_parameters['plotBurnOuts'] = False
	dh_parameters['plotStaticBias'] = True
	dh_parameters['showFiguresGenerated'] = True
	dh_parameters['saveFiguresGenerated'] = True
	dh_parameters['excludeDataBeforeJSONExperimentNumber'] = parameters['startIndexes']['experimentNumber']
	dh_parameters['excludeDataAfterJSONExperimentNumber'] =  parameters['startIndexes']['experimentNumber']

	# Get shorthand name to easily refer to configuration parameters
	sb_parameters = parameters['runConfigs']['StaticBias']

	# Print the starting message
	print('Applying static bias of V_GS='+str(sb_parameters['gateVoltageSetPoint'])+'V, V_DS='+str(sb_parameters['drainVoltageSetPoint'])+'V for '+str(sb_parameters['totalBiasTime'])+' seconds...')
	smu_instance.setComplianceCurrent(sb_parameters['complianceCurrent'])	

	# Ensure all sensor data is reset to empty lists so that there is one-to-one mapping between device and sensor measurements
	sensor_data = arduino_instance.takeMeasurement()
	for (measurement, value) in sensor_data.items():
		parameters['SensorData'][measurement] = []

	# === START ===
	# Apply voltages
	print('Applying bias voltages.')
	smu_instance.rampDrainVoltageTo(sb_parameters['drainVoltageSetPoint'])
	smu_instance.rampGateVoltageTo(sb_parameters['gateVoltageSetPoint'])

	# Delay before measurements begin (only useful for allowing current to settle a little, not usually necessary)
	if(sb_parameters['delayBeforeMeasurementsBegin'] > 0):
		print('Waiting for: ' + str(sb_parameters['delayBeforeMeasurementsBegin']) + ' seconds before measurements begin.')
		time.sleep(sb_parameters['delayBeforeMeasurementsBegin'])

	results = runStaticBias(smu_instance, 
							arduino_instance,
							drainVoltageSetPoint=sb_parameters['drainVoltageSetPoint'],
							gateVoltageSetPoint=sb_parameters['gateVoltageSetPoint'],
							totalBiasTime=sb_parameters['totalBiasTime'], 
							measurementTime=sb_parameters['measurementTime'])
	smu_instance.rampGateVoltageTo(sb_parameters['gateVoltageWhenDone'])
	smu_instance.rampDrainVoltageTo(sb_parameters['drainVoltageWhenDone'])

	# Float channels if desired
	if(sb_parameters['floatChannelsWhenDone']):
		print('Turning channels off.')
		smu_instance.turnChannelsOff()

	# Delay to allow channels to float or sit at their "WhenDone" values
	if(sb_parameters['delayWhenDone'] > 0):
		print('Waiting for: ' + str(sb_parameters['delayWhenDone']) + ' seconds...')
		time.sleep(sb_parameters['delayWhenDone'])
	
	# If the channels were turned off, need to turn them back on
	if(sb_parameters['floatChannelsWhenDone']):
		smu_instance.turnChannelsOn()
		print('Channels are back on.')
	# === COMPLETE ===

	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']
	
	# Print the metrics
	print('Max current: {:.4f}'.format(results['Computed']['id_max']))
	print('Min current: {:.4f}'.format(results['Computed']['id_min']))
	print('Average noise: {:.4f}'.format(results['Computed']['avg_id_std']))

	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
	
	# Save results as a JSON object
	if(isSavingResults):
		print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
		dlu.saveJSON(dlu.getDeviceDirectory(parameters), sb_parameters['saveFileName'], jsonData)
	
	# Show plots to the user if desired
	if(isPlottingResults):
		deviceHistoryScript.run(dh_parameters)
	
	return jsonData

# === Data Collection ===
def runStaticBias(smu_instance, arduino_instance, drainVoltageSetPoint, gateVoltageSetPoint, totalBiasTime, measurementTime):
	vds_data = []
	id_data = []
	vgs_data = []
	ig_data = []
	timestamps = []
	vds_std = []
	id_std = []
	vgs_std = []
	ig_std = []

	# Get the SMU measurement speed
	smu_measurementsPerSecond = smu_instance.measurementsPerSecond
	smu_secondsPerMeasurement = 1/smu_measurementsPerSecond

	# Compute the number of data points we will be collecting (unless measurementTime is unreasonably small)
	steps = max(int(totalBiasTime/measurementTime), 1) if(measurementTime > 0) else None
	
	# Take a timestamp for the start of the StaticBias
	startTime = time.time()

	# Criteria to keep taking measurements when measurementTime is relatively large
	continueCriterion = lambda i, measurementCount: i < steps
	if(measurementTime < smu_instance.measurementRateVariabilityFactor*smu_secondsPerMeasurement):
		# Criteria to keep taking measurements when measurementTime is very small
		continueCriterion = lambda i, measurementCount: (time.time() - startTime) < (totalBiasTime - (1/2)*smu_secondsPerMeasurement)
		continueCriterion = lambda i, measurementCount: (time.time() - startTime) < (totalBiasTime - (1/2)*(time.time() - startTime)/max(measurementCount, 1))

	i = 0
	measurementCount = 0
	while(continueCriterion(i, measurementCount)):
		# Define buffers for data to fill during each "measurementTime"
		measurements = {'Vds_data':[], 'Id_data':[], 'Vgs_data':[], 'Ig_data':[]}
		
		# Take the first data point of this "measurementTime"
		measurement = smu_instance.takeMeasurement()
		measurements['Vds_data'].append(measurement['V_ds'])
		measurements['Id_data'].append(measurement['I_d'])
		measurements['Vgs_data'].append(measurement['V_gs'])
		measurements['Ig_data'].append(measurement['I_g'])
		measurementCount += 1

		# While the current measurementTime has not been exceeded, continuously collect data. (subtract half of the SMU's speed so on average we take the right amount of time)
		while (time.time() - startTime) < (measurementTime*(i+1) - (1/2)*(time.time() - startTime)/measurementCount):
			measurement = smu_instance.takeMeasurement()
			measurements['Vds_data'].append(measurement['V_ds'])
			measurements['Id_data'].append(measurement['I_d'])
			measurements['Vgs_data'].append(measurement['V_gs'])
			measurements['Ig_data'].append(measurement['I_g'])
			measurementCount += 1
		
		# Save the median of all the measurements taken in this measurementTime window
		timestamp = time.time()
		vds_data.append(np.median(measurements['Vds_data']))
		id_data.append(np.median(measurements['Id_data']))
		vgs_data.append(np.median(measurements['Vgs_data']))
		ig_data.append(np.median(measurements['Ig_data']))
		timestamps.append(timestamp)
		
		# If multiple data points were collected in this measurementTime, save their standard deviation
		id_normalized = measurements['Id_data']
		if(len(measurements['Id_data']) >= 2):
			id_normalized = np.array(measurements['Id_data']) - np.polyval(np.polyfit(range(len(measurements['Id_data'])), measurements['Id_data'], 1), np.array(measurements['Id_data']))
		ig_normalized = measurements['Ig_data']	
		if(len(measurements['Ig_data']) >= 2):
			ig_normalized = np.array(measurements['Ig_data']) - np.polyval(np.polyfit(range(len(measurements['Ig_data'])), measurements['Ig_data'], 1), np.array(measurements['Ig_data']))			
		id_std.append(np.std(id_normalized))
		ig_std.append(np.std(ig_normalized))

		# Take a measurement with the Arduino
		sensor_data = arduino_instance.takeMeasurement()
		for (measurement, value) in sensor_data.items():
			parameters['SensorData'][measurement].append(value)

		# Update progress bar
		elapsedTime = time.time() - startTime
		print('\r[' + int(elapsedTime*70.0/totalBiasTime)*'=' + (70-int(elapsedTime*70.0/totalBiasTime)-1)*' ' + ']', end='')
		i += 1
	
	endTime = time.time()
	print('')
	print('Completed static bias in "' + '{:.4f}'.format(endTime - startTime) + '" seconds.')

	return {
		'Raw':{
			'vds_data':vds_data,
			'id_data':id_data,
			'vgs_data':vgs_data,
			'ig_data':ig_data,
			'timestamps':timestamps,
			'id_std':id_std,
			'ig_std':ig_std
		},
		'Computed':{
			'id_max':max(id_data),
			'id_min':min(id_data),
			'avg_id_std':np.mean(id_std)
		}
	}


