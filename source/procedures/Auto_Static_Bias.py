# === Imports ===
import random
import time

from procedures import Gate_Sweep as gateSweepScript
from procedures import Static_Bias as staticBiasScript
from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_instance, arduino_instance, communication_pipe=None):
	# Create distinct parameters for all scripts that could be run
	gateSweepParameters = dict(parameters)
	gateSweepParameters['runType'] = 'GateSweep'

	staticBiasParameters = dict(parameters)
	staticBiasParameters['runType'] = 'StaticBias'

	runAutoStaticBias(parameters, smu_instance, arduino_instance, gateSweepParameters, staticBiasParameters)	

def runAutoStaticBias(parameters, smu_instance, arduino_instance, gateSweepParameters, staticBiasParameters, communication_pipe=None):
	sb_parameters = staticBiasParameters['runConfigs']['StaticBias']
	asb_parameters = parameters['runConfigs']['AutoStaticBias']

	numberOfStaticBiases = asb_parameters['numberOfStaticBiases']
	
	# Build arrays of all parameters that could change over the course of any given experiement
	biasTimeList 				= asb_parameters['biasTimeList'] if(len(asb_parameters['biasTimeList']) == numberOfStaticBiases) else ([sb_parameters['totalBiasTime']]*numberOfStaticBiases)
	gateVoltageSetPointList 	= [sb_parameters['gateVoltageSetPoint']]*numberOfStaticBiases
	drainVoltageSetPointList 	= [sb_parameters['drainVoltageSetPoint']]*numberOfStaticBiases
	gateVoltageWhenDoneList 	= [sb_parameters['gateVoltageWhenDone']]*numberOfStaticBiases
	drainVoltageWhenDoneList 	= [sb_parameters['drainVoltageWhenDone']]*numberOfStaticBiases
	delayWhenDoneList 			= [sb_parameters['delayWhenDone']]*numberOfStaticBiases
	delayBeforeMeasurementsList = [sb_parameters['delayBeforeMeasurementsBegin']]*numberOfStaticBiases

	# Modify parameter arrays so that they increment there values as desired
	currentIncrementNumber = 1
	for i in range(numberOfStaticBiases):
		if(i >= asb_parameters['numberOfBiasesBetweenIncrements']*currentIncrementNumber):
			currentIncrementNumber += 1
		gateVoltageSetPointList[i] 	+= asb_parameters['incrementStaticGateVoltage']*(currentIncrementNumber-1)
		drainVoltageSetPointList[i] += asb_parameters['incrementStaticDrainVoltage']*(currentIncrementNumber-1)
		gateVoltageWhenDoneList[i] 	+= asb_parameters['incrementGateVoltageWhenDone']*(currentIncrementNumber-1)
		drainVoltageWhenDoneList[i] += asb_parameters['incrementDrainVoltageWhenDone']*(currentIncrementNumber-1)
		delayWhenDoneList[i] 		+= asb_parameters['incrementDelayBeforeReapplyingVoltage']*(currentIncrementNumber-1)	
	delayBeforeMeasurementsList[0] = asb_parameters['firstDelayBeforeMeasurementsBegin']

	# Randomize the time spent grounding the terminals if desired
	if(asb_parameters['shuffleDelaysBeforeReapplyingVoltage']):
		random.shuffle(delayWhenDoneList)



	## === START ===
	print('Beginning AutoStaticBias test with the following parameter lists:')
	print('Total Bias Times: {:} \n Gate Voltages:  {:} \n Drain Voltages:  {:} \n Gate Voltages between biases:  {:} \n Drain Voltages between biases:  {:} \n Delay Between Applying Voltages:  {:} \n Delay Before Measurements Begin:  {:}'.format(biasTimeList, gateVoltageSetPointList, drainVoltageSetPointList, gateVoltageWhenDoneList, drainVoltageWhenDoneList, delayWhenDoneList, delayBeforeMeasurementsList))
	
	# Run a pre-test gate sweep just to make sure everything looks good
	if(asb_parameters['doInitialGateSweep']):
		print('Taking an initial sweep to get a baseline of device performance prior to StaticBias...')
		gateSweepScript.run(gateSweepParameters, smu_instance, isSavingResults=True, isPlottingResults=False)

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
			gateSweepScript.run(gateSweepParameters, smu_instance, isSavingResults=True, isPlottingResults=False)
		staticBiasScript.run(staticBiasParameters, smu_instance, arduino_instance, isSavingResults=True, isPlottingResults=False)
		if(asb_parameters['applyGateSweepBetweenBiases']):
			gateSweepScript.run(gateSweepParameters, smu_instance, isSavingResults=True, isPlottingResults=False)

		print('Completed static bias #'+str(i+1)+' of '+str(numberOfStaticBiases))

		# Delay before doing the next StaticBias
		if((asb_parameters['delayBetweenBiases'] > 0) and (i+1 < numberOfStaticBiases)):
			print('Waiting for: ' + str(asb_parameters['delayBetweenBiases']) + ' seconds...')
			time.sleep(asb_parameters['delayBetweenBiases'])

		
		



