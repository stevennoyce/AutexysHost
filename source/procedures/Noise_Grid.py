# === Imports ===
import time
import numpy as np

import pipes
from procedures import Noise_Collection as noiseCollectionScript
from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# No setup required, just run
	runNoiseGrid(parameters, smu_systems, arduino_systems, share=share)	
	
def runNoiseGrid(parameters, smu_systems, arduino_systems, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]
	
	# Get shorthand name to easily refer to configuration parameters
	ng_parameters = parameters['runConfigs']['NoiseGrid']

	# If no gate/drain voltage set-point list given, use the set-points from the NoiseCollection runConfig
	if(len(ng_parameters['drainVoltages']) == 0):
		ng_parameters['drainVoltages'] = [parameters['runConfigs']['NoiseCollection']['drainVoltage']]
	if(len(ng_parameters['gateVoltages']) == 0):
		ng_parameters['gateVoltages'] = [parameters['runConfigs']['NoiseCollection']['gateVoltage']]

	# Set up counters
	numberOfVGS = len(ng_parameters['gateVoltages'])
	numberOfVDS = len(ng_parameters['drainVoltages'])
	numberOfNoiseCollections = numberOfVGS*numberOfVDS
	count = 0
	startTime = time.time()

	numPoints = len(ng_parameters['gateVoltages']) * len(ng_parameters['drainVoltages'])
	currentPoint = 1

	print("Executing noise grid")

	# === START ===
	for gateVoltage in ng_parameters['gateVoltages']:
		for drainVoltage in ng_parameters['drainVoltages']:
			pipes.progressUpdate(share, 'Noise Grid Run', start=0, current=currentPoint, end=numPoints, barType="Sweep")

			# Make copy of parameters to run NoiseCollection, but modify the setpoints
			noiseCollectionParameters = dict(parameters)
			noiseCollectionParameters['runType'] = 'NoiseCollection'
			noiseCollectionParameters['runConfigs']['NoiseCollection']['gateVoltage'] = gateVoltage
			noiseCollectionParameters['runConfigs']['NoiseCollection']['drainVoltage'] = drainVoltage
			print('V_GS set to: ' + str(gateVoltage) + ' V.')
			print('V_DS set to: ' + str(drainVoltage) + ' V.')
			
			# === Run ===
			print('Starting noise collection #'+str(count+1)+' of '+str(numberOfNoiseCollections))
			noiseCollectionScript.run(noiseCollectionParameters, smu_systems, arduino_systems, share=share)
			print('Completed noise collection #'+str(count+1)+' of '+str(numberOfNoiseCollections))
			count += 1
			
			# Delay if groundingTime > 0
			if((ng_parameters['groundingTime'] > 0) and (count < numberOfNoiseCollections)):
				print('Waiting for ' + str(ng_parameters['groundingTime']) + ' seconds...')
				time.sleep(ng_parameters['groundingTime'])

			currentPoint+=1


	