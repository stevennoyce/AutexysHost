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
					delayBetweenSweeps=cs_parameters['delayBetweenSweeps'],
					timedSweepStarts=cs_parameters['timedSweepStarts'],
					share=share)	
	# === COMPLETE ===
	
	# Copy parameters and save data structure that tracks the experiments of every device
	jsonData = dict(parameters)
	jsonData['Results'] = {'deviceIndexes':deviceIndexes}

	# Save results as a JSON object
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), cs_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))

	return jsonData

def runChipSweep(parameters, smu_systems, arduino_systems, deviceIndexes, sweepType, devices, sweepsPerDevice, delayBetweenDevices, delayBetweenSweeps, timedSweepStarts, share=None):	
	# Set up counters
	numberOfDevices = len(devices)
	numberOfSweeps = len(devices)*sweepsPerDevice
	sweepCount = 0
	startTime = time.time()
	
	# Send initial progress update
	pipes.progressUpdate(share, 'Sweep', start=0, current=0, end=sweepsPerDevice, barType='Sweep')
	pipes.progressUpdate(share, 'Device', start=0, current=0, end=numberOfDevices, barType='Group')
	
	for sweep_index in range(sweepsPerDevice):
		# Sweep all devices in this chip sweep.
		for device_index in range(len(devices)):
			# Choose next device to sweep from the list
			device = devices[device_index]
			
			# Make copy of parameters to run Sweep, adjusting relevant device-specific properties
			sweepParameters = copy.deepcopy(parameters)
			sweepParameters['Identifiers']['device'] = device
			sweepParameters['startIndexes'] = deviceIndexes[device]
			
			print('Starting sweep #'+str(sweepCount+1)+' of '+str(numberOfSweeps))
			
			# Set the SMU to the device that is about to be tested
			for smu_name, smu_instance in smu_systems.items():
				smu_instance.setDevice(device)
			
			print('Switched to device: "' + str(device) + '".')
			
			# Run sweep
			if(sweepType == 'DrainSweep'):
				sweepParameters['runType'] = 'DrainSweep'
				jsonData = drainSweepScript.run(sweepParameters, smu_systems, arduino_systems, share=share)
			else:
				sweepParameters['runType'] = 'GateSweep'
				jsonData = gateSweepScript.run(sweepParameters, smu_systems, arduino_systems, share=share)
			
			print('Completed sweep #'+str(sweepCount+1)+' of '+str(numberOfSweeps))
			sweepCount += 1
			
			# Send progress update
			pipes.progressUpdate(share, 'Device', start=0, current=device_index+1, end=numberOfDevices, barType='Group')
			
			# If desired, delay before moving on to the next device
			if(sweepCount < numberOfSweeps):
				if(delayBetweenDevices > 0):
					print('Waiting for ' + str(delayBetweenDevices) + ' seconds...')
					time.sleep(delayBetweenDevices)
		
		# Send progress update
		pipes.progressUpdate(share, 'Sweep', start=0, current=sweep_index+1, end=sweepsPerDevice, barType='Sweep')
		
		# If desired, delay until next sweep should start.	
		if(sweepCount < numberOfSweeps):
			if(delayBetweenSweeps > 0):
				if(timedSweepStarts):
					print('Starting next sweep ' + str(delayBetweenSweeps) + ' seconds after start of current sweep...')
					waitDuration = startTime + delayBetweenSweeps*sweepCount - time.time()
					time.sleep(max(0, waitDuration))
				else:
					print('Waiting for ' + str(delayBetweenSweeps) + ' seconds...')
					time.sleep(delayBetweenSweeps)
		
				
				