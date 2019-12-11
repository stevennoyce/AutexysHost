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

import glob
import pkgutil

from utilities import DataLoggerUtility as dlu
from drivers import SourceMeasureUnit as smu
from drivers import ArduinoBoard as arduinoBoard

import defaults
import pipes



# === Main API ===
def run(additional_parameters, share=None):
	"""Begins execution of an experiment whose parameters are defined by the union of addition_parameters and defaults.py.
	Also initializes a connection to the necessary SMU systems and/or Arduino systems needed to perform the experiment."""
	
	startTime = time.time()
	
	parameters = defaults.with_added(additional_parameters)

	# additional_parameters is required to specify valid user, project, wafer, chip, device
	parameters['Identifiers']['user']    = 'guest'   if(parameters['Identifiers']['user']    == '') else parameters['Identifiers']['user']
	parameters['Identifiers']['project'] = 'Project' if(parameters['Identifiers']['project'] == '') else parameters['Identifiers']['project']
	parameters['Identifiers']['wafer']   = 'Wafer'   if(parameters['Identifiers']['wafer']   == '') else parameters['Identifiers']['wafer']
	parameters['Identifiers']['chip']    = 'Chip'    if(parameters['Identifiers']['chip']    == '') else parameters['Identifiers']['chip']
	parameters['Identifiers']['device']  = 'Device'  if(parameters['Identifiers']['device']  == '') else parameters['Identifiers']['device']

	# Make an explicit flag in the data noting the original 'runType' of the procedure since this can be changed over the course of the experiment
	parameters['originalRunType'] = parameters['runType']

	# Initialize measurement system
	smu_systems = initializeMeasurementSystems(parameters)		

	# Initialize Arduino connection
	arduino_systems = initializeArduino(parameters)
	print("Sensor data: " + str(parameters['SensorData']))
	
	# Initialize list of device we plan to measure
	device_cycle_default = [str(x) + '-' + str(x+1) for x in range(1, 64)]
	device_cycle = device_cycle_default if((parameters['MeasurementSystem']['specificDeviceRange'] is None) or (len(parameters['MeasurementSystem']['specificDeviceRange']) == 0)) else parameters['MeasurementSystem']['specificDeviceRange']
	target_devices = [parameters['Identifiers']['device']] if(not parameters['MeasurementSystem']['deviceCycling']) else (device_cycle)
	
	# Run specified procedure
	runProcedure(parameters, additional_parameters, target_devices, smu_systems, arduino_systems, share=share)
	
	# Print finishing message noting how long this job took to run
	endTime = time.time()
	print('Completed job in "' + '{:.4f}'.format(endTime - startTime) + '" seconds.')



# === Internal API ===
def runProcedure(parameters, schedule_parameters, target_devices, smu_systems, arduino_systems, share=None):
	"""Prepares the file system for the upcoming experiment and selects a Procedure to carry out the experiment.
	In the event of an error during any procedure, this function is responsible for emergency ramping down the
	SMU voltages and exiting as gracefully as possible."""
	
	# Find all procedures defined in the 'procedures' sub-directory
	procedureDefinitions = initializeProcedures()	
	
	# Begin a new experiment and setup data saving for all target devices
	deviceIndexes = setUpDataSaving(parameters, schedule_parameters, target_devices)
		
	for device in target_devices:
		# Print the experiment start message
		print('About to begin experiment #' + str(deviceIndexes[device]['experimentNumber']) + ' for device ' + str(parameters['Identifiers']['wafer']) + str(parameters['Identifiers']['chip']) + ':' + str(device))
	
		# Make copy of parameters to run Procedure, adjusting relevant device-specific properties
		deviceParameters = copy.deepcopy(parameters)
		deviceParameters['Identifiers']['device'] = device
		deviceParameters['startIndexes'] = deviceIndexes[device]	
	
		# Set the SMUs to the device that is about to be tested
		for smu_name, smu_instance in smu_systems.items():
			smu_instance.setDevice(device)
	
		# Notify the UI that a new device is about to be tested
		pipes.deviceNumberUpdate(share, device)
	
		# === Run Procedure ===
		try:
			procedureDefinitions[deviceParameters['runType']]['function'](deviceParameters, smu_systems, arduino_systems, share=share)
		except Exception as e:
			# In case of an error, still try to ramp down SMU voltages, then disconnect
			for smu_name, smu_instance in smu_systems.items():
				smu_instance.rampDownVoltages()
				smu_instance.disconnect()
	
			# Save data files to mark this experiment as ended before exiting
			cleanUpDataSaving(parameters, target_devices, deviceIndexes)
			
			print('ERROR: Exception raised during the experiment.')
			raise
		# === Complete ===
	
	# Make sure to ramp down all SMU voltages now that the procedure has finished
	for smu_name, smu_instance in smu_systems.items():
		smu_instance.rampDownVoltages()
	
	# Save data files to mark this experiment as complete
	cleanUpDataSaving(parameters, target_devices, deviceIndexes)
	print('Procedure complete.')



def setUpDataSaving(parameters, schedule_parameters, target_devices):
	"""This function runs at the beginning of a procedure to set up all data structures needed to save data properly."""
	
	deviceIndexes = {}
	
	# Save a single starting timestamp for all target devices
	startTime = time.time()
	
	# Initialize saving data structures for all devices
	for device in target_devices:
		# Avoid modifying the original parameters
		deviceParameters = copy.deepcopy(parameters)
		deviceParameters['Identifiers']['device'] = device
		
		# Make sure that the data save folder exists before beginning
		print('Checking that save folder exists.')
		dlu.makeFolder(dlu.getDeviceDirectory(deviceParameters))
		
		# Save un-modified schedule file entry to 'SchedulesHistory'
		print('Saving to SchedulesHistory...')
		dlu.saveJSON(dlu.getDeviceDirectory(deviceParameters), 'SchedulesHistory', schedule_parameters, incrementIndex=False)
		
		# Start a new experiment for each device
		dlu.incrementJSONExperimentNumber(dlu.getDeviceDirectory(deviceParameters))
		
		# Store information about the start of this experiment for each device
		deviceIndexes[device] = dlu.loadJSONIndex(dlu.getDeviceDirectory(deviceParameters))
		deviceIndexes[device]['timestamp'] = startTime
	
	return deviceIndexes



def cleanUpDataSaving(parameters, target_devices, deviceIndexes):
	"""This function runs at the end of a procedure to tie off loose ends and return the system to a safe state."""
	
	# Save a single ending timestamp for all target devices
	endTime = time.time()
	
	# Clean up saving data structures for all devices
	for device in target_devices:
		# Avoid modifying the original parameters
		deviceParameters = copy.deepcopy(parameters)
		deviceParameters['Identifiers']['device'] = device
		
		# Store information about the start and end of this experiment
		deviceParameters['startIndexes'] = 	deviceIndexes[device]
		deviceParameters['endIndexes'] = dlu.loadJSONIndex(dlu.getDeviceDirectory(deviceParameters))
		deviceParameters['endIndexes']['timestamp'] = endTime
		
		# Save finished result to 'ParametersHistory' file
		print('Saving to ParametersHistory...')
		dlu.saveJSON(dlu.getDeviceDirectory(deviceParameters), 'ParametersHistory', deviceParameters, incrementIndex=False)



# === SMU Connection ===
def initializeMeasurementSystems(parameters):
	"""Given the parameters for running an experiment, sets up a connection to the necessary SMU or SMUs."""
	
	system_instances = {}
	parameters['MeasurementSystem']['systems'] = smu.getSystemConfiguration(parameters['MeasurementSystem']['systemType'])
	for system_name,system_info in parameters['MeasurementSystem']['systems'].items():
		system_id = system_info['uniqueID']
		system_type = system_info['type']
		system_settings = system_info['settings']
		if(system_type == 'B2912A'):
			system_instances[system_name] = smu.getConnectionToVisaResource(system_id, system_settings, defaultComplianceCurrent=100e-6, smuTimeout=60*1000)
		elif(system_type == 'PCB_System'):
			system_instances[system_name] = smu.getConnectionToPCB(system_id, system_settings)
		elif(system_type == 'Emulator_System'):
			system_instances[system_name] = smu.getConnectionToEmulator()
		else:
			raise NotImplementedError("Unkown Measurement System specified (try B2912A, PCB_System, ...)")
		system_id = system_instances[system_name].system_id
		print("Connected to " + str(system_type) + " system '" + str(system_name) + "', with ID: " + str(system_id))
	return system_instances



# === Arduino Connection ===
def initializeArduino(parameters):
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
			arduino_instance = arduinoBoard.getNullInstance()
	sensor_data = arduino_instance.takeMeasurement()
	for (measurement, value) in sensor_data.items():
		parameters['SensorData'][measurement] = [value]
		
	arduino_systems = {'Arduino': arduino_instance}
	return arduino_systems
	
	
	
# === Load Procedures ===	
def initializeProcedures():
	# Import all Procedure Definitions and save a reference to run their 'run' function
	procedureDefinitions = {}
	procedureDefinitionsBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'procedures')
	
	for importer, packageName, isPackage in pkgutil.iter_modules([procedureDefinitionsBasePath] + glob.glob(procedureDefinitionsBasePath + '/*/')):
		module = importer.find_module(packageName).load_module(packageName)
		packageCommonName = packageName.replace('_','')
		procedureDefinitions[packageCommonName] = {}
		procedureDefinitions[packageCommonName]['module'] = module
		procedureDefinitions[packageCommonName]['function'] = module.run

	return procedureDefinitions
	
	
	


