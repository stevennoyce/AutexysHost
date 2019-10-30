# === Imports ===
import random
import time

import pipes
from procedures import Gate_Sweep as gateSweepScript
from procedures import Flow_Static_Bias as flowStaticBiasScript
from utilities import DataLoggerUtility as dlu

# Turns ON "pin", turns every other pin OFF
# if pin == -1, turn off every pin
def turnOnlyPin(smu_instance, pumpPins, pin):
	pumpPins = range(1, 11) # do it for every pin in existence
	for i in pumpPins:
		if i != pin:
			smu_instance.digitalWrite(i, "LOW")
	#print("turning on: " + str(pin))
	smu_instance.digitalWrite(pin, "HIGH")

# Reverses prior pin to recycle, then flushes
def flushingPins(smu_instance, flushPins, reversePumpPins, pinToFlush):
	turnOnlyPin(smu_instance, reversePumpPins, pinToFlush)
	time.sleep(2)
	turnOnlyPin(smu_instance, reversePumpPins, -1)
	time.sleep(1)
	# turn on flushing pin
	turnOnlyPin(smu_instance, flushPins, flushPins[0])
	time.sleep(4)
	turnOnlyPin(smu_instance, flushPins, -1)
	time.sleep(1)
	turnOnlyPin(smu_instance, flushPins, flushPins[1])
	time.sleep(4)
	turnOnlyPin(smu_instance, flushPins, -1)
	time.sleep(1)

# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# Create distinct parameters for all scripts that could be run
	gateSweepParameters = dict(parameters)
	gateSweepParameters['runType'] = 'GateSweep'

	flowStaticBiasParameters = dict(parameters)
	flowStaticBiasParameters['runType'] = 'FlowStaticBias'

	runAutoFlowStaticBias(parameters, smu_systems, arduino_systems, gateSweepParameters, flowStaticBiasParameters, share=share)

def runAutoFlowStaticBias(parameters, smu_systems, arduino_systems, gateSweepParameters, flowStaticBiasParameters, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]
	
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

	# Send initial progress update
	pipes.progressUpdate(share, 'Bias', start=0, current=0, end=numberOfFlowStaticBiases, barType="Sweep")

	## === START ===
	print('Beginning AutoFlowStaticBias test with the following parameter lists:')
	print('Gate Voltages:  {:} \n Drain Voltages:  {:} \n Gate Voltages between biases:  {:} \n Drain Voltages between biases:  {:} \n Delay Between Applying Voltages:  {:} \n Delay Before Measurements Begin:  {:}'.format(gateVoltageSetPointList, drainVoltageSetPointList, gateVoltageWhenDoneList, drainVoltageWhenDoneList, delayWhenDoneList, delayBeforeMeasurementsList))

	# Run a pre-test gate sweep just to make sure everything looks good
	if(asb_parameters['doInitialGateSweep']):
		print('Taking an initial sweep to get a baseline of device performance prior to StaticBias...')
		gateSweepJsonData = gateSweepScript.run(gateSweepParameters, smu_systems, arduino_systems, share=share)

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
		reversePumpPins = parameters['runConfigs']['FlowStaticBias']['reversePumpPins']
		flushPins = parameters['runConfigs']['FlowStaticBias']['flushPins']
		
		for x in range(0, len(pumpPins)):
			pumpPins[x] = int(pumpPins[x])
			flowDurations[x] = int(flowDurations[x])
		
		# Run StaticBias, GateSweep (if desired) BEFORE
		if(asb_parameters['applyGateSweepBetweenBiases']):
			for x in range(0, len(pumpPins)):
				print("Exchanging fluid for digitalPin: " + str(pumpPins[x]))
				turnOnlyPin(smu_instance, pumpPins, int(pumpPins[x]))
				time.sleep(int(flowDurations[x]))
				print("Stopping fluid exchange")
				turnOnlyPin(smu_instance, pumpPins, -1) # turn off everything else
				time.sleep(5) # reduce noise
				
				gateSweepJsonData = gateSweepScript.run(gateSweepParameters, smu_systems, arduino_systems, share=share)
				
				print("START: Recycling, then flushing environment")
				pinToReverse = reversePumpPins[x]
				flushingPins(smu_instance, flushPins, reversePumpPins, pinToReverse)
				print("DONE: Recycling, then flushing environment")
				
				
		# delay for a bit
		print("Delaying for 20 seconds prior to FlowStaticBias")
		time.sleep(20)
		flowStaticBiasJsonData = flowStaticBiasScript.run(flowStaticBiasParameters, smu_systems, arduino_systems, share=share)

		if(asb_parameters['applyGateSweepBetweenBiases'] and asb_parameters['applyGateSweepBothBeforeAndAfter']):
			gateSweepJsonData = gateSweepScript.run(gateSweepParameters, smu_systems, arduino_systems, share=share)

		print('Completed static bias #'+str(i+1)+' of '+str(numberOfFlowStaticBiases))

		# Send progress update
		pipes.progressUpdate(share, 'Bias', start=0, current=i+1, end=numberOfFlowStaticBiases, barType="Sweep")

		# Delay before doing the next StaticBias
		if((asb_parameters['delayBetweenBiases'] > 0) and (i+1 < numberOfFlowStaticBiases)):
			print('Waiting for: ' + str(asb_parameters['delayBetweenBiases']) + ' seconds...')
			time.sleep(asb_parameters['delayBetweenBiases'])

		
		



