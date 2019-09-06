# === Imports ===
import random
import time

import pipes
from procedures import Gate_Sweep as gateSweepScript
from procedures import Static_Bias as staticBiasScript
from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# Create distinct parameters for all scripts that could be run
	gateSweepParameters = dict(parameters)
	gateSweepParameters['runType'] = 'GateSweep'
	staticBiasParameters = dict(parameters)
	staticBiasParameters['runType'] = 'StaticBias'

	runAutoStaticBias(parameters, smu_systems, arduino_systems, gateSweepParameters, staticBiasParameters, share=share)	

def runAutoStaticBias(parameters, smu_systems, arduino_systems, gateSweepParameters, staticBiasParameters, share=None):
	sb_parameters = staticBiasParameters['runConfigs']['StaticBias']
	asb_parameters = parameters['runConfigs']['AutoStaticBias']

	importantListLengths = [len(asb_parameters['biasTimeList']), len(asb_parameters['gateVoltageSetPointList']), len(asb_parameters['drainVoltageSetPointList']), len(asb_parameters['gateVoltageWhenDoneList']), len(asb_parameters['drainVoltageWhenDoneList']), len(asb_parameters['delayWhenDoneList'])]
	numberOfStaticBiases = max(asb_parameters['numberOfStaticBiases'], max(importantListLengths))
	
	# Build arrays of all parameters that could change over the course of any given experiement
	biasTimeList 				= asb_parameters['biasTimeList'] 				+ [sb_parameters['totalBiasTime']]       *(numberOfStaticBiases-len(asb_parameters['biasTimeList']))
	gateVoltageSetPointList 	= asb_parameters['gateVoltageSetPointList'] 	+ [sb_parameters['gateVoltageSetPoint']] *(numberOfStaticBiases-len(asb_parameters['gateVoltageSetPointList']))
	drainVoltageSetPointList 	= asb_parameters['drainVoltageSetPointList'] 	+ [sb_parameters['drainVoltageSetPoint']]*(numberOfStaticBiases-len(asb_parameters['drainVoltageSetPointList']))
	gateVoltageWhenDoneList 	= asb_parameters['gateVoltageWhenDoneList'] 	+ [sb_parameters['gateVoltageWhenDone']] *(numberOfStaticBiases-len(asb_parameters['gateVoltageWhenDoneList']))
	drainVoltageWhenDoneList 	= asb_parameters['drainVoltageWhenDoneList'] 	+ [sb_parameters['drainVoltageWhenDone']]*(numberOfStaticBiases-len(asb_parameters['drainVoltageWhenDoneList']))
	delayWhenDoneList 			= asb_parameters['delayWhenDoneList'] 			+ [sb_parameters['delayWhenDone']]	     *(numberOfStaticBiases-len(asb_parameters['delayWhenDoneList']))
	delayBeforeMeasurementsList = [sb_parameters['delayBeforeMeasurementsBegin']]*numberOfStaticBiases

	delayBeforeMeasurementsList[0] = asb_parameters['firstDelayBeforeMeasurementsBegin']
	


	## === START ===
	print('Beginning AutoStaticBias test with the following parameter lists:')
	print('Total Bias Times: {:} \n Gate Voltages:  {:} \n Drain Voltages:  {:} \n Gate Voltages between biases:  {:} \n Drain Voltages between biases:  {:} \n Delay Between Applying Voltages:  {:} \n Delay Before Measurements Begin:  {:}'.format(biasTimeList, gateVoltageSetPointList, drainVoltageSetPointList, gateVoltageWhenDoneList, drainVoltageWhenDoneList, delayWhenDoneList, delayBeforeMeasurementsList))
	
	# Run a pre-test gate sweep just to make sure everything looks good
	if(asb_parameters['doInitialGateSweep']):
		print('Taking an initial sweep to get a baseline of device performance prior to StaticBias...')
		gateSweepScript.run(gateSweepParameters, smu_systems, arduino_systems, share=share)

	# Run all Static Biases in this Experiment
	for i in range(numberOfStaticBiases):
		print('Starting static bias #'+str(i+1)+' of '+str(numberOfStaticBiases))
		
		# Get the parameters for this StaticBias from the pre-built arrays
		sb_parameters['totalBiasTime'] = biasTimeList[i]
		sb_parameters['gateVoltageSetPoint'] = gateVoltageSetPointList[i]
		sb_parameters['drainVoltageSetPoint'] = drainVoltageSetPointList[i]
		sb_parameters['gateVoltageWhenDone'] = gateVoltageWhenDoneList[i]
		sb_parameters['drainVoltageWhenDone'] = drainVoltageWhenDoneList[i]
		sb_parameters['delayWhenDone'] = delayWhenDoneList[i]
		sb_parameters['delayBeforeMeasurementsBegin'] = delayBeforeMeasurementsList[i]
		
		# Run StaticBias, GateSweep (if desired)
		if(asb_parameters['applyGateSweepBetweenBiases'] and asb_parameters['applyGateSweepBothBeforeAndAfter']):
			gateSweepScript.run(gateSweepParameters, smu_systems, arduino_systems, share=share)
		staticBiasScript.run(staticBiasParameters, smu_systems, arduino_systems, share=share)
		if(asb_parameters['applyGateSweepBetweenBiases']):
			gateSweepScript.run(gateSweepParameters, smu_systems, arduino_systems, share=share)

		print('Completed static bias #'+str(i+1)+' of '+str(numberOfStaticBiases))

		# Delay before doing the next StaticBias
		if((asb_parameters['delayBetweenBiases'] > 0) and (i+1 < numberOfStaticBiases)):
			print('Waiting for: ' + str(asb_parameters['delayBetweenBiases']) + ' seconds...')
			time.sleep(asb_parameters['delayBetweenBiases'])

		
		



