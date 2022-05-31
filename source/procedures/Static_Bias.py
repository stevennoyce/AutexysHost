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
	arduino_instance = arduino_systems[list(arduino_systems.keys())[0]]
	
	# Get shorthand name to easily refer to configuration parameters
	sb_parameters = parameters['runConfigs']['StaticBias']

	# Print the starting message
	print('Applying static bias of V_GS='+str(sb_parameters['gateVoltageSetPoint'])+'V, V_DS='+str(sb_parameters['drainVoltageSetPoint'])+'V for '+str(sb_parameters['totalBiasTime'])+' seconds...')
	smu_instance.setComplianceCurrent(sb_parameters['complianceCurrent'])	

	# === START ===
	# Apply bias voltages (or change channels to high-resistance mode)
	print('Applying bias voltages.')
	if(sb_parameters['supplyDrainVoltage']):
		smu_instance.rampDrainVoltageTo(sb_parameters['drainVoltageSetPoint'])
		print('Applied drain voltage.')
	else:
		smu_instance.setChannel1SourceMode(mode='current')
		smu_instance.setId(0)
	
	if(sb_parameters['supplyGateVoltage']):
		smu_instance.rampGateVoltageTo(sb_parameters['gateVoltageSetPoint'])
		print('Applied gate voltage.')
	else:
		smu_instance.setChannel2SourceMode(mode='current')
		smu_instance.setIg(0)

	# Delay before measurements begin (only useful for allowing current to settle a little, not usually necessary)
	if(sb_parameters['delayBeforeMeasurementsBegin'] > 0):
		print('Waiting for: ' + str(sb_parameters['delayBeforeMeasurementsBegin']) + ' seconds before measurements begin.')
		time.sleep(sb_parameters['delayBeforeMeasurementsBegin'])

	results = runStaticBias(smu_instance, 
							arduino_instance,
							totalBiasTime=sb_parameters['totalBiasTime'], 
							measurementTime=sb_parameters['measurementTime'],
							share=share)
	
	# Ramp bias voltages to their "when done" values (or exit high-resistance mode if it was previously enabled)
	if(sb_parameters['supplyGateVoltage']):
		smu_instance.rampGateVoltageTo(sb_parameters['gateVoltageWhenDone'])
	else:
		smu_instance.setChannel2SourceMode(mode='voltage')
		smu_instance.rampGateVoltageDown()
		
	if(sb_parameters['supplyDrainVoltage']):
		smu_instance.rampDrainVoltageTo(sb_parameters['drainVoltageWhenDone'])
	else:
		smu_instance.setChannel1SourceMode(mode='voltage')
		smu_instance.rampDrainVoltageDown()

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
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), sb_parameters['saveFileName'], jsonData, subDirectory=parameters['experimentSubFolder']+str(parameters['startIndexes']['experimentNumber']))
	
	# Save a 2nd data file under a different name if one or more of the channels was in high-resistance mode
	if((not sb_parameters['supplyGateVoltage']) or (not sb_parameters['supplyDrainVoltage'])):
		dlu.saveJSON(dlu.getDeviceDirectory(parameters), sb_parameters['secondaryFileName'], jsonData, subDirectory=parameters['experimentSubFolder']+str(parameters['startIndexes']['experimentNumber']))
	
	return jsonData

# === Data Collection ===
def runStaticBias(smu_instance, arduino_instance, totalBiasTime, measurementTime, share=None):
	vds_data = []
	id_data = []
	vgs_data = []
	ig_data = []
	timestamps = []
	vds_std = []
	id_std = []
	vgs_std = []
	ig_std = []
	arduino_data = []

	# Get the SMU measurement speed
	smu_measurementsPerSecond = smu_instance.measurementsPerSecond
	smu_secondsPerMeasurement = 1/smu_measurementsPerSecond

	# Compute the number of data points we will be collecting (unless measurementTime is unreasonably small)
	steps = max(int(totalBiasTime/measurementTime), 1) if(measurementTime > 0) else int(totalBiasTime/smu_secondsPerMeasurement)
	
	# Take a timestamp for the start of the StaticBias
	startTime = time.time()

	# Criteria to keep taking measurements when measurementTime is relatively large
	continueCriterion = lambda i, measurementCount: i < steps
	smallMeasurementTimeCriterion = lambda : measurementTime < smu_instance.measurementRateVariabilityFactor*smu_secondsPerMeasurement
	if(smallMeasurementTimeCriterion):
		# Criteria to keep taking measurements when measurementTime is very small
		continueCriterion = lambda i, measurementCount: (time.time() - startTime) < (totalBiasTime - (1/2)*smu_secondsPerMeasurement)
		continueCriterion = lambda i, measurementCount: (time.time() - startTime) < (totalBiasTime - (1/2)*(time.time() - startTime)/max(measurementCount, 1))

	i = 0
	measurementCount = 0
	while(continueCriterion(i, measurementCount)):
		# Send a progress message
		if(smallMeasurementTimeCriterion):
			pipes.progressUpdate(share, 'Static Bias Point', start=0, current=i+1, end=steps)
		else:
			pipes.progressUpdate(share, 'Static Bias Point', start=0, current=i+1, end=steps)

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
		vds_data_median = np.median(measurements['Vds_data'])
		id_data_median = np.median(measurements['Id_data'])
		vgs_data_median = np.median(measurements['Vgs_data'])
		ig_data_median = np.median(measurements['Ig_data'])
		vds_data.append(vds_data_median)
		id_data.append(id_data_median)
		vgs_data.append(vgs_data_median)
		ig_data.append(ig_data_median)
		timestamps.append(timestamp)
		arduino_data.append(arduino_instance.takeMeasurement())

		# If multiple data points were collected in this measurementTime, save their standard deviation
		id_normalized = measurements['Id_data']
		if(len(measurements['Id_data']) >= 2):
			id_normalized = np.array(measurements['Id_data']) - np.polyval(np.polyfit(range(len(measurements['Id_data'])), measurements['Id_data'], 1), np.array(measurements['Id_data']))
		ig_normalized = measurements['Ig_data']	
		if(len(measurements['Ig_data']) >= 2):
			ig_normalized = np.array(measurements['Ig_data']) - np.polyval(np.polyfit(range(len(measurements['Ig_data'])), measurements['Ig_data'], 1), np.array(measurements['Ig_data']))			
		id_std.append(np.std(id_normalized))
		ig_std.append(np.std(ig_normalized))

		# Send a data message
		pipes.livePlotUpdate(share,plots=
		[livePlotter.createLiveDataPoint(plotID='Response vs. Time',
										labels=['Drain Current', 'Gate Current'],
										xValues=[timestamp, timestamp], 
										yValues=[id_data_median, ig_data_median], 
										xAxisTitle='Time (s)', 
										yAxisTitle='Current (A)', 
										yscale='linear', 
										plotMode='lines',
										enumerateLegend=False,
										timeseries=True),
		])
		
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
			'ig_std':ig_std,
			'arduino_data':arduino_data,
		},
		'Computed':{
			'id_max':max(id_data),
			'id_min':min(id_data),
			'avg_id_std':np.mean(id_std),
			'tau_settle':settlingTimeConstant(timestamps, id_data)
		}
	}
	
def settlingTimeConstant(timestamps, id_data):
	id_start = id_data[0]
	id_mean = np.mean(id_data)
	id_settled = (id_start - id_mean)*np.exp(-1) + id_mean
	i_settled = -1
	if(len(id_data) > 2):
		for i in range(len(id_data) - 1):
			if(((id_data[i] <= id_settled) and (id_data[i+1] >= id_settled)) or ((id_data[i] >= id_settled) and (id_data[i+1] <= id_settled))):
				i_settled = i
				break
	return (timestamps[i_settled] - timestamps[0])
