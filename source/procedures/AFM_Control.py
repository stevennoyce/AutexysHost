# === Imports ===
import time
import numpy as np
import threading

from utilities import DataLoggerUtility as dlu

import scipy.optimize
import scipy.signal
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
	
	try:
		optParamVals, optParamCov = scipy.optimize.curve_fit(triangleCosWave, times, values,
			p0 = [guesses[parameterName] for parameterName in parameterNames], 
			bounds=[[-np.inf,-np.inf,-np.inf,-np.inf],[2*(max(values)-min(values)),4*(max(times)-min(times)),np.inf,np.inf]])
	
		for parameterName, value in zip(parameterNames, optParamVals):
			optParams[parameterName] = value
	except RuntimeError as e:
		print('Could not fit:')
		print(list(values))
		optParams = guesses
	
	possiblePhases = optParams['phase'] + np.arange(-20,20,1)*optParams['period']
	optParams['phase'] = min(possiblePhases, key=abs)
	
	return optParams

def getSegmentsOfTriangle(times, values, minSegmentLength=0, maxSegmentLength=float('inf'), discardThreshold=0.25, smoothSegmentsByTrimming=False, smoothSegmentsByOverlapping=False):
	times = np.array(times) - min(times)
	values = np.array(values)
	
	# Fit times and values to a triangle wave
	fitParams = fitTriangleWave(times, values)
	phase = fitParams['phase']
	period = fitParams['period']
	half_period = period/2
	
	# periodsMeasured = int((max(times) - min(times))/period) + 2
	fractionalTracesMeasured = 2*(max(times) - min(times))/period
	tracesMeasured = int(fractionalTracesMeasured)
	pointsPerTrace = len(times)/fractionalTracesMeasured
	
	# Break triangle wave into segments at the peaks and valleys
	all_segments = []
	for i in range(-4, tracesMeasured + 4):
		segment = np.where( ((i*half_period)+phase < times) & (times <= ((i+1)*half_period)+phase) )[0]
		if(len(segment) > 0):
			all_segments.append(list(segment))
	
	# Discard segments that are shorter than 'discardThreshold' times the typical segment length
	# median_segment_length = np.median([len(segment) for segment in all_segments])
	segments = []
	for segment	in all_segments:
		if(len(segment) >= discardThreshold*pointsPerTrace):
			segments.append(segment)
	
	# Attempt to make segments equal length by adding entries
	if(smoothSegmentsByOverlapping): # False by default
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
	if(smoothSegmentsByTrimming): # False by default
		min_segment_length = min(maxSegmentLength, min([len(segment) for segment in all_segments]))
		for segment	in segments:
			while(len(segment) > min_segment_length):
				segment.pop()
				if(len(segment) <= min_segment_length):
					break
				segment.pop(0)
			
	return segments

def extractTraces(deviceHistory):
	if deviceHistory[0]['runConfigs']['SGMControl']['tracesToMeasure'] == 1:
		return {
			'Vx': [[np.array(dh['Results']['smu2_v2_data']) for dh in deviceHistory]],
			'Vy': [[np.array(dh['Results']['smu2_v1_data']) for dh in deviceHistory]],
			'Id': [[np.array(dh['Results']['id_data']) for dh in deviceHistory]],
			'Ig': [[np.array(dh['Results']['ig_data']) for dh in deviceHistory]],
			'time': [[np.array(dh['Results']['timestamps_device']) for dh in deviceHistory]]
		}
	
	Vx_topology_trace = []
	Vx_topology_retrace = []
	Vx_nap_trace = []
	Vx_nap_retrace = []
	
	Vy_topology_trace = []
	Vy_topology_retrace = []
	Vy_nap_trace = []
	Vy_nap_retrace = []
	
	Id_topology_trace = []
	Id_topology_retrace = []
	Id_nap_trace = []
	Id_nap_retrace = []
	
	Ig_topology_trace = []
	Ig_topology_retrace = []
	Ig_nap_trace = []
	Ig_nap_retrace = []
	
	time_topology_trace = []
	time_topology_retrace = []
	time_nap_trace = []
	time_nap_retrace = []
	
	for i in range(len(deviceHistory)):
		timestamps = deviceHistory[i]['Results']['timestamps_smu2']
		Vx = deviceHistory[i]['Results']['smu2_v2_data']
		Vy = deviceHistory[i]['Results']['smu2_v1_data']
		time = deviceHistory[i]['Results']['timestamps_device']
		Ig = np.array(deviceHistory[i]['Results']['ig_data'])
		current = np.array(deviceHistory[i]['Results']['id_data'])
		currentLinearFit = np.polyval(np.polyfit(range(len(current)), current, 1), range(len(current)))
		currentLinearized = current - currentLinearFit
		currentLinearized = currentLinearized - np.median(currentLinearized)
		
		segments = getSegmentsOfTriangle(timestamps, Vx, discardThreshold=0.5, smoothSegmentsByOverlapping=False)
		
		for j in range(len(segments)):
			if((j % 4) == 0):
				Vx_topology_trace.append(list(np.array(Vx)[segments[j]]))
				Vy_topology_trace.append(list(np.array(Vy)[segments[j]]))
				Ig_topology_trace.append(list(np.array(Ig)[segments[j]]))
				Id_topology_trace.append(list(np.array(currentLinearized)[segments[j]]))
				time_topology_trace.append(list(np.array(time)[segments[j]]))
			elif((j % 4) == 1):
				Vx_topology_retrace.append(list(np.array(Vx)[segments[j]]))
				Vy_topology_retrace.append(list(np.array(Vy)[segments[j]]))
				Ig_topology_retrace.append(list(np.array(Ig)[segments[j]]))
				Id_topology_retrace.append(list(np.array(currentLinearized)[segments[j]]))
				time_topology_retrace.append(list(np.array(time)[segments[j]]))
			elif((j % 4) == 2):
				Vx_nap_trace.append(list(np.array(Vx)[segments[j]]))
				Vy_nap_trace.append(list(np.array(Vy)[segments[j]]))
				Ig_nap_trace.append(list(np.array(Ig)[segments[j]]))
				Id_nap_trace.append(list(np.array(currentLinearized)[segments[j]]))
				time_nap_trace.append(list(np.array(time)[segments[j]]))
			elif((j % 4) == 3):
				Vx_nap_retrace.append(list(np.array(Vx)[segments[j]]))
				Vy_nap_retrace.append(list(np.array(Vy)[segments[j]]))
				Ig_nap_retrace.append(list(np.array(Ig)[segments[j]]))
				Id_nap_retrace.append(list(np.array(currentLinearized)[segments[j]]))
				time_nap_retrace.append(list(np.array(time)[segments[j]]))
	
	return {
		'Vx': [Vx_topology_trace, Vx_topology_retrace, Vx_nap_trace, Vx_nap_retrace],
		'Vy': [Vy_topology_trace, Vy_topology_retrace, Vy_nap_trace, Vy_nap_retrace],
		'Id': [Id_topology_trace, Id_topology_retrace, Id_nap_trace, Id_nap_retrace],
		'Ig': [Id_topology_trace, Id_topology_retrace, Id_nap_trace, Id_nap_retrace],
		'time': [time_topology_trace, time_topology_retrace, time_nap_trace, time_nap_retrace]
	}

def extractTraces(deviceHistory):
	if deviceHistory[0]['runConfigs']['SGMControl']['tracesToMeasure'] == 1:
		return {
			'Vx': [[np.array(dh['Results']['smu2_v2_data']) for dh in deviceHistory]],
			'Vy': [[np.array(dh['Results']['smu2_v1_data']) for dh in deviceHistory]],
			'Id': [[np.array(dh['Results']['id_data']) for dh in deviceHistory]],
			'Ig': [[np.array(dh['Results']['ig_data']) for dh in deviceHistory]],
			'time': [[np.array(dh['Results']['timestamps_device']) for dh in deviceHistory]]
		}
	
	result = {
		'Vx': [],
		'Vy': [],
		'Id': [],
		'Ig': [],
		'time': []
	}
	
	allXs = np.array([dh['Results']['smu2_v2_data'] for dh in deviceHistory])
	medXs = np.median(allXs.T - np.median(allXs, axis=1).T, axis=1)
	
	derXs = scipy.signal.savgol_filter(medXs, 11, 2, 1)
	zero_crossings = np.where(np.diff(np.signbit(derXs)))[0]
	
	if zero_crossings.size == 0:
		zero_crossings = np.array([derXs.size])
	if zero_crossings.size == 1 or np.abs(derXs[0]) < 0.8*np.median(np.abs(derXs)):
		zero_crossings = np.append([0], zero_crossings)
	
	# Remove literal duplicates
	zero_crossings = sorted(list(set(zero_crossings)))
	
	segLengths = np.diff(zero_crossings)
	
	# Remove short segments
	segLengths = [l for l in segLengths if l > 0.8*np.median(segLengths)]
	
	segLength = int(np.median(segLengths))
	
	# Remove overlapping
	# To do
	
	segs = [[int(zc), int(zc + segLength)] for zc in zero_crossings if zc + segLength < medXs.size]
	
	result['segs'] = segs
	
	Fsamp = deviceHistory[0]['runConfigs']['SGMControl']['deviceMeasurementSpeed']
	b, a = scipy.signal.bessel(1, [50/(Fsamp/2), 70/(Fsamp/2)], btype='bandstop')
	
	for i in range(len(deviceHistory)):
		Id = np.array(deviceHistory[i]['Results']['id_data'])
		Ig = np.array(deviceHistory[i]['Results']['ig_data'])
		
		deviceHistory[i]['IdFilt'] = scipy.signal.filtfilt(b, a, Id)
		deviceHistory[i]['IgFilt'] = scipy.signal.filtfilt(b, a, Ig)
	
	result['Vx'] = [[np.array(dh['Results']['smu2_v2_data'][s[0]:s[1]]) for dh in deviceHistory] for s in segs]
	result['Vy'] = [[np.array(dh['Results']['smu2_v1_data'][s[0]:s[1]]) for dh in deviceHistory] for s in segs]
	
	result['IdNoFilt'] = [[dh['Results']['id_data'][s[0]:s[1]] for dh in deviceHistory] for s in segs]
	result['IgNoFilt'] = [[dh['Results']['ig_data'][s[0]:s[1]] for dh in deviceHistory] for s in segs]
	
	result['Id'] = [[dh['IdFilt'][s[0]:s[1]] for dh in deviceHistory] for s in segs]
	result['Ig'] = [[dh['IgFilt'][s[0]:s[1]] for dh in deviceHistory] for s in segs]
	
	result['time'] = [[np.array(dh['Results']['timestamps_device'][s[0]:s[1]]) for dh in deviceHistory] for s in segs]
	
	return result

def interpolate_nans(X):
	"""Overwrite NaNs with column value interpolations."""
	for j in range(X.shape[1]):
		mask_j = np.isnan(X[:,j])
		X[mask_j,j] = np.interp(np.flatnonzero(mask_j), np.flatnonzero(~mask_j), X[~mask_j,j])
	return X

def getRasteredMatrix(Vx, Vy, Id):
	# Determine matrix X-dimentions
	max_row_length = max([len(segment) for segment in Vx])
	
	# Convert each segment of Vy into a single value, then find what a reasonable "step" would be between values (need this to deal with noise)
	Vy_averages = [np.mean(segment) for segment in Vy]
	med_Vy_step = np.median(np.diff(Vy_averages))
	
	# Find all of the unqiue values of Vy
	min_distance_to_other_values = lambda candidate, values: min([abs(candidate - val) for val in values]) if(len(values) > 0) else float('inf')
	Vy_unique_values = []
	for Vy_avg in Vy_averages:
		# A Vy segment is considered "different" if is at least half a step away from every other value
		distance = min_distance_to_other_values(Vy_avg, Vy_unique_values)
		if(distance >= 0.5*med_Vy_step):
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
	physicalWidth = abs(max_Vx - min_Vx)/0.157e6
	physicalHeight = abs(max_Vy - min_Vy)/0.138e6
	
	return matrix, physicalWidth, physicalHeight
			

def getStartTime(timestamps, Vxs, skipNumberOfLines=1):
	fitParams = fitTriangleWave(timestamps, Vxs)
	
	periodsMeasured = (max(timestamps) - min(timestamps))/fitParams['period']
	passesMeasured = periodsMeasured
	passTime = fitParams['period']
	
	linesMeasured = passesMeasured/2 # Divide by 2 if nap enabled
	lineTime = 2*passTime # Multiply by 2 if nap enabled
	
	if fitParams['amplitude'] < 0:
		fitParams['phase'] += fitParams['period']/2
	
	possiblePhases = fitParams['phase'] + np.arange(-10,10,1)*fitParams['period']
	
	fitParams['phase'] = min(possiblePhases, key=abs)
	
	startTime = min(timestamps) + fitParams['phase']
	startTime += (lineTime)*(math.ceil(linesMeasured) + skipNumberOfLines)
	
	print('Determined line time to be {}'.format(lineTime))
	print('Determined startTime to be {}'.format(startTime))
	print('Curent time is {}'.format(time.time()))
	
	return startTime

def sleepUntil(startTime):
	time.sleep(startTime - time.time())

def medianMeasurement(smu, key, count):
	results = []
	
	for i in range(count):
		results.append(smu.takeMeasurement()[key])
	
	return np.median(results)

def waitForFrameSwitch(smu_secondary, lineTime):
	print('Waiting for frame switch')
	samples = 5
	
	Vy_1 = medianMeasurement(smu_secondary, 'V_ds', samples)
	time.sleep(1.01*lineTime)
	Vy_2 = medianMeasurement(smu_secondary, 'V_ds', samples)
	
	originalStepVy = Vy_2 - Vy_1
	stepVy = originalStepVy
	
	# While the original step and current step are both positive or both negative
	while(originalStepVy*stepVy > 0): 
		time.sleep(1.01*lineTime)
		Vy_1 = Vy_2
		Vy_2 = medianMeasurement(smu_secondary, 'V_ds', samples)
		stepVy = Vy_2 - Vy_1

	



# === Main ===
def run(parameters, smu_systems, isSavingResults=True, communication_pipe=None):
	# Print the starting message
	print('Beginning AFM-assisted measurements.')
	runAFM(parameters, smu_systems, isSavingResults)	
	# return jsonData



# === Data Collection ===
def runAFM(parameters, smu_systems, isSavingResults=True, communication_pipe=None):
	# Duke label 184553 is 'USB0::0x0957::0x8E18::MY51141244::INSTR' - use for device drain (CH1) and gate (CH2)
	# Duke Label 184554 is 'USB0::0x0957::0x8E18::MY51141241::INSTR' - use for AFM channels x (CH1) and y (CH2)
	
	# Get shorthand name to easily refer to configuration and SMUs
	afm_parameters = parameters['runConfigs']['AFMControl']
	smu_device = smu_systems['deviceSMU']
	smu_secondary = smu_systems['secondarySMU']
	vds = afm_parameters['drainVoltageSetPoint']
	vgs = afm_parameters['gateVoltageSetPoint']
	
	# Set SMU NPLC
	smu_device.setNPLC(1)
	smu_secondary.setNPLC(1)
	
	# Set a low compliance current for startup
	smu_device.setComplianceCurrent(10e-9)
	
	# Turn the device channels on and wait for system capacitances to charge
	print('Turning device channels on and waiting for equilibration')
	smu_device.turnChannelsOn()
	for i in range(10):
		print(smu_device.takeMeasurement())
		time.sleep(1)
	
	# Turn the voltage measurement channels on and wait
	print('Turning voltage measurement channels on')
	smu_secondary.turnChannelsOn()
	time.sleep(1)
	
	# Set SMU compliance to setpoints
	print('Setting device compliance to setpoint')
	smu_device.setComplianceCurrent(afm_parameters['complianceCurrent'])
	time.sleep(1)
	
	print('Setting voltage measurement compliance to setpoint')
	smu_secondary.setComplianceVoltage(afm_parameters['complianceVoltage'])
	time.sleep(1)
	
	# Apply Vgs and Vds to the device
	print('Ramping drain to source voltage')
	smu_device.rampDrainVoltageTo(vds, steps=150)
	print('Ramping gate to source voltage')
	smu_device.rampGateVoltageTo(vgs, steps=150)
	
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
	
	# Collect one more line to firm up the sync
	results = runAFMline(parameters, smu_systems, sleep_time1, sleep_time2)
	runStartTime = getStartTime(results['Raw']['timestamps_smu2'], results['Raw']['smu2_v2_data'], skipNumberOfLines=1)
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
			# Spin a new thread to save the data in the background
			threading.Thread(target=dlu.saveJSON,
				args=(dlu.getDeviceDirectory(parameters), afm_parameters['saveFileName'], jsonData, 'Ex'+str(parameters['startIndexes']['experimentNumber']))
			).start()
		
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
	print('Running AFM Control as Main')
	
	if sys.argv[2] == 'start':
		print('Setting up')

	