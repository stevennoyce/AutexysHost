# === Imports ===
import time

import pipes
from procedures import Drain_Sweep as drainSweepScript
from utilities import DataLoggerUtility as dlu


# === Main ===
def run(parameters, smu_instance, arduino_instance, communication_pipe=None):
	# No setup required, just run
	runAutoDrainSweep(parameters, smu_instance, arduino_instance)	

def runAutoDrainSweep(parameters, smu_instance, arduino_instance, communication_pipe=None):
	ads_parameters = parameters['runConfigs']['AutoDrainSweep']

	# If no gate voltage set-point list given, use the set-point from the DrainSweep runConfig
	if(len(ads_parameters['gateVoltageSetPoints']) == 0):
		ads_parameters['gateVoltageSetPoints'] = [parameters['runConfigs']['DrainSweep']['gateVoltageSetPoint']]

	# Set up counters
	numberOfSweeps = len(ads_parameters['gateVoltageSetPoints'])*ads_parameters['sweepsPerVGS']
	sweepCount = 0
	startTime = time.time()
	
	# === START ===
	for i in range(len(ads_parameters['gateVoltageSetPoints'])):
		# Make copy of parameters to run GateSweep, but modify the Vgs setpoint
		drainSweepParameters = dict(parameters)
		drainSweepParameters['runType'] = 'DrainSweep'
		drainSweepParameters['runConfigs']['DrainSweep']['gateVoltageSetPoint'] = ads_parameters['gateVoltageSetPoints'][i]
		
		print('Sweep V_GS set to: ' + str(ads_parameters['gateVoltageSetPoints'][i]) + ' V.')
		
		for j in range(ads_parameters['sweepsPerVGS']):
			print('Starting sweep #'+str(sweepCount+1)+' of '+str(numberOfSweeps))
			drainSweepScript.run(drainSweepParameters, smu_instance, isSavingResults=True, isPlottingResults=False)
			print('Completed sweep #'+str(sweepCount+1)+' of '+str(numberOfSweeps))
			sweepCount += 1
			if(ads_parameters['timedSweepStarts']):
				print('Starting next sweep ' + str(ads_parameters['delayBetweenSweeps']) + ' seconds after start of current sweep...')
				waitDuration = startTime + ads_parameters['delayBetweenSweeps']*(sweepCount) - time.time()
				time.sleep(max(0, waitDuration))
			elif((ads_parameters['delayBetweenSweeps'] > 0) and (sweepCount < numberOfSweeps)):
				print('Waiting for ' + str(ads_parameters['delayBetweenSweeps']) + ' seconds...')
				time.sleep(ads_parameters['delayBetweenSweeps'])