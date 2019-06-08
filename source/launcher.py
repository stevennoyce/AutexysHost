"""This module is used to 'launch' or execute a particular experiment. When the experiment completes, the launcher is finished.
Experiments are typically fed to the launcher by a dispatcher as it reads experiments out of a schedule file. The launcher can 
also be run by providing a subset of the parameters found in defaults.py, but it is still recommended to define these parameters 
in a schedule file and have a dispatcher handle execution."""

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
from procedures import Flow_Static_Bias as flowStaticBiasScript
from procedures import Auto_Gate_Sweep as autoGateScript
from procedures import Auto_Drain_Sweep as autoDrainScript
from procedures import Auto_Static_Bias as autoBiasScript
from procedures import AFM_Control as afmControlScript
from procedures import SGM_Control as sgmControlScript
from procedures import Delay as delayScript
from procedures import Inverter_Sweep as inverterSweepScript
from procedures import Rapid_Bias as rapidBiasScript
from procedures import Noise_Collection as noiseCollectionScript
from procedures import Noise_Grid as noiseGridScript

from utilities import DataLoggerUtility as dlu
from drivers import SourceMeasureUnit as smu
from drivers import ArduinoBoard as arduinoBoard

import defaults



# === Main API ===
def run(additional_parameters, communication_pipe=None):
	"""Begins execution of an experiment whose parameters are defined by the union of addition_parameters and defaults.py.
	Also initializes a connection to the necessary SMU systems and/or Arduino systems needed to perform the experiment."""
	
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
			runAction(params, additional_parameters, smu_systems, arduino_instance, communication_pipe=communication_pipe)
	else:
		runAction(parameters, additional_parameters, smu_systems, arduino_instance, communication_pipe=communication_pipe)
	
	endTime = time.time()
	print('Completed job in "' + '{:.4f}'.format(endTime - startTime) + '" seconds.')



# === Internal API ===
def runAction(parameters, schedule_parameters, smu_systems, arduino_instance, communication_pipe=None):
	"""Prepares the file system for the upcoming experiment and selects a Procedure to carry out the experiment.
	In the event of an error during any procedure, this function is responsible for emergency ramping down the
	SMU voltages and exiting as gracefully as possible."""
	
	print('Checking that save folder exists.')
	dlu.makeFolder(dlu.getDeviceDirectory(parameters))
	
	experiment = dlu.incrementJSONExperimentNumber(dlu.getDeviceDirectory(parameters))
	print('About to begin experiment #' + str(experiment) + ' for device ' + str(parameters['Identifiers']['wafer']) + str(parameters['Identifiers']['chip']) + ':' + str(parameters['Identifiers']['device']))
	parameters['startIndexes'] = dlu.loadJSONIndex(dlu.getDeviceDirectory(parameters))
	parameters['startIndexes']['timestamp'] = time.time()
	
	parameters['originalRunType'] = parameters['runType']
	
	print('Saving to SchedulesHistory...')
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), 'SchedulesHistory', schedule_parameters, incrementIndex=False)
	
	for smu_name, smu_instance in smu_systems.items():
		smu_instance.setDevice(parameters['Identifiers']['device'])
	
	smu_names = list(smu_systems.keys())
	smu_default_instance = smu_systems[smu_names[0]]	
	
	try:
		if(parameters['runType'] == 'GateSweep'):
			gateSweepScript.run(parameters, smu_default_instance, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'DrainSweep'):
			drainSweepScript.run(parameters, smu_default_instance, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'BurnOut'):
			burnOutScript.run(parameters, smu_default_instance, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'AutoBurnOut'):
			autoBurnScript.run(parameters, smu_default_instance, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'StaticBias'):
			staticBiasScript.run(parameters, smu_default_instance, arduino_instance, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'FlowStaticBias'):
			flowStaticBiasScript.run(parameters, smu_default_instance, arduino_instance, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'AutoGateSweep'):
			autoGateScript.run(parameters, smu_default_instance, arduino_instance, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'AutoDrainSweep'):
			autoDrainScript.run(parameters, smu_default_instance, arduino_instance, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'AutoStaticBias'):
			autoBiasScript.run(parameters, smu_default_instance, arduino_instance, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'AFMControl'):
			afmControlScript.run(parameters, smu_systems, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'SGMControl'):
			sgmControlScript.run(parameters, smu_systems, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'Delay'):
			delayScript.run(parameters, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'InverterSweep'):
			inverterSweepScript.run(parameters, smu_systems, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'RapidBias'):
			rapidBiasScript.run(parameters, smu_default_instance, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'NoiseCollection'):
			noiseCollectionScript.run(parameters, smu_default_instance, communication_pipe=communication_pipe)
		elif(parameters['runType'] == 'NoiseGrid'):
			noiseGridScript.run(parameters, smu_default_instance, communication_pipe=communication_pipe)
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



# === SMU Connection ===
def initMeasurementSystems(parameters):
	"""Given the parameters for running an experiment, sets up a connection to the necessary SMU or SMUs."""
	
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
	"""Given the parameters for running an experiment, sets up a connection to the (usually optional) Arduino."""
	
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
	


