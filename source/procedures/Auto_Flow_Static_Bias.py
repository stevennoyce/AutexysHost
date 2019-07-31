# === Imports ===
import random
import time

import pipes
from procedures import Gate_Sweep as gateSweepScript
from procedures import Flow_Static_Bias as flowStaticBiasScript
from utilities import DataLoggerUtility as dlu


def flushAirAndWaterPins(smu_instance, airPin, waterPin, pumpPins):
	a = 1
	turnOnlyPin(smu_instance, pumpPins, airPin)
	time.sleep(4)
	turnOnlyPin(smu_instance, pumpPins, -1)
	time.sleep(1)
	turnOnlyPin(smu_instance, pumpPins, waterPin)
	time.sleep(2)
	turnOnlyPin(smu_instance, pumpPins, -1)
	time.sleep(1)
	turnOnlyPin(smu_instance, pumpPins, airPin)
	time.sleep(4)
	turnOnlyPin(smu_instance, pumpPins, -1)
	time.sleep(1)

def turnOnlyPin(smu_instance, pumpPins, pin):
	pumpPins = range(1, 11) # do it for every pin in existence
	for i in pumpPins:
		if i != pin:
			smu_instance.digitalWrite(i, "LOW")
	smu_instance.digitalWrite(pin, "HIGH")

# === Main ===
def run(parameters, smu_instance, arduino_instance, share=None):
	# Create distinct parameters for all scripts that could be run
	gateSweepParameters = dict(parameters)
	gateSweepParameters['runType'] = 'GateSweep'

	flowStaticBiasParameters = dict(parameters)
	flowStaticBiasParameters['runType'] = 'FlowStaticBias'

	runAutoFlowStaticBias(parameters, smu_instance, arduino_instance, gateSweepParameters, flowStaticBiasParameters)	

def runAutoFlowStaticBias(parameters, smu_instance, arduino_instance, gateSweepParameters, flowStaticBiasParameters, share=None):
	sb_parameters = flowStaticBiasParameters['runConfigs']['FlowStaticBias']
	asb_parameters = parameters['runConfigs']['AutoFlowStaticBias']

	numberOfFlowStaticBiases = asb_parameters['numberOfFlowStaticBiases']
	
	# Build arrays of all parameters that could change over the course of any given experiement
	# biasTimeList 				= asb_parameters['biasTimeList'] if(len(asb_parameters['biasTimeList']) == numberOfFlowStaticBiases) else ([sb_parameters['totalBiasTime']]*numberOfFlowStaticBiases)
	gateVoltageSetPointList 	= [sb_parameters['gateVoltageSetPoint']]*numberOfFlowStaticBiases
	drainVoltageSetPointList 	= [sb_parameters['drainVoltageSetPoint']]*numberOfFlowStaticBiases
	gateVoltageWhenDoneList 	= [sb_parameters['gateVoltageWhenDone']]*numberOfFlowStaticBiases
	drainVoltageWhenDoneList 	= [sb_parameters['drainVoltageWhenDone']]*numberOfFlowStaticBiases
	delayWhenDoneList 			= [sb_parameters['delayWhenDone']]*numberOfFlowStaticBiases
	delayBeforeMeasurementsList = [sb_parameters['delayBeforeMeasurementsBegin']]*numberOfFlowStaticBiases

	# Modify parameter arrays so that they increment there values as desired
	currentIncrementNumber = 1
	for i in range(numberOfFlowStaticBiases):
		if(i >= asb_parameters['numberOfBiasesBetweenIncrements']*currentIncrementNumber):
			currentIncrementNumber += 1
		gateVoltageSetPointList[i] 	+= asb_parameters['incrementStaticGateVoltage']*(currentIncrementNumber-1)
		drainVoltageSetPointList[i] += asb_parameters['incrementStaticDrainVoltage']*(currentIncrementNumber-1)
		gateVoltageWhenDoneList[i] 	+= asb_parameters['incrementGateVoltageWhenDone']*(currentIncrementNumber-1)
		drainVoltageWhenDoneList[i] += asb_parameters['incrementDrainVoltageWhenDone']*(currentIncrementNumber-1)
		delayWhenDoneList[i] 		+= asb_parameters['incrementDelayBeforeReapplyingVoltage']*(currentIncrementNumber-1)	
	delayBeforeMeasurementsList[0] = asb_parameters['firstDelayBeforeMeasurementsBegin']



	## === START ===
	print('Beginning AutoFlowStaticBias test with the following parameter lists:')
	print('Gate Voltages:  {:} \n Drain Voltages:  {:} \n Gate Voltages between biases:  {:} \n Drain Voltages between biases:  {:} \n Delay Between Applying Voltages:  {:} \n Delay Before Measurements Begin:  {:}'.format(gateVoltageSetPointList, drainVoltageSetPointList, gateVoltageWhenDoneList, drainVoltageWhenDoneList, delayWhenDoneList, delayBeforeMeasurementsList))
	
	# Run a pre-test gate sweep just to make sure everything looks good
	if(asb_parameters['doInitialGateSweep']):
		print('Taking an initial sweep to get a baseline of device performance prior to StaticBias...')
		gateSweepScript.run(gateSweepParameters, smu_instance, isSavingResults=True, isPlottingResults=False)

	# Run all Static Biases in this Experiment
	for i in range(numberOfFlowStaticBiases):
		print('Starting flow static bias #'+str(i+1)+' of '+str(numberOfFlowStaticBiases))
		
		# Get the parameters for this FlowStaticBias from the pre-built arrays
		#sb_parameters['totalBiasTime'] = biasTimeList[i]
		sb_parameters['gateVoltageSetPoint'] = gateVoltageSetPointList[i]
		sb_parameters['drainVoltageSetPoint'] = drainVoltageSetPointList[i]
		sb_parameters['gateVoltageWhenDone'] = gateVoltageWhenDoneList[i]
		sb_parameters['drainVoltageWhenDone'] = drainVoltageWhenDoneList[i]
		sb_parameters['delayWhenDone'] = delayWhenDoneList[i]
		sb_parameters['delayBeforeMeasurementsBegin'] = delayBeforeMeasurementsList[i]
		
		pumpPins = parameters['runConfigs']['FlowStaticBias']['pumpPins']
		flowDurations = parameters['runConfigs']['FlowStaticBias']['flowDurations']
		airAndWaterPins = parameters['runConfigs']['FlowStaticBias']['airAndWaterPins']
		airPin = airAndWaterPins[0]
		waterPin = airAndWaterPins[1]
		
		for x in range(0, len(pumpPins)):
			pumpPins[x] = int(pumpPins[x])
			flowDurations[x] = int(flowDurations[x])
		
		# Run StaticBias, GateSweep (if desired) BEFORE
		if(asb_parameters['applyGateSweepBetweenBiases']):
			for x in range(0, len(pumpPins)):
				if x != 0:
					print("Exchanging air and water")
					flushAirAndWaterPins(smu_instance, airPin, waterPin, pumpPins)
					print("DONE exchanging air and water pins")
				print("Exchanging fluid for digitalPin: " + str(pumpPins[x]))
				turnOnlyPin(smu_instance, pumpPins, int(pumpPins[x]))
				time.sleep(int(flowDurations[x]))
				print("Stopping fluid exchange")
				turnOnlyPin(smu_instance, pumpPins, -1) # turn off everything else
				time.sleep(5) # reduce noise
				gateSweepScript.run(gateSweepParameters, smu_instance, isSavingResults=True, isPlottingResults=False)
				
		# delay for a bit
		print("Delaying for 20 seconds prior to FlowStaticBias")
		time.sleep(20)
		flowStaticBiasScript.run(flowStaticBiasParameters, smu_instance, arduino_instance, isSavingResults=True, isPlottingResults=False)
		if(asb_parameters['applyGateSweepBetweenBiases'] and asb_parameters['applyGateSweepBothBeforeAndAfter']):
			gateSweepScript.run(gateSweepParameters, smu_instance, isSavingResults=True, isPlottingResults=False)

		print('Completed static bias #'+str(i+1)+' of '+str(numberOfFlowStaticBiases))

		# Delay before doing the next StaticBias
		if((asb_parameters['delayBetweenBiases'] > 0) and (i+1 < numberOfFlowStaticBiases)):
			print('Waiting for: ' + str(asb_parameters['delayBetweenBiases']) + ' seconds...')
			time.sleep(asb_parameters['delayBetweenBiases'])

		
		



