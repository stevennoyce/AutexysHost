# === Imports ===
import pipes
from procedures import Burn_Out as burnOutScript
from procedures import Gate_Sweep as gateSweepScript
from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# Create distinct parameters for all scripts that could be run
	gateSweepParameters = dict(parameters)
	gateSweepParameters['runType'] = 'GateSweep'
	burnOutParameters = dict(parameters)
	burnOutParameters['runType'] = 'BurnOut'

	runAutoBurnOut(parameters, smu_systems, arduino_systems, gateSweepParameters, burnOutParameters, share=share)

def runAutoBurnOut(parameters, smu_systems, arduino_systems, gateSweepParameters, burnOutParameters, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]
	
	# Get shorthand name to easily refer to configuration parameters
	abo_parameters = parameters['runConfigs']['AutoBurnOut']

	targetOnOffRatio = abo_parameters['targetOnOffRatio']
	allowedDegradationFactor = abo_parameters['limitOnOffRatioDegradation']
	burnOutLimit = abo_parameters['limitBurnOutsAllowed']
	burnOutCount = 0

	# === START ===
	# Take an initial sweep to get a baseline for device performance
	print('Beginning AutoBurnOut with a target On/Off ratio of: '+str(abo_parameters['targetOnOffRatio']))
	print('Taking an initial sweep to get baseline performance of the device...')
	sweepResults = gateSweepScript.run(gateSweepParameters, smu_systems, arduino_systems, share=share)
	previousOnOffRatio = sweepResults['Computed']['onOffRatio']

	while((previousOnOffRatio < targetOnOffRatio) and (burnOutCount < burnOutLimit)):
		print('Starting burnout #'+str(burnOutCount+1))

		# Run BurnOut and GateSweep
		burnOutScript.run(burnOutParameters, smu_systems, arduino_systems, share=share)
		sweepResults = gateSweepScript.run(gateSweepParameters, smu_systems, arduino_systems, share=share)

		# If the On/Off ratio dropped by more than 'allowedDegredationFactor' stop BurnOut now
		currentOnOffRatio = sweepResults['Computed']['onOffRatio']
		if(currentOnOffRatio < allowedDegradationFactor*previousOnOffRatio):
			break
		previousOnOffRatio = currentOnOffRatio
		
		print('Completed sweep #'+str(burnOutCount+1))
		burnOutCount += 1
		
