# === Imports ===
import time
import numpy as np
import threading

from procedures import Device_History as deviceHistoryScript
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

def getStartTime(timestamps, Vxs):
	fitParams = fitTriangleWave(timestamps, values)
	
	periodsMeasured = (max(timestamps) - min(timestamps))/fitParams['period']
	passesMeasured = periodsMeasured
	passTime = fitParams['period']
	linesMeasured = passesMeasured/2 # Divide by 2 if nap enabled
	lineTime = 2*passTime # Multiply by 2 if nap enabled
	
	startTime = min(timestamps) + fitParams['phase']
	startTime += lineTime*2*math.ceil(linesMeasured)
	
	return startTime

def sleepUntil(startTime):
	time.sleep(startTime - time.time())

# === Main ===
def run(parameters, smu_systems, isSavingResults=True, isPlottingResults=False):
	# Create distinct parameters for plotting the results
	dh_parameters = {}
	dh_parameters['Identifiers'] = dict(parameters['Identifiers'])
	dh_parameters['dataFolder'] = parameters['dataFolder']
	dh_parameters['plotGateSweeps'] = False
	dh_parameters['plotBurnOuts'] = False
	dh_parameters['plotStaticBias'] = False
	dh_parameters['showFiguresGenerated'] = True
	dh_parameters['saveFiguresGenerated'] = False
	dh_parameters['excludeDataBeforeJSONExperimentNumber'] = parameters['startIndexes']['experimentNumber']
	dh_parameters['excludeDataAfterJSONExperimentNumber'] =  parameters['startIndexes']['experimentNumber']

	# Print the starting message
	print('Beginning AFM-assisted measurements.')
	
	runAFM(parameters, smu_systems, isSavingResults, isPlottingResults)	
	
	# Show plots to the user
	if(isPlottingResults):
		deviceHistoryScript.run(dh_parameters)
		
	# return jsonData

# === Data Collection ===
def runAFM(parameters, smu_systems, isSavingResults, isPlottingResults):
	# Duke label 184553 is 'USB0::0x0957::0x8E18::MY51141244::INSTR' - use for device drain (CH1) and gate (CH2)
	# Duke Label 184554 is 'USB0::0x0957::0x8E18::MY51141241::INSTR' - use for AFM channels x (CH1) and y (CH2)
	
	# Get shorthand name to easily refer to configuration parameters
	afm_parameters = parameters['runConfigs']['AFMControl']
	
	smu_device = smu_systems['deviceSMU']
	smu_secondary = smu_systems['secondarySMU']
	
	# Set SMU source modes
	# smu_device.setChannel1SourceMode("voltage")
	# smu_device.setChannel2SourceMode("voltage")
	
	# smu_secondary.setChannel1SourceMode("current")
	# smu_secondary.setChannel2SourceMode("current")
	
	# Set SMU NPLC
	smu_device.setNPLC(1)
	smu_secondary.setNPLC(1)
	
	# Set SMU compliance
	smu_device.setComplianceCurrent(afm_parameters['complianceCurrent'])
	# smu_device.setComplianceVoltage(afm_parameters['complianceVoltage'])
	
	# smu_secondary.setComplianceCurrent(afm_parameters['complianceCurrent'])	
	smu_secondary.setComplianceVoltage(afm_parameters['complianceVoltage'])
	
	# Apply Vgs and Vds to the device
	smu_device.rampDrainVoltageTo(afm_parameters['drainVoltageSetPoint'])
	smu_device.rampGateVoltageTo(afm_parameters['gateVoltageSetPoint'])
	
	smu_device.takeMeasurement()
	smu_secondary.takeMeasurement()
	
	# input('Press enter to begin the measurement...')
	
	# for line in range(afm_parameters['lines']):
	# 	print('Line {} of {}'.format(line, afm_parameters['lines']))
		
	# 	lineStartTime = time.time()
	# 	traceTime = (1/afm_parameters['scanRate'])/2
	# 	passTime = 2*traceTime
	# 	lineTime = 2*traceTime
	# 	if afm_parameters['napOn']:
	# 		lineTime = lineTime*2
		
	# 	passPoints = afm_parameters['deviceMeasurementSpeed']*passTime
		
	# 	results = runAFMline(parameters, smu_systems, isSavingResults, isPlottingResults, passPoints)
		
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
	
	passTime = 1/afm_parameters['scanRate']
	traceTime = passTime/2
	lineTime = 2*traceTime
	if afm_parameters['napOn']:
		lineTime = lineTime*2
	
	passPoints = afm_parameters['deviceMeasurementSpeed']*passTime
	
	vds = afm_parameters['drainVoltageSetPoint']
	vgs = afm_parameters['gateVoltageSetPoint']
	interval = 1/afm_parameters['deviceMeasurementSpeed']
	
	sleep_time1 = smu_device.setupSweep(vds, vds, vgs, vgs, passPoints, triggerInterval=interval)
	sleep_time2 = smu_secondary.setupSweep(0, 0, 0, 0, passPoints, triggerInterval=interval)
	
	
	results = runAFMline(parameters, smu_systems, isSavingResults, isPlottingResults, sleep_time1, sleep_time2)
	
	runStartTime = getStartTime(results['timestamps_smu2'], results['smu2_v2_data'])
	sleepUntil(runStartTime)
	
	for line in range(afm_parameters['lines']):
		print('Starting line {} of {}'.format(line+1, afm_parameters['lines']))
		
		lineStartTime = time.time()
		results = runAFMline(parameters, smu_systems, isSavingResults, isPlottingResults, sleep_time1, sleep_time2)
		
		# Add important metrics from the run to the parameters for easy access later in ParametersHistory
		parameters['Computed'] = results['Computed']
		
		# Copy parameters and add in the test results
		jsonData = dict(parameters)
		jsonData['Results'] = results['Raw']
		
		# Save results as a JSON object
		if(isSavingResults):
			print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
			# _thread.start_new_thread(dlu.saveJSON, (dlu.getDeviceDirectory(parameters), afm_parameters['saveFileName'], jsonData))
			threading.Thread(target=dlu.saveJSON,
				args=(dlu.getDeviceDirectory(parameters), afm_parameters['saveFileName'], jsonData)
			).start()
			# dlu.saveJSON(dlu.getDeviceDirectory(parameters), afm_parameters['saveFileName'], jsonData)
		
		elapsedRunTime = time.time() - runStartTime
		elapsedLineTime = elapsedRunTime - line*lineTime
		print('Time elapsed is {}, lineTime is {}'.format(elapsedLineTime, lineTime))
		time.sleep(max(lineTime - elapsedLineTime, 0))
	
	smu_device.turnChannelsOff()


def runAFMline(parameters, smu_systems, isSavingResults, isPlottingResults, sleep_time1, sleep_time2):
	# Get shorthand name to easily refer to configuration parameters
	afm_parameters = parameters['runConfigs']['AFMControl']
	
	smu_device = smu_systems['deviceSMU']
	smu_secondary = smu_systems['secondarySMU']
	
	lineStartTime = time.time()
	
	# Device SMU data
	vds_data = []
	id_data = []
	vgs_data = []
	ig_data = []
	device_timestamps = []
	
	# Seconary SMU data
	smu2_v1_data = []
	smu2_i1_data = []
	smu2_v2_data = []
	smu2_i2_data = []
	smu2_timestamps = []
	
	# Take measurements
	smu_device.initSweep()
	startTime1 = time.time()
	smu_secondary.initSweep()
	startTime2 = time.time()
	
	time.sleep(0.5*min(sleep_time1 - (startTime2 - startTime1), sleep_time2))
	
	results_device = smu_device.endSweep()
	results_secondary = smu_secondary.endSweep()
	
	print('Difference in start times is {} s'.format(startTime2 - startTime1))
	
	# Pick the data to save
	vds_data = results_device['Vds_data']
	id_data = results_device['Id_data']
	vgs_data = results_device['Vgs_data']
	ig_data = results_device['Ig_data']
	timestamps_device = [startTime1 + t for t in results_device['timestamps']]
	
	smu2_v1_data = results_secondary['Vds_data']
	smu2_i1_data = results_secondary['Id_data']
	smu2_v2_data = results_secondary['Vgs_data']
	smu2_i2_data = results_secondary['Ig_data']
	timestamps_smu2 = [startTime2 + t for t in results_secondary['timestamps']]
	
	return {
		'Raw':{
			'vds_data':vds_data,
			'id_data':id_data,
			'vgs_data':vgs_data,
			'ig_data':ig_data,
			'timestamps_device':timestamps_device,
			'smu2_v1_data':smu2_v1_data,
			'smu2_i1_data':smu2_i1_data,
			'smu2_v2_data':smu2_v2_data,
			'smu2_i2_data':smu2_i2_data,
			'timestamps_smu2':timestamps_smu2,
		},
		'Computed':{
			'metric that you care about':123456789
		}
	}


	