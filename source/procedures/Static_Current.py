# === Imports ===
import time
import numpy as np

import pipes
from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]
	
	# This script uses the default Ardunio, which is the first one in the list of Ardunio systems
	arduino_names = list(arduino_systems.keys())
	arduino_instance = arduino_systems[arduino_names[0]]
	
	# Get shorthand name to easily refer to configuration parameters
	sc_parameters = parameters['runConfigs']['StaticCurrent']

	# Print the starting message
	print('Applying static current of I_G='+str(sc_parameters['gateCurrentSetPoint'])+' A, I_D='+str(sc_parameters['drainCurrentSetPoint'])+' A for '+str(sc_parameters['totalBiasTime'])+' seconds...')
	smu_instance.setComplianceVoltage(sc_parameters['complianceVoltage'])	

	# Ensure all sensor data is reset to empty lists so that there is one-to-one mapping between device and sensor measurements
	sensor_data = arduino_instance.takeMeasurement()
	for (measurement, value) in sensor_data.items():
		parameters['SensorData'][measurement] = []

	# === START ===
	# Change SMU into current-source mode
	smu_instance.setChannel1SourceMode(mode='current')
	smu_instance.setChannel2SourceMode(mode='current')
	
	# Apply voltages
	print('Applying bias currents.')
	smu_instance.rampDrainCurrentTo(sc_parameters['drainCurrentSetPoint'])
	smu_instance.rampGateCurrentTo(sc_parameters['gateCurrentSetPoint'])

	# Delay before measurements begin (only useful for allowing current to settle a little, not usually necessary)
	if(sc_parameters['delayBeforeMeasurementsBegin'] > 0):
		print('Waiting for: ' + str(sc_parameters['delayBeforeMeasurementsBegin']) + ' seconds before measurements begin.')
		time.sleep(sc_parameters['delayBeforeMeasurementsBegin'])

	results = runStaticCurrent(smu_instance, 
							arduino_instance,
							drainCurrentSetPoint=sc_parameters['drainCurrentSetPoint'],
							gateCurrentSetPoint=sc_parameters['gateCurrentSetPoint'],
							totalBiasTime=sc_parameters['totalBiasTime'], 
							measurementTime=sc_parameters['measurementTime'])
	smu_instance.rampGateCurrentTo(sc_parameters['gateCurrentWhenDone'])
	smu_instance.rampDrainCurrentTo(sc_parameters['drainCurrentWhenDone'])

	# Float channels if desired
	if(sc_parameters['floatChannelsWhenDone']):
		print('Turning channels off.')
		smu_instance.turnChannelsOff()

	# Delay to allow channels to float or sit at their "WhenDone" values
	if(sc_parameters['delayWhenDone'] > 0):
		print('Waiting for: ' + str(sc_parameters['delayWhenDone']) + ' seconds...')
		time.sleep(sc_parameters['delayWhenDone'])
	
	# If the channels were turned off, need to turn them back on
	if(sc_parameters['floatChannelsWhenDone']):
		smu_instance.turnChannelsOn()
		print('Channels are back on.')
	
	# Change SMU back into default voltage-source mode
	smu_instance.setChannel1SourceMode(mode='voltage')
	smu_instance.setChannel2SourceMode(mode='voltage')
	# === COMPLETE ===

	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']
	
	# Print the metrics
	print('Max voltage: {:.4f}'.format(results['Computed']['vds_max']))
	print('Min voltage: {:.4f}'.format(results['Computed']['vds_min']))
	print('Average noise: {:.4f}'.format(results['Computed']['avg_vds_std']))

	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
	
	# Save results as a JSON object
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), sc_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))
	
	return jsonData

# === Data Collection ===
def runStaticCurrent(smu_instance, arduino_instance, drainCurrentSetPoint, gateCurrentSetPoint, totalBiasTime, measurementTime, share=None):
	vds_data = []
	id_data = []
	vgs_data = []
	ig_data = []
	timestamps = []
	vds_std = []
	id_std = []
	vgs_std = []
	ig_std = []

	# Set the SMU timeout to be a few measurementTime's long
	#timeout = max(1000, 3*measurementTime*1000)
	timeout = 60000
	smu_instance.setTimeout(timeout_ms=timeout)
	print('SMU timeout set to ' + str(timeout) + ' ms.')

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
		timestamp = time.time()
		measurement = smu_instance.takeMeasurement()
		measurements['Vds_data'].append(measurement['V_ds'])
		measurements['Id_data'].append(measurement['I_d'])
		measurements['Vgs_data'].append(measurement['V_gs'])
		measurements['Ig_data'].append(measurement['I_g'])
		measurementCount += 1
		
		# While the current measurementTime has not been exceeded, continuously collect data. (subtract half of the SMU's speed so on average we take the right amount of time)
		while (time.time() - startTime) < (measurementTime*(i+1) - (1/2)*(time.time() - startTime)/measurementCount):
			timestamp = time.time()
			measurement = smu_instance.takeMeasurement()
			measurements['Vds_data'].append(measurement['V_ds'])
			measurements['Id_data'].append(measurement['I_d'])
			measurements['Vgs_data'].append(measurement['V_gs'])
			measurements['Ig_data'].append(measurement['I_g'])
			measurementCount += 1
			# Sleep for a fraction of the SMU's speed so we put a slight delay between consecutive queries
			time.sleep((1/2)*(time.time() - startTime)/measurementCount)
		
		# Save the median of all the measurements taken in this measurementTime window
		vds_data.append(np.median(measurements['Vds_data']))
		id_data.append(np.median(measurements['Id_data']))
		vgs_data.append(np.median(measurements['Vgs_data']))
		ig_data.append(np.median(measurements['Ig_data']))
		timestamps.append(timestamp)
		
		# If multiple data points were collected in this measurementTime, save their standard deviation
		vds_normalized = measurements['Vds_data']
		if(len(measurements['Vds_data']) >= 2):
			id_normalized = np.array(measurements['Vds_data']) - np.polyval(np.polyfit(range(len(measurements['Vds_data'])), measurements['Vds_data'], 1), np.array(measurements['Vds_data']))
		vgs_normalized = measurements['Vgs_data']	
		if(len(measurements['Vgs_data']) >= 2):
			ig_normalized = np.array(measurements['Vgs_data']) - np.polyval(np.polyfit(range(len(measurements['Vgs_data'])), measurements['Vgs_data'], 1), np.array(measurements['Vgs_data']))			
		vds_std.append(np.std(vds_normalized))
		vgs_std.append(np.std(vgs_normalized))

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
	print('Completed static current in "' + '{:.4f}'.format(endTime - startTime) + '" seconds.')

	return {
		'Raw':{
			'vds_data':vds_data,
			'id_data':id_data,
			'vgs_data':vgs_data,
			'ig_data':ig_data,
			'timestamps':timestamps,
			'vds_std':vds_std,
			'vgs_std':vgs_std
		},
		'Computed':{
			'vds_max':max(vds_data),
			'vds_min':min(vds_data),
			'avg_vds_std':np.mean(vds_std),
			'tau_settle':settlingTimeConstant(timestamps, vds_data)
		}
	}
	
def settlingTimeConstant(timestamps, data):
	d_start = data[0]
	d_mean = np.mean(data)
	d_settled = (d_start - d_mean)*np.exp(-1) + d_mean
	d_settled = -1
	if(len(data) > 2):
		for i in range(len(data) - 1):
			if(((data[i] <= d_settled) and (data[i+1] >= d_settled)) or ((data[i] >= d_settled) and (data[i+1] <= d_settled))):
				d_settled = i
				break
	return (timestamps[d_settled] - timestamps[0])
	


