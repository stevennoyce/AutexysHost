# === Imports ===
import time
import numpy as np
import threading

from utilities import DataLoggerUtility as dlu

import scipy.optimize
import math

def triangleSine(x):
	coefficients = [(-1)**i*(2*i+1)**(-2)*np.sin((2*i+1)*x) for i in range(15)]
	wave = np.sum(coefficients, axis=0)
	return wave/np.max(wave)

def triangleSinWave(times, amplitude, period, phase, offset):
	return offset + amplitude*triangleSine(2*np.pi*(times - phase)/period)

def triangleCosWave(times, amplitude, period, phase, offset):
	return triangleSinWave(times, amplitude, period, phase - period/4, offset)

def fitTriangleWave(times, values):
	parameterNames = ['amplitude', 'period', 'phase', 'offset']
	
	values = np.array(values)
	minTime = np.min(times)
	times = np.array(times) - minTime
	
	slopes = np.abs(values[1:]-values[0:-1])/((max(times)-min(times))/len(times))
	slope = np.median(slopes)
	
	guesses = {}
	optParams = {}
	
	guesses['amplitude'] = (np.max(values) - np.min(values))/2
	guesses['period'] = np.max(times)/2
	guesses['period'] = 4*guesses['amplitude']/slope
	guesses['offset'] = np.mean(values)
	guesses['phase'] = (1-(values[0] - np.min(values))/(guesses['amplitude']*2))/(guesses['period']/2)
	
	if values[1] < values[0]:
		# guesses['phase'] = guesses['period'] - guesses['phase'] # Use this for always positive phase
		guesses['phase'] *= -1 # Use this for smallest phase, positive or negative
	
	optParamVals, optParamCov = scipy.optimize.curve_fit(triangleCosWave, times, values,
		p0 = [guesses[parameterName] for parameterName in parameterNames])
	
	for parameterName, value in zip(parameterNames, optParamVals):
		optParams[parameterName] = value
	
	return optParams

def getSegmentsOfTriangle(times, values, minSegmentLength=0, maxSegmentLength=float('inf'), discardThreshold=0.25, smoothSegmentsByTrimming=False, smoothSegmentsByOverlapping=False):
	times = np.array(times) - min(times)
	values = np.array(values)
	
	# Fit times and values to a triangle wave
	fitParams = fitTriangleWave(times, values)
	phase = fitParams['phase']
	period = fitParams['period']
	half_period = period/2
	
	periodsMeasured = int((max(times) - min(times))/period) + 2
	tracesMeasured = 2*periodsMeasured
	
	# Break triangle wave into segments at the peaks and valleys
	all_segments = []
	for i in range(-1, tracesMeasured):
		segment = np.where( ((i*half_period)+phase < times) & (times <= ((i+1)*half_period)+phase) )[0]
		if(len(segment) > 0):
			all_segments.append(list(segment))
			
	# Discard segments that are shorter than 'discardThreshold' times the typical segment length
	median_segment_length = np.median([len(segment) for segment in all_segments])
	segments = []
	for segment	in all_segments:
		if(len(segment) >= discardThreshold*median_segment_length):
			segments.append(segment)
		
	# Attempt to make segments equal length by adding entries
	if(smoothSegmentsByOverlapping):
		max_segment_length = max(minSegmentLength, max([len(segment) for segment in all_segments]))
		for segment	in segments:
			while(len(segment) < max_segment_length):
				if(max(segment) + 1 < len(times)):
					segment.append(max(segment) + 1)
				if(len(segment) >= max_segment_length):
					break
				if(min(segment) > 0):
					segment.insert(0, min(segment) - 1)
	
	# Attempt to make segments equal length by removing entries
	if(smoothSegmentsByTrimming):
		min_segment_length = min(maxSegmentLength, min([len(segment) for segment in all_segments]))
		for segment	in segments:
			while(len(segment) > min_segment_length):
				segment.pop()
				if(len(segment) <= min_segment_length):
					break
				segment.pop(0)
			
	return segments

def getRasteredMatrix(Vx, Vy, Id):
	# Determine matrix X-dimentions
	max_row_length = max([len(segment) for segment in Vx])	
	
	# Convert each segment of Vy into a single value, then find what a reasonable "step" would be between values (need this to deal with noise)
	Vy_averages = [np.mean(segment) for segment in Vy]
	max_Vy_step = max([abs(Vy_averages[i+1] - Vy_averages[i]) for i in range(len(Vy_averages) - 1)])
	
	# Find all of the unqiue values of Vy
	min_distance_to_other_values = lambda candidate, values: min([abs(candidate - val) for val in values]) if(len(values) > 0) else float('inf')
	Vy_unique_values = []
	for Vy_avg in Vy_averages:
		# A Vy segment is considered "different" if is at least half a step away from every other value
		distance = min_distance_to_other_values(Vy_avg, Vy_unique_values)
		if(distance >= 0.5*max_Vy_step):
			Vy_unique_values.append(Vy_avg)
	Vy_unique_values = list(reversed(sorted(Vy_unique_values))) ## TODO: determine which ordering of Vy will plot it not upside-down
	
	# We now have the number of "real" lines if some lines were scanned multiple times
	number_of_rows = len(Vy_unique_values)
	
	# Create empty matrix
	matrix = np.full((number_of_rows, max_row_length), np.NaN)
	
	# If this is a retrace, reverse the data so that we can treat it the same as a regular trace
	for i in range(len(Vx)):
		if(Vx[i][0] > Vx[i][-1]):
			Vx[i] = list(reversed(Vx[i]))
			Vy[i] = list(reversed(Vy[i]))
			Id[i] = list(reversed(Id[i]))
	
	# Get one of the max-length rows to align any shorter rows to	
	template_row = []
	for segment in Vx:
		if(len(segment) >= len(template_row)):
			template_row = segment
	
	# Fill matrix with data by shifting rows into place
	for r in range(len(Vx)):
		# Get the relevant data for this row in the matrix
		row_values = list(Id[r])
		row_Vx = list(Vx[r])
		row_Vy = list(Vy[r])
		
		# Fix the width of the row by filling in blank squares
		offset = 0
		while(len(row_values) < max_row_length):
			if(Vx[r][0] > template_row[offset+1]):
				row_values.insert(0, np.NaN)
				if(offset < len(row_values) - 1):
					offset += 1
			else:
				row_values.append(np.NaN)
		
		# Identify the position of the row by its average Vy
		row_Vy_avg = np.mean(row_Vy)
		row_index = np.abs(np.array(Vy_unique_values) - row_Vy_avg).argmin()

		# For now, if data was previously assigned to this row it is simply overwritten by the more recent data		
		matrix[row_index] = row_values
	
	# Determine physical X and Y-dimensions
	max_Vx = max([max(seg) for seg in Vx])
	min_Vx = min([min(seg) for seg in Vx])
	max_Vy = max([max(seg) for seg in Vy])
	min_Vy = min([min(seg) for seg in Vy])
	physicalWidth = abs(max_Vx - min_Vx)/0.157
	physicalHeight = abs(max_Vy - min_Vy)/0.138
	
	return matrix, physicalWidth, physicalHeight
			

def getStartTime(timestamps, Vxs, skipNumberOfLines=1):
	fitParams = fitTriangleWave(timestamps, Vxs)
	
	periodsMeasured = (max(timestamps) - min(timestamps))/fitParams['period']
	passesMeasured = periodsMeasured
	passTime = fitParams['period']
	
	linesMeasured = passesMeasured/2 # Divide by 2 if nap enabled
	lineTime = 2*passTime # Multiply by 2 if nap enabled
	
	startTime = min(timestamps) + fitParams['phase']
	startTime += (lineTime)*(math.ceil(linesMeasured) + skipNumberOfLines)
	
	print('Determined line time to be {}'.format(lineTime))
	print('Determined startTime to be {}'.format(startTime))
	print('Curent time is {}'.format(time.time()))
	
	return startTime

def sleepUntil(startTime):
	time.sleep(startTime - time.time())

def waitForFrameSwitch(smu_secondary, lineTime):
	Vy_1 = smu_secondary.takeMeasurement()['V_ds']
	time.sleep(1.1*lineTime)
	Vy_2 = smu_secondary.takeMeasurement()['V_ds']
	oritinalStepVy = Vy_2 - Vy_1
	stepVy = oritinalStepVy
	
	# While the original step and current step are both positive or both negative
	while(oritinalStepVy*stepVy > 0): 
		time.sleep(1.1*lineTime)
		Vy_1 = Vy_2
		Vy_2 = smu_secondary.takeMeasurement()['V_ds']
		stepVy = Vy_2 - Vy_1

	



# === Main ===
def run(parameters, smu_systems, isSavingResults=True):
	# Print the starting message
	print('Beginning AFM-assisted measurements.')
	runAFM(parameters, smu_systems, isSavingResults)	
	# return jsonData



# === Data Collection ===
def runAFM(parameters, smu_systems, isSavingResults=True):
	# Duke label 184553 is 'USB0::0x0957::0x8E18::MY51141244::INSTR' - use for device drain (CH1) and gate (CH2)
	# Duke Label 184554 is 'USB0::0x0957::0x8E18::MY51141241::INSTR' - use for AFM channels x (CH1) and y (CH2)
	
	# Get shorthand name to easily refer to configuration and SMUs
	afm_parameters = parameters['runConfigs']['AFMControl']
	smu_device = smu_systems['deviceSMU']
	smu_secondary = smu_systems['secondarySMU']
	vds = afm_parameters['drainVoltageSetPoint']
	vgs = afm_parameters['gateVoltageSetPoint']
	
	# Set SMU source modes
	#smu_device.setChannel1SourceMode("voltage")
	#smu_device.setChannel2SourceMode("voltage")
	#smu_secondary.setChannel1SourceMode("current")
	#smu_secondary.setChannel2SourceMode("current")
	
	# Set SMU NPLC
	smu_device.setNPLC(1)
	smu_secondary.setNPLC(1)
	
	# Set SMU compliance
	smu_device.setComplianceCurrent(afm_parameters['complianceCurrent'])
	smu_secondary.setComplianceVoltage(afm_parameters['complianceVoltage'])
	
	# Apply Vgs and Vds to the device
	smu_device.rampDrainVoltageTo(vds)
	smu_device.rampGateVoltageTo(vgs)
	
	# Take a measurement to update the SMU visual displays
	smu_device.takeMeasurement()
	smu_secondary.takeMeasurement()
	
	# input('Press enter to begin the measurement...')
	# time.sleep(300)
	
	# for line in range(afm_parameters['lines']):
	# 	print('Line {} of {}'.format(line, afm_parameters['lines']))
		
	# 	lineStartTime = time.time()
	# 	traceTime = (1/afm_parameters['scanRate'])/2
	# 	passTime = 2*traceTime
	# 	lineTime = 2*traceTime
	# 	if afm_parameters['napOn']:
	# 		lineTime = lineTime*2
		
	# 	passPoints = afm_parameters['deviceMeasurementSpeed']*passTime
		
	# 	results = runAFMline(parameters, smu_systems, passPoints)
		
	# 	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	# 	parameters['Computed'] = results['Computed']
		
	# 	# Copy parameters and add in the test results
	# 	jsonData = dict(parameters)
	# 	jsonData['Results'] = results['Raw']
		
	# 	# Save results as a JSON object
	# 	if(isSavingResults):
	# 		print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	# 		dlu.saveJSON(dlu.getDeviceDirectory(parameters), afm_parameters['saveFileName'], jsonData)
		
	# 	elapsedTime = time.time() - lineStartTime
	# 	print('Time elapsed is {}, lineTime is {}'.format(elapsedTime, lineTime))
	# 	time.sleep(max(lineTime - elapsedTime, 0))
	
	# Compute time per trace, pass (aka 2 traces) and line (aka topology pass + nap pass), as well as the approx number of points to collect per pass
	passTime = 1/afm_parameters['scanRate']
	traceTime = passTime/2
	lineTime = 2*traceTime
	if(afm_parameters['napOn']):
		lineTime = lineTime*2
	passPoints = afm_parameters['deviceMeasurementSpeed']*passTime
	
	# Choose the amount of time it takes for the SMU to measure one point
	interval = 1/afm_parameters['deviceMeasurementSpeed']
	
	# Prepare the SMUs to collect data in sweep mode
	sleep_time1 = smu_device.setupSweep(vds, vds, vgs, vgs, passPoints, triggerInterval=interval)
	sleep_time2 = smu_secondary.setupSweep(0, 0, 0, 0, passPoints, triggerInterval=interval)
	
	# If desired, wait for the AFM to reach the end of a scan before beginning
	if(afm_parameters['startOnFrameSwitch']):
		waitForFrameSwitch(smu_secondary, lineTime)
	
	# Collect one line un-synchronized to the AFM to figure out when the next trace will start
	results = runAFMline(parameters, smu_systems, sleep_time1, sleep_time2)
	
	runStartTime = getStartTime(results['Raw']['timestamps_smu2'], results['Raw']['smu2_v2_data'], skipNumberOfLines=3)
	sleepUntil(runStartTime)
	
	for line in range(afm_parameters['lines']):
		print('Starting line {} of {}'.format(line+1, afm_parameters['lines']))
		
		results = runAFMline(parameters, smu_systems, sleep_time1, sleep_time2)
				
		# Copy parameters and add in the test results
		parameters['Computed'] = results['Computed']
		jsonData = dict(parameters)
		jsonData['Results'] = results['Raw']
		
		# Save results as a JSON object
		if(isSavingResults):
			print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
			# _thread.start_new_thread(dlu.saveJSON, (dlu.getDeviceDirectory(parameters), afm_parameters['saveFileName'], jsonData))
			threading.Thread(target=dlu.saveJSON,
				args=(dlu.getDeviceDirectory(parameters), afm_parameters['saveFileName'], jsonData, 'Ex'+str(parameters['startIndexes']['experimentNumber']))
			).start()
			# dlu.saveJSON(dlu.getDeviceDirectory(parameters), afm_parameters['saveFileName'], jsonData)
		
		fittedStartTime = getStartTime(results['Raw']['timestamps_smu2'], results['Raw']['smu2_v2_data'], skipNumberOfLines=1)
		elapsedRunTime = time.time() - runStartTime
		elapsedLineTime = elapsedRunTime - line*lineTime
		print('Time elapsed is {}, lineTime is {}'.format(elapsedLineTime, lineTime))
		
		plannedDelay = max(lineTime - elapsedLineTime, 0)
		fittedDelay = fittedStartTime - time.time()
		if(abs(plannedDelay - fittedDelay) < 0.25*plannedDelay):
			time.sleep(fittedDelay)
		else: 
			time.sleep(plannedDelay)
	
	smu_device.turnChannelsOff()



def runAFMline(parameters, smu_systems, sleep_time1, sleep_time2):
	# Get shorthand name to easily refer to configuration and SMUs
	afm_parameters = parameters['runConfigs']['AFMControl']
	smu_device = smu_systems['deviceSMU']
	smu_secondary = smu_systems['secondarySMU']
		
	# Take measurements
	smu_device.initSweep()
	startTime1 = time.time()
	smu_secondary.initSweep()
	startTime2 = time.time()
	
	# Sleep for about half the time it takes for the data to be collected
	time.sleep(0.5*min(sleep_time1 - (startTime2 - startTime1), sleep_time2))
	
	# Request data from the SMUs
	results_device = smu_device.endSweep()
	results_secondary = smu_secondary.endSweep()
	
	print('Difference in start times is {} s'.format(startTime2 - startTime1))
	
	# Adjust timestamps to be in realtime values
	timestamps_device = [startTime1 + t for t in results_device['timestamps']]
	timestamps_smu2 = [startTime2 + t for t in results_secondary['timestamps']]
	
	return {
		'Raw':{
			'vds_data':	results_device['Vds_data'],
			'id_data':	results_device['Id_data'],
			'vgs_data':	results_device['Vgs_data'],
			'ig_data':	results_device['Ig_data'],
			'timestamps_device': timestamps_device,
			'smu2_v1_data':	results_secondary['Vds_data'],
			'smu2_i1_data':	results_secondary['Id_data'],
			'smu2_v2_data':	results_secondary['Vgs_data'],
			'smu2_i2_data':	results_secondary['Ig_data'],
			'timestamps_smu2': timestamps_smu2,
		},
		'Computed':{
			
		}
	}

if(__name__=='__main__'):
	x = np.array([1,2,3,4,3,2,1,2,3,4, 3, 2, 1, 2, 3, 4])
	t = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
	i = getSegmentsOfTriangle(t, x)
	print(i)
	print(x[i[0]])

	