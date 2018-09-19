# === Imports ===
import time

from procedures import Gate_Sweep as gateSweepScript
from utilities import DataLoggerUtility as dlu


# === Main ===
def run(parameters, smu_instance, arduino_instance):
	# No setup required, just run
	runAutoGateSweep(parameters, smu_instance, arduino_instance)	

def runAutoGateSweep(parameters, smu_instance, arduino_instance):
	ags_parameters = parameters['runConfigs']['AutoGateSweep']

	numberOfSweeps = len(ags_parameters['drainVoltageSetPoints'])*ags_parameters['sweepsPerVDS']
	sweepCount = 0
	startTime = time.time()
	
	# === START ===
	for i in range(len(ags_parameters['drainVoltageSetPoints'])):
		# Make copy of parameters to run GateSweep, but modify the Vds setpoint
		gateSweepParameters = dict(parameters)
		gateSweepParameters['runType'] = 'GateSweep'
		gateSweepParameters['runConfigs']['GateSweep']['drainVoltageSetPoint'] = ags_parameters['drainVoltageSetPoints'][i]
		
		print('Sweep V_DS set to: ' + str(ags_parameters['drainVoltageSetPoints'][i]) + ' V.')
		
		for j in range(ags_parameters['sweepsPerVDS']):
			print('Starting sweep #'+str(sweepCount+1)+' of '+str(numberOfSweeps))
			gateSweepScript.run(gateSweepParameters, smu_instance, isSavingResults=True, isPlottingResults=False)
			print('Completed sweep #'+str(sweepCount+1)+' of '+str(numberOfSweeps))
			sweepCount += 1
			if(ags_parameters['timedSweepStarts']):
				print('Starting next sweep ' + str(ags_parameters['delayBetweenSweeps']) + ' seconds after start of current sweep...')
				waitDuration = startTime + ags_parameters['delayBetweenSweeps']*(sweepCount) - time.time()
				time.sleep(waitDuration)
			elif((ags_parameters['delayBetweenSweeps'] > 0) and (sweepCount < numberOfSweeps)):
				print('Waiting for ' + str(ags_parameters['delayBetweenSweeps']) + ' seconds...')
				time.sleep(ags_parameters['delayBetweenSweeps'])

