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
	
	# Initialize list of devices we plan to measure (defaults to the single device in 'Identifiers')
	target_devices = [parameters['Identifiers']['device']]
	
	# Initialize procedure cycling parameters (defaults to a single procedure run, with no addiitonal built-in delays)
	is_cycling = parameters['MeasurementSystem']['deviceCycling']
	procedure_cycles      = 1     if(not is_cycling) else parameters['DeviceCycling']['numberOfCycles']
	delay_between_devices = 0     if(not is_cycling) else parameters['DeviceCycling']['delayBetweenDevices']
	delay_between_cycles  = 0     if(not is_cycling) else parameters['DeviceCycling']['delayBetweenCycles']
	timed_cycles          = False if(not is_cycling) else parameters['DeviceCycling']['timedCycles']
	
	# If device cycling is enabled for this measurement system, modify the target devices to include all devices of interest
	if(is_cycling):
		# By default, it will measure all devices numbered 1 to 64 unless a specific range of devices was specifed
		device_cycle_specific = parameters['DeviceCycling']['specificDeviceRange']
		device_cycle_default = [str(x) + '-' + str(x+1) for x in range(1, 64)]
		target_devices = device_cycle_default if((device_cycle_specific is None) or (len(device_cycle_specific) == 0)) else device_cycle_specific		
	
	# Run specified procedure
	runProcedure(parameters, additional_parameters, smu_systems, arduino_systems, target_devices, cycles=procedure_cycles, delay_between_devices=delay_between_devices, delay_between_cycles=delay_between_cycles, timed_cycles=timed_cycles, share=share)
	
	# Print finishing message noting how long this job took to run
	endTime = time.time()
	print('Completed job in "' + '{:.4f}'.format(endTime - startTime) + '" seconds.')



# === Internal API ===
def runProcedure(parameters, schedule_parameters, smu_systems, arduino_systems, target_devices, cycles=1, delay_between_devices=0, delay_between_cycles=0, timed_cycles=False, share=None):
	"""Prepares the file system for the upcoming experiment and selects a Procedure to carry out the experiment.
	In the event of an error during any procedure, this function is responsible for emergency ramping down the
	SMU voltages and exiting as gracefully as possible."""
	
	# Find all procedures defined in the 'procedures' sub-directory
	procedureDefinitions = initializeProcedures()	
	
	# Begin a new experiment and setup data saving for all target devices
	deviceIndexes = setUpDataSaving(parameters, schedule_parameters, target_devices)
	
	# If any cycling will occur, notify the UI
	if((cycles > 1) or (len(target_devices) > 1)):
		pipes.progressUpdate(share, 'Cycle', start=0, current=0, end=cycles, barType='Group1')
		pipes.progressUpdate(share, 'Device', start=0, current=0, end=len(target_devices), barType='Group2')
		print('Device Cycling is beginning.')
	
	# Mark the start of this procedure
	startTime = time.time()
	
	# Repeat the procedure 'cycles' number of times
	for cycle_index in range(cycles):
		# Cycle through all target devices	
		for device_index in range(len(target_devices)):
			device = target_devices[device_index]
			
			# Print the experiment start message
			print('Running experiment #' + str(deviceIndexes[device]['experimentNumber']) + ' for device ' + str(parameters['Identifiers']['wafer']) + str(parameters['Identifiers']['chip']) + ':' + str(device))
		
			# Make copy of parameters to run this Procedure, adjusting relevant device-specific properties
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
			# === Procedure Complete ===
			
			# Send device progress update
			if((cycles > 1) or (len(target_devices) > 1)):
				pipes.progressUpdate(share, 'Device', start=0, current=(device_index+1), end=len(target_devices), barType='Group2')
			
			# If desired, delay before moving on to the next device
			if(device_index < len(target_devices)-1):
				if(delay_between_devices > 0):
					print('Waiting for ' + str(delay_between_devices) + ' seconds, before switching to next device...')
					time.sleep(delay_between_devices)
		
		# Send cycle progress update
		if((cycles > 1) or (len(target_devices) > 1)):
			pipes.progressUpdate(share, 'Cycle', start=0, current=(cycle_index+1), end=cycles, barType='Group1')
			
		# If desired, delay until next cycle should start.	
		if(cycle_index < cycles-1):
			if(delay_between_cycles > 0):
				wait_duration = (delay_between_devices) if(not timed_cycles) else ((startTime + delay_between_devices*cycle_index) - time.time())
				print('Waiting for ' + str(wait_duration) + ' seconds, before beginning next cycle...')
				time.sleep(max(0, wait_duration))
	
	# === all cycles complete ===
	
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
		dlu.makeFolder(dlu.getDeviceDirectory(deviceParameters))
		
		# Start a new experiment for each device
		dlu.incrementJSONExperimentNumber(dlu.getDeviceDirectory(deviceParameters))
		
		# Store information about the start of this experiment for each device
		deviceIndexes[device] = dlu.loadJSONIndex(dlu.getDeviceDirectory(deviceParameters))
		deviceIndexes[device]['timestamp'] = startTime
		
		# Print the experiment start message
		print('Set up experiment #' + str(deviceIndexes[device]['experimentNumber']) + ' for device ' + str(deviceParameters['Identifiers']['wafer']) + str(deviceParameters['Identifiers']['chip']) + ':' + str(device))
	
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
		
		# Save finished result to 'ParametersHistory' file for each device
		print('Saving to ParametersHistory...')
		dlu.saveJSON(dlu.getDeviceDirectory(deviceParameters), 'ParametersHistory', deviceParameters, incrementIndex=False)
	
	# If multiple devices were involved in this procedure, we need additional information to be saved in order to track this
	if(len(target_devices) > 1):
		# This file will be in a folder named for the procedure run
		chipParameters = copy.deepcopy(parameters)
		chipParameters['Identifiers']['device'] = chipParameters['runType']
		chipParameters['DeviceCycling']['deviceIndexes'] = deviceIndexes
		
		# Set up save folder + indexing system for this additonal file
		dlu.makeFolder(dlu.getDeviceDirectory(chipParameters))
		experiment = dlu.incrementJSONExperimentNumber(dlu.getDeviceDirectory(chipParameters))
		
		# Save an additional file that contains information about all of the devices just involved in the last experiment
		print('Saving to DeviceCycling...')
		dlu.saveJSON(dlu.getDeviceDirectory(chipParameters), 'DeviceCycling', chipParameters, subDirectory='Ex'+str(experiment))
	
		



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
	
	
	


