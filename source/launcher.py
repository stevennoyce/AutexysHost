# === Imports ===
import os
import sys
import platform
import time
import copy

from procedures import Burn_Out as burnOutScript
from procedures import Gate_Sweep as gateSweepScript
from procedures import Drain_Sweep as drainSweepScript
from procedures import Auto_Burn_Out as autoBurnScript
from procedures import Static_Bias as staticBiasScript
from procedures import Auto_Gate_Sweep as autoGateScript
from procedures import Auto_Static_Bias as autoBiasScript
from procedures import AFM_Control as afmControlScript
from procedures import Delay as delayScript

from utilities import DataLoggerUtility as dlu
from utilities import PlotPostingUtility as plotPoster
from drivers import SourceMeasureUnit as smu
from drivers import ArduinoBoard as arduinoBoard

import defaults



# === Main API ===
def run(additional_parameters):
	startTime = time.time()
	
	parameters = defaults.with_added(additional_parameters)

	# Initialize measurement system
	smu_systems = initMeasurementSystems(parameters)		

	# Initialize Arduino connection
	arduino_instance = initArduino(parameters)
	print("Sensor data: " + str(parameters['SensorData']))
	
	# Run specified action:
	if((parameters['MeasurementSystem']['systemType'] == 'standalone') and (len(parameters['MeasurementSystem']['deviceRange']) > 0)):
		for device in parameters['MeasurementSystem']['deviceRange']:
			params = copy.deepcopy(parameters)
			params['Identifiers']['device'] = device
			runAction(params, additional_parameters, smu_systems, arduino_instance)
	else:
		runAction(parameters, additional_parameters, smu_systems, arduino_instance)
	
	endTime = time.time()
	print('Completed job in "' + '{:.4f}'.format(endTime - startTime) + '" seconds.')

def run_file(schedule_file_path):
	schedule_index = 0

	print('Opening schedule file: ' + schedule_file_path)

	while( schedule_index < len(dlu.loadJSON(directory='', loadFileName=schedule_file_path)) ):
		print('Loading line #' + str(schedule_index+1) + ' in schedule file ' + schedule_file_path)
		parameter_list = dlu.loadJSON(directory='', loadFileName=schedule_file_path)

		print('Launching job #' + str(schedule_index+1) + ' of ' + str(len(parameter_list)) + ' in schedule file ' + schedule_file_path)
		print('Schedule contains ' + str(len(parameter_list) - schedule_index - 1) + ' other incomplete jobs.')
		additional_parameters = parameter_list[schedule_index].copy()
		run(additional_parameters)

		schedule_index += 1


# === Internal API ===
def runAction(parameters, schedule_parameters, smu_systems, arduino_instance):
	print('Checking that save folder exists.')
	dlu.makeFolder(dlu.getDeviceDirectory(parameters))

	experiment = dlu.incrementJSONExperiementNumber(dlu.getDeviceDirectory(parameters))
	print('About to begin experiment #' + str(experiment))
	parameters['startIndexes'] = dlu.loadJSONIndex(dlu.getDeviceDirectory(parameters))
	parameters['startIndexes']['timestamp'] = time.time()
	
	print('Saving to SchedulesHistory...')
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), 'SchedulesHistory', schedule_parameters, incrementIndex=False)

	for smu_name, smu_instance in smu_systems.items():
		smu_instance.setDevice(parameters['Identifiers']['device'])

	smu_names = list(smu_systems.keys())
	smu_default_instance = smu_systems[smu_names[0]]	

	try:
		if(parameters['runType'] == 'GateSweep'):
			gateSweepScript.run(parameters, smu_default_instance)
		elif(parameters['runType'] == 'DrainSweep'):
			drainSweepScript.run(parameters, smu_default_instance)
		elif(parameters['runType'] == 'BurnOut'):
			burnOutScript.run(parameters, smu_default_instance)
		elif(parameters['runType'] == 'AutoBurnOut'):
			autoBurnScript.run(parameters, smu_default_instance)
		elif(parameters['runType'] == 'StaticBias'):
			staticBiasScript.run(parameters, smu_default_instance, arduino_instance)
		elif(parameters['runType'] == 'AutoGateSweep'):
			autoGateScript.run(parameters, smu_default_instance, arduino_instance)
		elif(parameters['runType'] == 'AutoStaticBias'):
			autoBiasScript.run(parameters, smu_default_instance, arduino_instance)
		elif(parameters['runType'] == 'AFMControl'):
			afmControlScript.run(parameters, smu_systems)
		elif(parameters['runType'] == 'Delay'):
			delayScript.run(parameters)
		else:
			raise NotImplementedError("Invalid action for the Source Measure Unit")
	except Exception as e:
		for smu_name, smu_instance in smu_systems.items():
			smu_instance.rampDownVoltages()
			smu_instance.disconnect()

		parameters['endIndexes'] = dlu.loadJSONIndex(dlu.getDeviceDirectory(parameters))
		parameters['endIndexes']['timestamp'] = time.time()
		print('Saving to ParametersHistory...')
		dlu.saveJSON(dlu.getDeviceDirectory(parameters), 'ParametersHistory', parameters, incrementIndex=False)

		print('ERROR: Exception raised during the experiment.')
		raise
	
	for smu_name, smu_instance in smu_systems.items():
		smu_instance.rampDownVoltages()
	parameters['endIndexes'] = dlu.loadJSONIndex(dlu.getDeviceDirectory(parameters))
	parameters['endIndexes']['timestamp'] = time.time()
	
	print('Saving to ParametersHistory...')
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), 'ParametersHistory', parameters, incrementIndex=False)

	#print('Posting plots online...')
	#plotPoster.postPlots(parameters)





# === SMU Connection ===
def initMeasurementSystems(parameters):
	system_instances = {}
	parameters['MeasurementSystem']['systems'] = smu.getSystemConfiguration(parameters['MeasurementSystem']['systemType'])
	for system_name,system_info in parameters['MeasurementSystem']['systems'].items():
		system_id = system_info['uniqueID']
		system_type = system_info['type']
		system_settings = system_info['settings']
		if(system_type == 'B2912A'):
			system_instances[system_name] = smu.getConnectionToVisaResource(system_id, system_settings, defaultComplianceCurrent=100e-6, smuTimeout=60*1000)
		elif(system_type == 'PCB2v14'):
			system_instances[system_name] = smu.getConnectionToPCB(system_id, system_settings)
		else:
			raise NotImplementedError("Unkown Measurement System specified (try B2912A, PCB2v14, ...)")
		system_id = system_instances[system_name].system_id
		print("Connected to " + str(system_type) + " system '" + str(system_name) + "', with ID: " + str(system_id))
	return system_instances



# === Arduino Connection ===
def initArduino(parameters):
	arduino_instance = None
	baud = 9600
	try:
		port = '/dev/cu.wchusbserial1410'
		arduino_instance = arduinoBoard.getConnection(port, baud)
		print("Connected to Arduino on port: " + str(port))
	except: 
		try:
			port = '/dev/cu.wchusbserial1420'
			arduino_instance = arduinoBoard.getConnection(port, baud)
			print("Connected to Arduino on port: " + str(port))
		except: 
			print("No Arduino connected.")
			return arduinoBoard.getNullInstance()
	sensor_data = arduino_instance.takeMeasurement()
	for (measurement, value) in sensor_data.items():
		parameters['SensorData'][measurement] = [value]
	return arduino_instance
	


