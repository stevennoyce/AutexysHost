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
	fsb_parameters = parameters['runConfigs']['FlowStaticBias']

	# Print the starting message
	print('Applying flow static bias of V_GS='+str(fsb_parameters['gateVoltageSetPoint'])+'V, V_DS='+str(fsb_parameters['drainVoltageSetPoint'])+'V')
	smu_instance.setComplianceCurrent(fsb_parameters['complianceCurrent'])	

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
							drainVoltageSetPoint=fsb_parameters['drainVoltageSetPoint'],
							gateVoltageSetPoint=fsb_parameters['gateVoltageSetPoint'],
							measurementTime=fsb_parameters['measurementTime'],
							flowDurations=fsb_parameters['flowDurations'], 
							subCycleDurations=fsb_parameters['subCycleDurations'],
							pumpPins=fsb_parameters['pumpPins'],
							reversePumpPins=fsb_parameters['reversePumpPins'],
							flushPins=fsb_parameters['flushPins'],
							cycleCount=fsb_parameters['cycleCount'],
							solutions=fsb_parameters['solutions'],
							share=share)
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
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), fsb_parameters['saveFileName'], jsonData, subDirectory=parameters['experimentSubFolder']+str(parameters['startIndexes']['experimentNumber']))
	
	return jsonData

# Turns ON "pin", turns every other pin OFF
# if pin == -1, turn off every pin
def turnOnlyPin(smu_instance, pumpPins, pin):
	pumpPins = range(1, 11) # do it for every pin in existence
	for i in pumpPins:
		if i != pin:
			smu_instance.digitalWrite(i, "LOW")
	#print("turning on: " + str(pin))
	smu_instance.digitalWrite(pin, "HIGH")

# Reverses prior pin to recycle, then flushes
def flushingPins(smu_instance, flushPins, reversePumpPins, pinToFlush):
	turnOnlyPin(smu_instance, reversePumpPins, pinToFlush)
	time.sleep(2)
	turnOnlyPin(smu_instance, reversePumpPins, -1)
	time.sleep(1)
	# turn on flushing pin
	turnOnlyPin(smu_instance, flushPins, flushPins[0])
	time.sleep(4)
	turnOnlyPin(smu_instance, flushPins, -1)
	time.sleep(1)
	turnOnlyPin(smu_instance, flushPins, flushPins[1])
	time.sleep(4)
	turnOnlyPin(smu_instance, flushPins, -1)
	time.sleep(1)

# === Data Collection ===
def runFlowStaticBias(smu_instance, drainVoltageSetPoint, gateVoltageSetPoint, measurementTime, flowDurations, subCycleDurations, pumpPins, reversePumpPins, flushPins, cycleCount, solutions, share=None):
	
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
	printStatement = "Starting Flow Static Bias"
	printStatement = printStatement + (40 - len(printStatement)) * " "
	# casting stuff as ints from strings
	'''
	cycleCount = int(cycleCount)
	for a in range(0, len(flowDurations)):
		flowDurations[a] = int(flowDurations[a])
		pumpPins[a] = int(pumpPins[a])
		smu_instance.smu.write(":source:digital:external" + str(pumpPins[a]) + ":function DIO")
		smu_instance.smu.write(":source:digital:external" + str(pumpPins[a]) + ":polarity positive")
		subCycleDurations[a] = int(subCycleDurations[a])
	'''
	
	# define totalBiasTime
	totalBiasTime = 0
	for tt in subCycleDurations:
		totalBiasTime += int(tt) * int(cycleCount)
	
	# Get the SMU measurement speed
	smu_measurementsPerSecond = smu_instance.measurementsPerSecond
	smu_secondsPerMeasurement = 1/smu_measurementsPerSecond

	# Compute the number of data points we will be collecting (unless measurementTime is unreasonably small)
	steps = max(int(totalBiasTime/measurementTime), 1) if(measurementTime > 0) else None
	
	# offsetTime, to account for air and water flushing
	offsetTime = 0
	
	# pour in first fluid prior to measurementCount starting (and thus prior to measurements starting)
	#print("Exchanging fluid for digitalPin: " + str(pumpPins[0]))
	#turnOnlyPin(smu_instance, pumpPins, pumpPins[0])
	#time.sleep(flowDurations[0])
	#print("Stopping fluid exchange")
	#turnOnlyPin(smu_instance, pumpPins, -1) # turn off everything else
	
	# Take a timestamp for the start of the FlowStaticBias
	startTime = time.time()

	# Criteria to keep taking measurements when measurementTime is relatively large
	continueCriterion = lambda i, measurementCount, startTime: i < steps
	smallMeasurementTimeCriterion = lambda: measurementTime < smu_instance.measurementRateVariabilityFactor*smu_secondsPerMeasurement
	if(smallMeasurementTimeCriterion):
		# Criteria to keep taking measurements when measurementTime is very small
		continueCriterion = lambda i, measurementCount, startTime: (time.time() - startTime) < (totalBiasTime - (1/2)*smu_secondsPerMeasurement)
		continueCriterion = lambda i, measurementCount, startTime: (time.time() - startTime) < (totalBiasTime - (1/2)*(time.time() - startTime)/max(measurementCount, 1))
	
	'''
	# initialize pump_on_intervals array
	for cyc in range(0, len(pumpPins)):
		pump_on_intervals.append([])
	
	# define array of all possible times when fluid exchange should happen, given the number of cycles
	allPossibleExchangeTimesStart = []
	allPossibleExchangeTimesStart.append(0) # very initial pin
	for cyc in range(0, cycleCount):
		for cycDur in subCycleDurations:
			timeCounter += cycDur
			allPossibleExchangeTimesStart.append(timeCounter)	
	
	# define array of all possible times when fluid flow, upon initializing, should STOP flowing
	allPossibleExchangeTimesEnd = []
	timeCounter = 1 # offset due to initial flow prior to data collection
	allPossibleExchangeTimesEnd.append(flowDurations[0]) # very first pin's exchange
	for cyc in allPossibleExchangeTimesStart:
		allPossibleExchangeTimesEnd.append(cyc + flowDurations[(timeCounter) % len(flowDurations)])
		timeCounter += 1		
	'''
	
	reversePumpTime = 2;
	forwardFlushTime = 2;
	reverseFlushTime = 2;
	allPossibleExchangeTimes = []
	allPossibleExchangePins = []
	# calculate total cycle duration
	totalCycleDuration = 0
	for subCycleDuration in subCycleDurations:
		totalCycleDuration += subCycleDuration
	for i in range(0, cycleCount):
		cycleStartTime = i*totalCycleDuration
		for forwardPump in range(0, len(pumpPins)):		
			allPossibleExchangeTimes.append(cycleStartTime)
			allPossibleExchangePins.append(pumpPins[forwardPump])
			allPossibleExchangeTimes.append(cycleStartTime + flowDurations[forwardPump])
			allPossibleExchangePins.append(-1)
			if len(reversePumpPins) != 0:
				reversePumpStartTime = cycleStartTime + subCycleDurations[forwardPump] - reversePumpTime - forwardFlushTime - reverseFlushTime;
				allPossibleExchangeTimes.append(reversePumpStartTime) # reverse pin first
				allPossibleExchangePins.append(reversePumpPins[forwardPump])
				allPossibleExchangeTimes.append(reversePumpStartTime + forwardFlushTime) # flush pin first
				allPossibleExchangePins.append(flushPins[0])
				allPossibleExchangeTimes.append(reversePumpStartTime + forwardFlushTime + reverseFlushTime)
				allPossibleExchangePins.append(flushPins[1])
			cycleStartTime += subCycleDurations[forwardPump]
	
	print(allPossibleExchangeTimes)
	print(allPossibleExchangePins)
	print("Exchanging: " , [i.upper() for i in solutions])
	print("Estimated Time: " + str(totalBiasTime) + " seconds")

	i = 0
	measurementCount = 0	
	currentIndex = 0
	pinInQuestion = -1
	while(continueCriterion(i, measurementCount, startTime)):
		if (smallMeasurementTimeCriterion):
			pipes.progressUpdate(share, 'Flow Static Bias Point', start=0, current=i+1, end=steps)
		else:
			pipes.progressUpdate(share, 'Flow Static Bias Point', start=0, current=i+1, end=steps)

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
			
			currentTimeNotRounded = time.time() - startTime
			roundCurrentTime = int(currentTimeNotRounded)
			
			if roundCurrentTime in allPossibleExchangeTimes: # start exchanging fluids; pin will constantly be spammed ON but doesn't matter
				currentIndex = allPossibleExchangeTimes.index(roundCurrentTime)
				pinInQuestion = allPossibleExchangePins[currentIndex]
				if pinInQuestion in pumpPins:
					#print("Exchanging Fluid: " + solutions[pumpPins.index(pinInQuestion)] + " at Pin: " + str(pinInQuestion))
					printStatement = "Exchanging Fluid: " + solutions[pumpPins.index(pinInQuestion)].upper() + " at Pin: " + str(pinInQuestion)
					printStatement = printStatement + (40 - len(printStatement)) * " "
				elif pinInQuestion in reversePumpPins:
					#print("Reversing Fluid: " + solutions[reversePumpPins.index(pinInQuestion)] + " at Pin: " + str(pinInQuestion))
					printStatement = "Reversing Fluid: " + solutions[reversePumpPins.index(pinInQuestion)].upper() + " at Pin: " + str(pinInQuestion)
					printStatement = printStatement + (40 - len(printStatement)) * " "
				elif pinInQuestion in flushPins:
					if flushPins.index(pinInQuestion) == 0:
						#print("Flushing Water Through")
						printStatement = "Flushing Water Through"
						printStatement = printStatement + (40 - len(printStatement)) * " "
					else:
						#print("Reversing Water")
						printStatement = "Reversing Water"
						printStatement = printStatement + (40 - len(printStatement)) * " "
				elif pinInQuestion == -1:
					#print("Stopping Fluid Flow")
					printStatement = "Stopping Fluid Flow"
					printStatement = printStatement + (40 - len(printStatement)) * " "
				turnOnlyPin(smu_instance, pumpPins, allPossibleExchangePins[currentIndex])
				
			
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
		vds_data_median = np.median(measurements['Vds_data'])
		vds_data.append(vds_data_median)
		id_data_median = np.median(measurements['Id_data'])
		id_data.append(id_data_median)
		vgs_data_median = np.median(measurements['Vgs_data'])
		vgs_data.append(vgs_data_median)
		ig_data_median = np.median(measurements['Ig_data'])
		ig_data.append(ig_data_median)
		timestamps.append(timestamp)
		
		pump_on_intervals.append(time.time() - startTime)
		pump_on_intervals_pin.append(pinInQuestion)

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

		# Send a data message
		pipes.livePlotUpdate(share,plots=
		[livePlotter.createLiveDataPoint(plotID='Current vs. Time',
										labels=['Flow Static Bias Drain Current [A]', 'Flow Static Bias Gate Current [A]'],
										xValues=[timestamp, timestamp], 
										yValues=[id_data_median, ig_data_median], 
										xAxisTitle='Time (s)', 
										yAxisTitle='Current (A)', 
										yscale='log', 
										enumerateLegend=False,
										timeseries=True),
		])

		# Update Flow Progress
		elapsedTime = time.time() - startTime
		print('\r'+printStatement + '[' + int(elapsedTime*30.0/totalBiasTime)*'=' + (30-int(elapsedTime*30.0/totalBiasTime)-1)*' ' + ']', end=' ')
		
		# Update progress bar
		#print('\r[' + int(elapsedTime*70.0/totalBiasTime)*'=' + (70-int(elapsedTime*70.0/totalBiasTime)-1)*' ' + ']' + printStatement, end='')
		i += 1
	
	
	'''
	print("START: Recycling, then flushing environment")
	flushStart = time.time()
	pinToReverseIndex = (pinAlternatingCounter - 1) % len(pumpPins) # index of pin to reverse to recycle prior to flowing in next fluid
	pinToReverse = reversePumpPins[pinToReverseIndex]
	flushingPins(smu_instance, flushPins, reversePumpPins, pinToReverse)
	print("DONE: Recycling, then flushing environment")
	flushEnd = time.time()
	offsetTime = flushEnd - flushStart
	startTime += offsetTime
	'''
	
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
	


