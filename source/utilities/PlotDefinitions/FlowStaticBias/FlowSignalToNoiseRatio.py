# Author: Nathan Choe
# specifically for: AutoFlowStaticBias data

# Allow to run as standalone file
import os
import sys
if __name__ == '__main__':	
	pathParents = os.getcwd().split(os.sep)
	if 'AutexysHost' in pathParents:
		os.chdir(os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source'))

from utilities.MatplotlibUtility import *
import matplotlib as plt
import statistics


plotDescription = {
	'plotCategory': 'device',
	'priority': 1,
	'dataFileDependencies': ['FlowStaticBias.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'colorMap':'white_blue_black',
		'colorDefault': ['#1f77b4'],
		'color2Default': ['#009933'],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ (V)',
		'ylabel':'Signal-to-Noise Ratio',
		'y2label':'Noise (A)',
		'leg_vds_label':'$V_{{DS}}^{{Sweep}}$ = {:}V',
		'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V',
		'leg_vgs_change':'$V_{{GS}}^{{Incr}}$ = {:}V',
		'leg_data_min_x':'{:}V',
		'leg_data_max_x':'{:}V',
		'leg_data_min_y':'{:}',
		'leg_data_max_y':'{:}',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	
	# deviceHistory of FlowStaticBiases
	
	# Testing/debugging
	# deviceHistory[0]['Results']['vgs_data'] = [[1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]]
	# deviceHistory[0]['Results']['gateVoltages'] = [[1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]]
	# deviceHistory[0]['Results']['id_data'] = [[15,20,13, 14,13,14, 15,18,17, 20,19,23]]
	# deviceHistory[0]['runConfigs']['GateSweep']['stepsInVGSPerDirection'] = 4
	# deviceHistory[0]['runConfigs']['GateSweep']['pointsPerVGS'] = 3
	# deviceHistory[0]['runConfigs']['GateSweep']['gateVoltageMaximum'] = 4
	# deviceHistory[0]['runConfigs']['GateSweep']['gateVoltageMinimum'] = 1
	# mode_parameters['sweepDirection'] = 'forward'
	# deviceHistory[0]['Results']['vgs_data'] = [[1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]]
	# deviceHistory[0]['Results']['gateVoltages'] = [[1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]]
	# deviceHistory[0]['Results']['id_data'] = [[5, 4, 5, 10, 11, 11, 15, 14, 13, 20, 20, 19]]
	# deviceHistory[0]['runConfigs']['GateSweep']['stepsInVGSPerDirection'] = 4
	# deviceHistory[0]['runConfigs']['GateSweep']['pointsPerVGS'] = 3
	# deviceHistory[0]['runConfigs']['GateSweep']['gateVoltageMaximum'] = 4
	# deviceHistory[0]['runConfigs']['GateSweep']['gateVoltageMinimum'] = 1
	# mode_parameters['sweepDirection'] = 'forward'
	# debuggingInfo(deviceHistory, identifiers, mode_parameters)

	
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	ax2 = None

	# Build Color Map and Color Bar
	#totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	#holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarAxisLabel='')
	#colors2 = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['color2Default'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')

	# Calculate means and standard deviations
	normalize = False # Normalize by Vgs? (divides all SNRs by Vgs)
	noiseAxis = True # Plot noise on second y axis?
	
	
	SNR = []
	SNR_averaged_cycles = []
	SNR_total = []
	allVgs = []
	for i in range(len(deviceHistory)):
		
		currentDevice = deviceHistory[i]
		
		cycleCount = currentDevice["runConfigs"]["FlowStaticBias"]["cycleCount"]
		pumpPins = currentDevice["runConfigs"]["FlowStaticBias"]["pumpPins"]
		numberOfMotors = len(pumpPins)
		# this should be a constant value regardless
		currentVgs = statistics.mean(currentDevice["Results"]["vgs_data"]) 
		currentVds = statistics.mean(currentDevice["Results"]["vds_data"]) 
		
		# current data, with each index containing current data for each respective motor, in their own index for each cycle
		# id_data_total = [ [ [], [] ], [ [], [] ], [ [], [] ] ]
		# ^ with three cycles, with two motors
		id_data_total = []
		for cycleIndex in range(0, cycleCount):
			cycleArray = []
			for pinCount in range(0, numberOfMotors):
				cycleArray.append([])
			id_data_total.append(cycleArray)
		
		# go through pump_on_intervals_pin, add to proper id_data index based on where pin is
		counter = 0
		pinAlternatingCounter = 0
		measuredIdData = currentDevice["Results"]["id_data"]
		pump_on_intervals_pin = currentDevice["Results"]["pump_on_intervals_pin"]
		prevPin = pump_on_intervals_pin[0]
		
		for pumpIntervalCount in pump_on_intervals_pin:
			if prevPin != pumpIntervalCount:
				#print("counter: ", str(counter))
				pinAlternatingCounter += 1
				prevPin = pumpIntervalCount
				#print(int(pinAlternatingCounter / len(pumpPins)))
				
			variablename = int(pinAlternatingCounter / len(pumpPins))
			id_data_total[ variablename ][pumpPins.index(pumpIntervalCount)].append(measuredIdData[counter])
			counter += 1
		
		# calculate signal to noise ratio!
		# The assumption here is that the FIRST pin is the control
		
		# SNR: each index represents noise per cycle; each array in respective index represents SNR b/w control and 
		# solutions outputted from digitalPins as ordered in pumpPins
		SNR = []
		
		for cycleIndex in range(0, cycleCount):			
			individualPumpRatio = []
			for pinIndex in range(1, len(pumpPins)):
				control_data = id_data_total[cycleIndex][0]
				other_data = id_data_total[cycleIndex][pinIndex]
				u1 = statistics.mean(control_data)
				u2 = statistics.mean(other_data)
				signal = abs(u1 - u2)
				std1 = statistics.pstdev(control_data)
				std2 = statistics.pstdev(other_data)
				noise = (std1 + std2) / 2
				individualPumpRatio.append(signal / noise)
			SNR.append(individualPumpRatio)
		
		SNR_averaged_cycles = []
		for i in range(0, len(pumpPins)-1):
			SNR_averaged_cycles.append([])
			for k in range(0, cycleCount):
				SNR_averaged_cycles[i].append(SNR[k][i])
			a = statistics.mean(SNR_averaged_cycles[i])
			SNR_averaged_cycles[i] = a
		
			SNR_total.append(SNR_averaged_cycles[0])
			
		allVgs.append(currentVgs)
	
	print(allVgs, SNR_total)
	#plt.plot(allVgs, SNR_total, "ro")
	ax.plot(allVgs, SNR_total, color=colors[0], linestyle=None, linewidth=0, marker='o', markersize=4)
		
	'''
	# Plot (both directions on same plot)
	deviceHistory[i]['Results']['vgs_data_to_plot'] = vgs_data_to_plot
	deviceHistory[i]['Results']['snr_to_plot'] = snr_to_plot

	# print('vgs_data_to_plot', vgs_data_to_plot)
	# print('snr_to_plot', snr_to_plot)

	line = plotSNR(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])

	# Add second noise axis
	if noiseAxis:
		ax2, line2 = plotNoiseAxis(ax, vgs_data_to_plot, noise_to_plot, colors2[i], lineStyle=None)

	if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
		setLabel(line, mode_parameters['legendLabels'][i])
		if noiseAxis:
			setLabel(line2, mode_parameters['legendLabels'][i])
	'''
		

def debuggingInfo(deviceHistory, identifiers, mode_parameters):
	print("Debugging info for SignalToNoiseRatio.py")
	print("Device history = ", deviceHistory)
	#print("Identifiers = ", identifiers)
	#print("Mode parameters = ", mode_parameters)
	#print("Results in Device histoyr = ")
	#for key in deviceHistory[0]['Results']:
	#	print(key, ": ", deviceHistory[0]['Results'][key], "\n")
	# print('vgs_data_to_plot', ": ", deviceHistory[0]['Results']['vgs_data_to_plot'], "\n")
	#print('snr_to_plot', ": ", deviceHistory[0]['Results']['snr_to_plot'], "\n")
	#print('steps = ', deviceHistory[0]['runConfigs']['GateSweep']['stepsInVGSPerDirection'])

if __name__ == '__main__':
	import json

	data = []
	with open('FlowStaticBias.json') as f:
	    for line in f:
	        data.append(json.loads(line))
	        
	plot(data, None)

