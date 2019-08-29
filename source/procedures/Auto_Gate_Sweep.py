# === Imports ===
import time

import pipes
from procedures import Gate_Sweep as gateSweepScript
from utilities import DataLoggerUtility as dlu


# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# No setup required, just run
	runAutoGateSweep(parameters, smu_systems, arduino_systems, share=share)	

def runAutoGateSweep(parameters, smu_systems, arduino_systems, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]
	
	# Get shorthand name to easily refer to configuration parameters
	ags_parameters = parameters['runConfigs']['AutoGateSweep']

	# If no drain voltage set-point list given, use the set-point from the GateSweep runConfig
	if(len(ags_parameters['drainVoltageSetPoints']) == 0):
		ags_parameters['drainVoltageSetPoints'] = [parameters['runConfigs']['GateSweep']['drainVoltageSetPoint']]

	# Set up counters
	numberOfSweeps = len(ags_parameters['drainVoltageSetPoints'])*ags_parameters['sweepsPerVDS']
	sweepCount = 0
	startTime = time.time()
	
	# Send initial progress update
	pipes.progressUpdate(share, 'Sweep', start=0, current=sweepCount, end=numberOfSweeps)
	
	# === START ===
	for i in range(len(ags_parameters['drainVoltageSetPoints'])):
		# Make copy of parameters to run GateSweep, but modify the Vds setpoint
		gateSweepParameters = dict(parameters)
		gateSweepParameters['runType'] = 'GateSweep'
		gateSweepParameters['runConfigs']['GateSweep']['drainVoltageSetPoint'] = ags_parameters['drainVoltageSetPoints'][i]
		print('Sweep V_DS set to: ' + str(ags_parameters['drainVoltageSetPoints'][i]) + ' V.')
		
		for j in range(ags_parameters['sweepsPerVDS']):
			# Run sweep
			print('Starting sweep #'+str(sweepCount+1)+' of '+str(numberOfSweeps))
			gateSweepScript.run(gateSweepParameters, smu_systems, arduino_systems, share=share)
			print('Completed sweep #'+str(sweepCount+1)+' of '+str(numberOfSweeps))
			sweepCount += 1
			
			# Send progress update
			pipes.progressUpdate(share, 'Sweep', start=0, current=sweepCount, end=numberOfSweeps)
			
			# If desired, delay until next sweep should start
			if(ags_parameters['timedSweepStarts']):
				print('Starting next sweep ' + str(ags_parameters['delayBetweenSweeps']) + ' seconds after start of current sweep...')
				waitDuration = startTime + ags_parameters['delayBetweenSweeps']*(sweepCount) - time.time()
				time.sleep(max(0, waitDuration))
			elif((ags_parameters['delayBetweenSweeps'] > 0) and (sweepCount <= numberOfSweeps)):
				print('Waiting for ' + str(ags_parameters['delayBetweenSweeps']) + ' seconds...')
				time.sleep(ags_parameters['delayBetweenSweeps'])
				
				