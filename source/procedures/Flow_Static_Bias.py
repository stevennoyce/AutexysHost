# === Imports ===
import time
import numpy as np

import pipes
from procedures import Device_History as deviceHistoryScript
from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_instance, arduino_instance, isSavingResults=True, isPlottingResults=False, communication_pipe=None):
	# Create distinct parameters for plotting the results
	dh_parameters = {}
	dh_parameters['Identifiers'] = dict(parameters['Identifiers'])
	dh_parameters['dataFolder'] = parameters['dataFolder']
	dh_parameters['plotGateSweeps'] = False
	dh_parameters['plotBurnOuts'] = False
	dh_parameters['plotStaticBias'] = True
	dh_parameters['excludeDataBeforeJSONExperimentNumber'] = parameters['startIndexes']['experimentNumber']
	dh_parameters['excludeDataAfterJSONExperimentNumber'] =  parameters['startIndexes']['experimentNumber']

	# Get shorthand name to easily refer to configuration parameters
	
	
	fsb_parameters = parameters['runConfigs']['FlowStaticBias']

	# Print the starting message
	print('Applying flow static bias of V_GS='+str(fsb_parameters['gateVoltageSetPoint'])+'V, V_DS='+str(fsb_parameters['drainVoltageSetPoint'])+'V')
	smu_instance.setComplianceCurrent(fsb_parameters['complianceCurrent'])	

	# Ensure all sensor data is reset to empty lists so that there is one-to-one mapping between device and sensor measurements
	sensor_data = arduino_instance.takeMeasurement()
	for (measurement, value) in sensor_data.items():
		parameters['SensorData'][measurement] = []

	# === START ===
	# Apply voltages
	print('Applying bias voltages.')
	smu_instance.rampDrainVoltageTo(fsb_parameters['drainVoltageSetPoint'])
	smu_instance.rampGateVoltageTo(fsb_parameters['gateVoltageSetPoint'])

	'''
	# Delay before measurements begin (only useful for allowing current to settle a little, not usually necessary)
	if(fsb_parameters['delayBeforeMeasurementsBegin'] > 0):
		print('Waiting for: ' + str(fsb_parameters['delayBeforeMeasurementsBegin']) + ' seconds before measurements begin.')
		time.sleep(fsb_parameters['delayBeforeMeasurementsBegin'])
	'''

	results = runFlowStaticBias(smu_instance, 
							arduino_instance,
							delayBeforeMeasurementsBegin=fsb_parameters['delayBeforeMeasurementsBegin'],
							drainVoltageSetPoint=fsb_parameters['drainVoltageSetPoint'],
							gateVoltageSetPoint=fsb_parameters['gateVoltageSetPoint'],
							measurementTime=fsb_parameters['measurementTime'],
							flowDurations=fsb_parameters['flowDurations'], 
							subCycleDurations=fsb_parameters['subCycleDurations'],
							pumpPins=fsb_parameters['pumpPins'],
							airAndWaterPins=fsb_parameters['airAndWaterPins'],
							cycleCount=fsb_parameters['cycleCount'],
							solutions=fsb_parameters['solutions'])
	smu_instance.rampGateVoltageTo(fsb_parameters['gateVoltageWhenDone'])
	smu_instance.rampDrainVoltageTo(fsb_parameters['drainVoltageWhenDone'])

	# Float channels if desired
	if(fsb_parameters['floatChannelsWhenDone']):
		print('Turning channels off.')
		smu_instance.turnChannelsOff()

	# Delay to allow channels to float or sit at their "WhenDone" values
	if(fsb_parameters['delayWhenDone'] > 0):
		print('Waiting for: ' + str(fsb_parameters['delayWhenDone']) + ' seconds...')
		time.sleep(fsb_parameters['delayWhenDone'])
	
	# If the channels were turned off, need to turn them back on
	if(fsb_parameters['floatChannelsWhenDone']):
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
		dlu.saveJSON(dlu.getDeviceDirectory(parameters), fsb_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))
	
	# Show plots to the user if desired
	if(isPlottingResults):
		deviceHistoryScript.run(dh_parameters)
	
	return jsonData

# Turns ON "pin", turns every other pin OFF
# if pin == -1, turn off every pin
def turnOnlyPin(smu_instance, pumpPins, pin):
	pumpPins = range(1, 11) # do it for every pin in existence
	for i in pumpPins:
		if i != pin:
			smu_instance.digitalWrite(i, "LOW")
	smu_instance.digitalWrite(pin, "HIGH")

def flushAirAndWaterPins(smu_instance, airPin, waterPin, pumpPins):
	a = 1
	turnOnlyPin(smu_instance, pumpPins, airPin)
	time.sleep(4)
	turnOnlyPin(smu_instance, pumpPins, -1)
	time.sleep(1)
	turnOnlyPin(smu_instance, pumpPins, waterPin)
	time.sleep(2)
	turnOnlyPin(smu_instance, pumpPins, -1)
	time.sleep(1)
	turnOnlyPin(smu_instance, pumpPins, airPin)
	time.sleep(4)
	turnOnlyPin(smu_instance, pumpPins, -1)
	time.sleep(1)

# === Data Collection ===
def runFlowStaticBias(smu_instance, arduino_instance, delayBeforeMeasurementsBegin, drainVoltageSetPoint, gateVoltageSetPoint, measurementTime, flowDurations, subCycleDurations, pumpPins, airAndWaterPins, cycleCount, solutions, communication_pipe=None):
	
	smu_instance.digitalWrite(1, "LOW")
	
	vds_data = []
	id_data = []
	vgs_data = []
	ig_data = []
	pump_on_intervals = []
	pump_on_intervals_pin = []
	timestamps = []
	vds_std = []
	id_std = []
	vgs_std = []
	ig_std = []
	
	# casting stuff as ints from strings
	cycleCount = int(cycleCount)
	for a in range(0, len(flowDurations)):
		flowDurations[a] = int(flowDurations[a])
		pumpPins[a] = int(pumpPins[a])
		smu_instance.smu.write(":source:digital:external" + str(pumpPins[a]) + ":function DIO")
		smu_instance.smu.write(":source:digital:external" + str(pumpPins[a]) + ":polarity positive")
		subCycleDurations[a] = int(subCycleDurations[a])
	
	# define totalBiasTime
	totalBiasTime = 0
	for tt in subCycleDurations:
		totalBiasTime += int(tt) * int(cycleCount)
	totalBiasTime += delayBeforeMeasurementsBegin
	#totalBiasTime += 10*((len(subCycleDurations) * cycleCount) - 1) # each flush takes 10 seconds
	
	# Get the SMU measurement speed
	smu_measurementsPerSecond = smu_instance.measurementsPerSecond
	smu_secondsPerMeasurement = 1/smu_measurementsPerSecond

	# Compute the number of data points we will be collecting (unless measurementTime is unreasonably small)
	steps = max(int(totalBiasTime/measurementTime), 1) if(measurementTime > 0) else None
	
	# instantiate air and water pins
	airPin = airAndWaterPins[0]
	waterPin = airAndWaterPins[1]
	
	# offsetTime, to account for air and water flushing
	offsetTime = 0
	
	# pour in first fluid prior to measurementCount starting (and thus prior to measurements starting)
	print("Exchanging fluid for digitalPin: " + str(pumpPins[0]))
	turnOnlyPin(smu_instance, pumpPins, pumpPins[0])
	time.sleep(flowDurations[0])
	print("Stopping fluid exchange")
	turnOnlyPin(smu_instance, pumpPins, -1) # turn off everything else
	
	# Take a timestamp for the start of the FlowStaticBias
	startTime = time.time()

	# Criteria to keep taking measurements when measurementTime is relatively large
	continueCriterion = lambda i, measurementCount, startTime: i < steps
	if(measurementTime < smu_instance.measurementRateVariabilityFactor*smu_secondsPerMeasurement):
		# Criteria to keep taking measurements when measurementTime is very small
		continueCriterion = lambda i, measurementCount, startTime: (time.time() - startTime) < (totalBiasTime - (1/2)*smu_secondsPerMeasurement)
		continueCriterion = lambda i, measurementCount, startTime: (time.time() - startTime) < (totalBiasTime - (1/2)*(time.time() - startTime)/max(measurementCount, 1))
	
	# initialize pump_on_intervals array
	for cyc in range(0, len(pumpPins)):
		pump_on_intervals.append([])
	
	# define array of all possible times when fluid exchange should happen, given the number of cycles
	allPossibleExchangeTimesStart = []
	timeCounter = delayBeforeMeasurementsBegin
	for cyc in range(0, cycleCount):
		for cycDur in subCycleDurations:
			timeCounter += cycDur
			allPossibleExchangeTimesStart.append(timeCounter)	
	
	# define array of all possible times when fluid flow, upon initializing, should STOP flowing
	allPossibleExchangeTimesEnd = []
	timeCounter = 1 # offset due to initial flow prior to data collection
	for cyc in allPossibleExchangeTimesStart:
		allPossibleExchangeTimesEnd.append(cyc + flowDurations[(timeCounter) % len(flowDurations)])
		timeCounter += 1
	
	# define array of all possible times when flushing should occur
	allPossibleFlushTimes = []
	for cyc in allPossibleExchangeTimesStart:
		allPossibleFlushTimes.append(cyc - 10) # 10 seconds before start of each cycle, do flushing
			
	
	i = 0
	measurementCount = 0
	pinAlternatingCounter = 1 # at least two motors, first environment was start, so first time pin exchange happens would require digital pin at index 1
	
	currentPin = 1
	currentDigitalPin = pumpPins[0]
	exchangeStartBool = True
	exchangeEndBool = True
	exchangeFlush = True
	while(continueCriterion(i, measurementCount, startTime)):
		# Define buffers for data to fill during each "measurementTime"
		measurements = {'Vds_data':[], 'Id_data':[], 'Vgs_data':[], 'Ig_data':[], 
						'Vds_intervals':[], 'Id_intervals':[], 'Vgs_intervals':[], 'Ig_intervals':[]}
		
		# Take the first data point of this "measurementTime"
		measurement = smu_instance.takeMeasurement()
		measurements['Vds_data'].append(measurement['V_ds'])
		measurements['Id_data'].append(measurement['I_d'])
		measurements['Vgs_data'].append(measurement['V_gs'])
		measurements['Ig_data'].append(measurement['I_g'])
		measurementCount += 1
		
		# While the current measurementTime has not been exceeded, continuously collect data. (subtract half of the SMU's speed so on average we take the right amount of time)
		while (time.time() - startTime) < (measurementTime*(i+1) - (1/2)*(time.time() - startTime)/measurementCount):
			
			# need this to prevent multiple time additions to pump_on_intervals
			if currentPin == pinAlternatingCounter:
				exchangeStartBool = True
				exchangeEndBool = False
			
			# Check to see if it is time to start exchanging out fluids
			currentTimeNotRounded = time.time() - startTime
			roundCurrentTime = int(currentTimeNotRounded) # round to nearest integer due to slight time lag
			#roundCurrentTime = round(currentTimeNotRounded, 1)
			
			#print(roundCurrentTime, pinAlternatingCounter)
			
			pinToTurnOnIndex = pinAlternatingCounter % len(pumpPins)
			
			if roundCurrentTime in allPossibleExchangeTimesStart: # start exchanging fluids; pin will constantly be spammed ON but doesn't matter
				
				if exchangeFlush == True:
					print("Exchanging Air and Water Pins first")
					flushAirAndWaterStart = time.time()
					flushAirAndWaterPins(smu_instance, airPin, waterPin, pumpPins)
					print("DONE exchanging air and water pins")
					flushAirAndWaterEnd = time.time()
					offsetTime = flushAirAndWaterEnd - flushAirAndWaterStart
					startTime += offsetTime
					exchangeFlush = False
					
				turnOnlyPin(smu_instance, pumpPins, pumpPins[pinToTurnOnIndex])
				currentDigitalPin = pumpPins[pinToTurnOnIndex]
				if exchangeStartBool == True:
					
					
					print("Exchanging fluid for digitalPin: " + str(pumpPins[pinToTurnOnIndex]))
					#print("added start interval: " + str(currentTimeNotRounded))
					pump_on_intervals[pinToTurnOnIndex].append(currentTimeNotRounded)	
					exchangeStartBool = False
					exchangeEndBool = True
					currentPin += 1
				
			# Check to see if it is time to STOP exchanging out fluids. Turn off all pins when this condition holds true
			if roundCurrentTime in allPossibleExchangeTimesEnd:
				#pinToTurnOnIndex = (pinAlternatingCounter - 1) % len(pumpPins) # this doesn't actually matter, since the code stops ALL pins
				turnOnlyPin(smu_instance, pumpPins, -1)
				if exchangeEndBool == True:
					print("Stopping fluid flow") # + str(pumpPins[pinToTurnOnIndex]))
					#print("added end interval: " + str(currentTimeNotRounded))
					pump_on_intervals[pinToTurnOnIndex].append(currentTimeNotRounded)	
					exchangeEndBool = False
					pinAlternatingCounter += 1
					exchangeFlush = True
			
			measurement = smu_instance.takeMeasurement()
			measurements['Vds_data'].append(measurement['V_ds'])
			measurements['Id_data'].append(measurement['I_d'])
			measurements['Vgs_data'].append(measurement['V_gs'])
			measurements['Ig_data'].append(measurement['I_g'])
			
			measurementCount += 1
			# Sleep for a fraction of the SMU's speed so we put a slight delay between consecutive queries
			time.sleep((1/2)*(time.time() - startTime + offsetTime)/measurementCount)
		
		# Save the median of all the measurements taken in this measurementTime window
		timestamp = time.time()
		vds_data.append(np.median(measurements['Vds_data']))
		id_data.append(np.median(measurements['Id_data']))
		vgs_data.append(np.median(measurements['Vgs_data']))
		ig_data.append(np.median(measurements['Ig_data']))
		
		pump_on_intervals_pin.append(currentDigitalPin)

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
	
	print("Exchanging Air and Water Pins first") # final exchange
	flushAirAndWaterStart = time.time()
	flushAirAndWaterPins(smu_instance, airPin, waterPin, pumpPins)
	print("DONE exchanging air and water pins")
	flushAirAndWaterEnd = time.time()
	offsetTime = flushAirAndWaterEnd - flushAirAndWaterStart
	startTime += offsetTime
	print("exchanging control fluid:")
	turnOnlyPin(smu_instance, pumpPins, pumpPins[0])
	time.sleep(5)
	turnOnlyPin(smu_instance, pumpPins, -1)
	
	endTime = time.time()
	print('')
	print('Completed static bias in "' + '{:.4f}'.format(endTime - startTime) + '" seconds.')

	return {
		'Raw':{
			'vds_data':vds_data,
			'id_data':id_data,
			'vgs_data':vgs_data,
			'ig_data':ig_data,
			'pump_on_intervals':pump_on_intervals,
			'pump_on_intervals_pin':pump_on_intervals_pin,
			'timestamps':timestamps,
			'id_std':id_std,
			'ig_std':ig_std,
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
	


