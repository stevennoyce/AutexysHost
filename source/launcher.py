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
def run(additional_parameters, workspace_data_path=None, share=None):
	"""Begins execution of an experiment whose parameters are defined by the union of addition_parameters and defaults.py.
	Also initializes a connection to the necessary SMU systems and/or Arduino systems needed to perform the experiment."""
	
	startTime = time.time()
	
	# === Load Defaults ===
	parameters = defaults.with_added(additional_parameters)

	# if workspace_data_path was specified, use that as the data folder for this procedure (instead of the value loaded from defaults.py)
	parameters['dataFolder'] = workspace_data_path   if(workspace_data_path is not None)            else parameters['dataFolder']

	# additional_parameters is required to specify valid user, project, wafer, chip, device
	placeholder_identifiers = defaults.identifiers()
	parameters['Identifiers']['user']    = placeholder_identifiers['user']    if(parameters['Identifiers']['user']    == '') else parameters['Identifiers']['user']
	parameters['Identifiers']['project'] = placeholder_identifiers['project'] if(parameters['Identifiers']['project'] == '') else parameters['Identifiers']['project']
	parameters['Identifiers']['wafer']   = placeholder_identifiers['wafer']   if(parameters['Identifiers']['wafer']   == '') else parameters['Identifiers']['wafer']
	parameters['Identifiers']['chip']    = placeholder_identifiers['chip']    if(parameters['Identifiers']['chip']    == '') else parameters['Identifiers']['chip']
	parameters['Identifiers']['device']  = placeholder_identifiers['device']  if(parameters['Identifiers']['device']  == '') else parameters['Identifiers']['device']

	# Make an explicit flag in the data noting the original 'runType' of the procedure since this can be changed over the course of the experiment
	parameters['originalRunType'] = parameters['runType']

	# Extract relevant system configuration information from SourceMeasureUnit.py
	parameters['MeasurementSystem']['systems'] = smu.getSystemConfiguration(parameters['MeasurementSystem']['systemType'])

	# === SMU  ===
	# Initialize measurement system
	smu_systems = initializeMeasurementSystems(parameters)		

	# Initialize Arduino connection
	arduino_systems = initializeArduino(parameters)
	print("Sensor data: " + str(parameters['SensorData']))
	
	# === Start ===
	startProcedure(parameters, smu_systems, arduino_systems, share=share)
	# === Complete ===
	
	# Print finishing message noting how long this job took to run
	print('Completed job in "' + '{:.4f}'.format(time.time() - startTime) + '" seconds.')



# === Internal API ===
def startProcedure(parameters, smu_systems, arduino_systems, share=None):
	"""Determines if this procedure should run in normal or DeviceCycling mode. Also does the setup, error handling, and clean up
	for the procedure."""
	
	# === Cycling ===
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
	
	# === Setup ===
	# Begin a new experiment and set up data saving for each target device
	deviceIndexes = setUpDataSaving(parameters, target_devices)
	
	# === Run Procedure ===
	try:
		pipes.checkAbortStatus(share)
		runProcedure(parameters, smu_systems, arduino_systems, deviceIndexes, target_devices, cycles=procedure_cycles, delay_between_devices=delay_between_devices, delay_between_cycles=delay_between_cycles, timed_cycles=timed_cycles, share=share)
	except pipes.AbortError as e:
		print("ABORT. Launcher received abort: " + str(e))
	except:
		# In case of a general procedure error, still try to ramp down SMU voltages, then disconnect
		for smu_name, smu_instance in smu_systems.items():
			smu_instance.rampDownVoltages()
			smu_instance.disconnect()

		# Save data files to mark this experiment as ended before exiting
		cleanUpDataSaving(parameters, target_devices, deviceIndexes)
		
		print('ERROR: Exception raised during the experiment.')
		raise
	# === Procedure Complete ===
	
	# Make sure to ramp down all SMU voltages now that the procedure has finished
	for smu_name, smu_instance in smu_systems.items():
		smu_instance.rampDownVoltages()
	
	# Save data files to mark this experiment as complete
	cleanUpDataSaving(parameters, target_devices, deviceIndexes)
	print('Procedure complete.')



def runProcedure(parameters, smu_systems, arduino_systems, deviceIndexes, target_devices, cycles=1, delay_between_devices=0, delay_between_cycles=0, timed_cycles=False, share=None):
	"""Runs the procedure specified in parameters, and iterates over many cycles if desired"""
	
	# Find all procedures defined in the 'procedures' sub-directory
	procedureDefinitions = explicitlyInitializeProcedures()	
	
	# Determine if any cycling is set to occur
	is_cycling = (cycles > 1) or (len(target_devices) > 1)
	
	# If any cycling will occur, notify the UI
	if(is_cycling):
		pipes.progressUpdate(share, 'Cycle', start=0, current=0, end=cycles, barType='Group1', enableAbort=True)
		print('Device Cycling is beginning.')
	
	# Mark the start of this procedure
	startTime = time.time()
	
	# Repeat the procedure 'cycles' number of times
	for cycle_index in range(cycles):
		# Cycle through all target devices	
		for device_index in range(len(target_devices)):
			device = target_devices[device_index]
			
			# Send the UI an initial notification before the first device starts. Also resets this progress bar for each new cycle.
			if(is_cycling and (device_index == 0)):
				pipes.progressUpdate(share, 'Device', start=0, current=0, end=len(target_devices), barType='Group2', enableAbort=True)
			
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
			procedureDefinitions[deviceParameters['runType']]['function'](deviceParameters, smu_systems, arduino_systems, share=share)	
			# === Procedure Complete ===
			
			# Send device progress update
			if(is_cycling):
				pipes.progressUpdate(share, 'Device', start=0, current=(device_index+1), end=len(target_devices), barType='Group2', enableAbort=True)
				
			
			# If desired, delay before moving on to the next device
			if(device_index < len(target_devices)-1):
				if(delay_between_devices > 0):
					print('Waiting for ' + str(delay_between_devices) + ' seconds, before switching to next device...')
					time.sleep(delay_between_devices)
		
		# Send cycle progress update
		if(is_cycling):
			pipes.progressUpdate(share, 'Cycle', start=0, current=(cycle_index+1), end=cycles, barType='Group1', enableAbort=True)
			
		# If desired, delay until next cycle should start.	
		if(cycle_index < cycles-1):
			if(delay_between_cycles > 0):
				wait_duration = (delay_between_cycles) if(not timed_cycles) else ((startTime + delay_between_cycles*(cycle_index+1)) - time.time())
				print('Waiting for ' + str(wait_duration) + ' seconds, before beginning next cycle...')
				time.sleep(max(0, wait_duration))	
	
	

def setUpDataSaving(parameters, target_devices):
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
	
	# If multiple devices were involved in this procedure, we need an additional file to be saved to track this
	if(len(target_devices) > 1):
		# Avoid modifying the original parameters
		cyclingParameters = copy.deepcopy(parameters)
		cyclingParameters['Identifiers']['device'] = 'DeviceCycling'
		
		# This is the key information we need to recover later in order to find all of the data from this multi-device procedure
		cyclingParameters['DeviceCycling']['deviceIndexes'] = deviceIndexes
		
		# Set up save folder + indexing system for this additonal file
		dlu.makeFolder(dlu.getDeviceDirectory(cyclingParameters))
		dlu.incrementJSONExperimentNumber(dlu.getDeviceDirectory(cyclingParameters))
		indexes = dlu.loadJSONIndex(dlu.getDeviceDirectory(cyclingParameters))
		cyclingParameters['startIndexes'] = indexes
		cyclingParameters['startIndexes']['timestamp'] = endTime
		cyclingParameters['endIndexes']   = indexes
		cyclingParameters['endIndexes']['timestamp']   = endTime
		
		# Save an additional file that contains information about all of the devices just involved in the last experiment
		print('Saving to DeviceCycling...')
		dlu.saveJSON(dlu.getDeviceDirectory(cyclingParameters), 'DeviceCycling', cyclingParameters, subDirectory='Ex'+str(cyclingParameters['startIndexes']['experimentNumber']))
		dlu.saveJSON(dlu.getDeviceDirectory(cyclingParameters), 'ParametersHistory', cyclingParameters, incrementIndex=False)
		


# === SMU Connection ===
def initializeMeasurementSystems(parameters):
	"""Given the parameters for running an experiment, sets up a connection to the necessary SMU or SMUs."""
	
	smu_systems = {}
	
	for system_name,system_info in parameters['MeasurementSystem']['systems'].items():
		system_id = system_info['uniqueID']
		system_type = system_info['type']
		system_settings = system_info['settings']
		
		# Handle connection to each possible system type
		if(system_type == 'Automatic'):
			try:
				smu_systems[system_name] = smu.getConnectionToPCB(port=system_id, baud=115200, system_settings=system_settings)
			except:
				smu_systems[system_name] = smu.getConnectionToVisaResource(system_id, system_settings, defaultComplianceCurrent=100e-6, smuTimeout=60*1000)
		elif(system_type == 'B2912A'):
			smu_systems[system_name] = smu.getConnectionToVisaResource(system_id, system_settings, defaultComplianceCurrent=100e-6, smuTimeout=60*1000)
		elif(system_type == 'PCB_System'):
			smu_systems[system_name] = smu.getConnectionToPCB(port=system_id, baud=115200, system_settings=system_settings)
		elif(system_type == 'Emulator_System'):
			smu_systems[system_name] = smu.getConnectionToEmulator()
		elif(system_type == 'Arduino_System'):
			print('Arduino system detected. Connection will be handled separately.')
			continue
		else:
			raise NotImplementedError("Unkown Measurement System specified (try B2912A, PCB_System, ...)")
		
		# Print connection success message
		print("Connected to " + str(system_type) + " system '" + str(system_name) + "', with ID: " + str(smu_systems[system_name].system_id))
	
	return smu_systems



# === Arduino Connection ===
def initializeArduino(parameters):
	"""Given the parameters for running an experiment, sets up a connection to the (usually optional) Arduino."""
	
	arduino_systems = {}
	
	for system_name,system_info in parameters['MeasurementSystem']['systems'].items():
		system_id = system_info['uniqueID']
		system_type = system_info['type']
		system_settings = system_info['settings']
		
		# Only handle connections of type 'Arduino_System'
		if(system_type == 'Arduino_System'):
			arduino_systems[system_name] = arduinoBoard.getConnection(port=system_id, baud=9600, system_settings=system_settings)
	
	# If no specific Arduino_System was specified in configuration, still check to see if any are available to connect 
	if(len(arduino_systems.keys()) == 0):	
		arduino_systems = {'MCU': arduinoBoard.getConnection(port='', baud=9600)}
	
	#for arduino_reference in arduino_systems:
	#	sensor_data = arduino_reference.takeMeasurement()
	#	for (measurement, value) in sensor_data.items():
	#		parameters['SensorData'][measurement] = [value]
	
	return arduino_systems
	
	
	
# === Load Procedures ===	
from procedures import Gate_Sweep
from procedures import Drain_Sweep
from procedures import Free_Run

from procedures import Static_Bias
from procedures import Rapid_Bias
from procedures import Small_Signal

from procedures import Auto_Gate_Sweep
from procedures import Auto_Drain_Sweep
from procedures import Auto_Static_Bias

from procedures import Noise_Collection
from procedures import Noise_Grid

from procedures import Inverter_Sweep
from procedures import Inverter_Bias
from procedures import AFM_Control
from procedures import SGM_Control
from procedures import Flow_Static_Bias
from procedures import Auto_Flow_Static_Bias
from procedures import Burn_Out
from procedures import Auto_Burn_Out
from procedures import Delay
from procedures import PT_Sensor

def explicitlyInitializeProcedures():	
	basic_procedures = [
		['GateSweep',  Gate_Sweep],
		['DrainSweep', Drain_Sweep],
		['FreeRun',    Free_Run],
	]
	
	timed_procedures = [
		['StaticBias', Static_Bias],
		['RapidBias',  Rapid_Bias],
		['SmallSignal', Small_Signal],
	]
	
	repeated_procedures = [
		['AutoGateSweep',  Auto_Gate_Sweep],
		['AutoDrainSweep', Auto_Drain_Sweep],
		['AutoStaticBias', Auto_Static_Bias],
	]
	
	noise_procedures = [
		['NoiseCollection', Noise_Collection],
		['NoiseGrid',       Noise_Grid],
	]
	
	specialized_procedures = [
		['InverterSweep', Inverter_Sweep],
		['InverterBias',  Inverter_Bias],
		['AFMControl',    AFM_Control],
		['SGMControl',    SGM_Control],
		['FlowStaticBias',     Flow_Static_Bias],
		['AutoFlowStaticBias', Auto_Flow_Static_Bias],
		['BurnOut',       Burn_Out],
		['AutoBurnOut',   Auto_Burn_Out],
		['Delay',         Delay],
		['PTSensor',      PT_Sensor],
	]
	
	enabledProcedures = []
	enabledProcedures.extend(basic_procedures)
	enabledProcedures.extend(timed_procedures)
	enabledProcedures.extend(repeated_procedures)
	enabledProcedures.extend(noise_procedures)
	enabledProcedures.extend(specialized_procedures)
	
	procedureDefinitions = {}
	for (procedureCommonName, procedureModule) in enabledProcedures:
		procedureDefinitions[procedureCommonName] = {}
		procedureDefinitions[procedureCommonName]['module'] = procedureModule
		procedureDefinitions[procedureCommonName]['function'] = procedureModule.run

	return procedureDefinitions
	


### DEPRECATED ###
def dynamicallyInitializeProcedures():
	# Import all Procedure Definitions and save a reference to run their 'run' function
	procedureDefinitions = {}
	procedureDefinitionsBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'procedures/') if(not getattr(sys, 'frozen', False)) else (os.path.join(sys._MEIPASS, 'procedures/'))
	
	for importer, packageName, isPackage in pkgutil.iter_modules([procedureDefinitionsBasePath] + glob.glob(procedureDefinitionsBasePath + '/*/')):
		module = importer.find_module(packageName).load_module(packageName)
		packageCommonName = packageName.replace('_','')
		procedureDefinitions[packageCommonName] = {}
		procedureDefinitions[packageCommonName]['module'] = module
		procedureDefinitions[packageCommonName]['function'] = module.run

	return procedureDefinitions
	
	
	
	


