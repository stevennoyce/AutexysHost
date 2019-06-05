# === Imports ===
import time
import numpy as np

from procedures import Noise_Collection as noiseCollectionScript
from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_instance, isSavingResults=True, isPlottingResults=False, communication_pipe=None):
	# No setup required, just run
	runNoiseGrid(parameters, smu_instance)	
	
def runNoiseGrid(parameters, smu_instance, communication_pipe=None):
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
	
	# === START ===
	for gateVoltage in ng_parameters['gateVoltages']:
		for drainVoltage in ng_parameters['drainVoltages']:
			# Make copy of parameters to run NoiseCollection, but modify the setpoints
			noiseCollectionParameters = dict(parameters)
			noiseCollectionParameters['runType'] = 'NoiseCollection'
			noiseCollectionParameters['runConfigs']['NoiseCollection']['gateVoltage'] = gateVoltage
			noiseCollectionParameters['runConfigs']['NoiseCollection']['drainVoltage'] = drainVoltage
			print('V_GS set to: ' + str(gateVoltage) + ' V.')
			print('V_DS set to: ' + str(drainVoltage) + ' V.')
			
			# === Run ===
			print('Starting noise collection #'+str(count+1)+' of '+str(numberOfNoiseCollections))
			noiseCollectionScript.run(noiseCollectionParameters, smu_instance, isSavingResults=True, isPlottingResults=False)
			print('Completed noise collection #'+str(count+1)+' of '+str(numberOfNoiseCollections))
			count += 1
			
			# Delay if groundingTime > 0
			if((ng_parameters['groundingTime'] > 0) and (count < numberOfNoiseCollections)):
				print('Waiting for ' + str(ng_parameters['groundingTime']) + ' seconds...')
				time.sleep(ng_parameters['groundingTime'])


	