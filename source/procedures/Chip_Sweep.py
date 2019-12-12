# === Imports ===
import time
import copy

import pipes
from procedures import Gate_Sweep as gateSweepScript
from procedures import Drain_Sweep as drainSweepScript
from utilities import DataLoggerUtility as dlu


# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# Get shorthand name to easily refer to configuration parameters
	cs_parameters = parameters['runConfigs']['ChipSweep']
	
	# Make a data structure to track the experiment number for each device in this chip sweep
	deviceIndexes = {}
	
	# Make save folders and increment the experiment number for every device in this chip sweep
	print('Setting up save folders for all devices in this chip sweep.')
	for device in cs_parameters['devices']:
		deviceParameters = copy.deepcopy(parameters)
		deviceParameters['Identifiers']['device'] = device
		dlu.makeFolder(dlu.getDeviceDirectory(deviceParameters))
		dlu.incrementJSONExperimentNumber(dlu.getDeviceDirectory(deviceParameters))
		deviceIndexes[device] = dlu.loadJSONIndex(dlu.getDeviceDirectory(deviceParameters))
		deviceIndexes[device]['timestamp'] = parameters['startIndexes']['timestamp']
	
	# === START ===
	runChipSweep(	parameters, 
					smu_systems, 
					arduino_systems, 
					deviceIndexes=deviceIndexes, 
					sweepType=cs_parameters['sweepType'],
					devices=cs_parameters['devices'],
					sweepsPerDevice=cs_parameters['sweepsPerDevice'],
					delayBetweenDevices=cs_parameters['delayBetweenDevices'],
					delayBetweenCycles=cs_parameters['delayBetweenCycles'],
					timedCycles=cs_parameters['timedCycles'],
					share=share)	
	# === COMPLETE ===
	
	# Save to ParametersHistory for all devices in this chip sweep
	print('Saving ParametersHistory data for all devices...')
	endTime = time.time()
	for device in cs_parameters['devices']:
		deviceParameters = copy.deepcopy(parameters)
		deviceParameters['Identifiers']['device'] = device
		deviceParameters['runType'] = cs_parameters['sweepType']
		deviceParameters['startIndexes'] = deviceIndexes[device]
		deviceParameters['endIndexes'] = dlu.loadJSONIndex(dlu.getDeviceDirectory(deviceParameters))
		deviceParameters['endIndexes']['timestamp'] = endTime
		dlu.saveJSON(dlu.getDeviceDirectory(deviceParameters), 'ParametersHistory', deviceParameters, incrementIndex=False)
	
	# Copy parameters and save the data structure that tracks the experiments of every device
	jsonData = dict(parameters)
	jsonData['Results'] = {'deviceIndexes':deviceIndexes}

	# Save results as a JSON object
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), cs_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))

	return jsonData

def runChipSweep(parameters, smu_systems, arduino_systems, deviceIndexes, sweepType, devices, sweepsPerDevice, delayBetweenDevices, delayBetweenCycles, timedCycles, share=None):		
	# Set up counters
	numberOfDevices = len(devices)
	numberOfSweeps = len(devices)*sweepsPerDevice
	sweepCount = 0
	startTime = time.time()
	
	# Send initial progress update
	pipes.progressUpdate(share, 'Sweep', start=0, current=0, end=sweepsPerDevice, barType='Sweep')
	pipes.progressUpdate(share, 'Device', start=0, current=0, end=numberOfDevices, barType='Group1')
	
	for cycle_index in range(sweepsPerDevice):
		# Sweep all devices in this chip sweep.
		for device_index in range(len(devices)):
			# Choose next device to sweep from the list
			device = devices[device_index]
			
			# Make copy of parameters to run Sweep, adjusting relevant device-specific properties
			sweepParameters = copy.deepcopy(parameters)
			sweepParameters['Identifiers']['device'] = device
			sweepParameters['startIndexes'] = deviceIndexes[device]
			sweepParameters['runType'] = sweepType
			
			print('Starting sweep #'+str(sweepCount+1)+' of '+str(numberOfSweeps))
			
			# Set the SMU to the device that is about to be tested
			for smu_name, smu_instance in smu_systems.items():
				smu_instance.setDevice(device)
			
			print('Switched to device: "' + str(device) + '".')
			
			# Run sweep
			if(sweepType == 'GateSweep'):
				jsonData = gateSweepScript.run(sweepParameters, smu_systems, arduino_systems, share=share)
			elif(sweepType == 'DrainSweep'):
				jsonData = drainSweepScript.run(sweepParameters, smu_systems, arduino_systems, share=share)
			
			print('Completed sweep #'+str(sweepCount+1)+' of '+str(numberOfSweeps))
			sweepCount += 1
			
			# Send progress update
			pipes.progressUpdate(share, 'Device', start=0, current=device_index+1, end=numberOfDevices, barType='Group1')
			
			# If desired, delay before moving on to the next device
			if(sweepCount < numberOfSweeps):
				if(delayBetweenDevices > 0):
					print('Waiting for ' + str(delayBetweenDevices) + ' seconds...')
					time.sleep(delayBetweenDevices)
		
		# Send progress update
		pipes.progressUpdate(share, 'Cycle', start=0, current=cycle_index+1, end=sweepsPerDevice, barType='Sweep')
		
		# If desired, delay until next cycle should start.	
		if(sweepCount < numberOfSweeps):
			if(delayBetweenCycles > 0):
				if(timedCycles):
					print('Starting next sweep ' + str(delayBetweenCycles) + ' seconds after start of current sweep...')
					waitDuration = startTime + delayBetweenCycles*(cycle_index+1) - time.time()
					time.sleep(max(0, waitDuration))
				else:
					print('Waiting for ' + str(delayBetweenCycles) + ' seconds...')
					time.sleep(delayBetweenCycles)
		
				
				