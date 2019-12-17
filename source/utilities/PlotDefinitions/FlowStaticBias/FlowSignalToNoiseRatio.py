# Author: Nathan Choe
# specifically for: AutoFlowStaticBias data

from utilities.MatplotlibUtility import *


plotDescription = {
	'plotCategory': 'device',
	'priority': 610,
	'dataFileDependencies': ['FlowStaticBias.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'colorMap':'plasma',
		'colorDefault': ['#1f77b4'],
		'color2Default': ['#009933'],
		'includeOriginOnYaxis':True,
		
		'xlabel':'$V_{{GS}}$ (V)',
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

	# Build Color Map and Color Bar
	#totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	#holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0, colorMapEnd=0.87, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarAxisLabel='')
	#colors2 = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['color2Default'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')

	# Calculate means and standard deviations
	normalize = False # Normalize by Vgs? (divides all SNRs by Vgs)
	noiseAxis = True # Plot noise on second y axis?
		
	SNR = []
	SNR_averaged_cycles = []
	SNR_total = []
	SNR_total_std = []
	allVgs = []
	for i in range(len(deviceHistory)):
		
		currentDevice = deviceHistory[i]
		
		cycleCount = currentDevice["runConfigs"]["FlowStaticBias"]["cycleCount"]
		pumpPins = currentDevice["runConfigs"]["FlowStaticBias"]["pumpPins"]
		numberOfMotors = len(pumpPins)
		# this should be a constant value regardless
		currentVgs = np.mean(currentDevice["Results"]["vgs_data"]) 
		currentVds = np.mean(currentDevice["Results"]["vds_data"]) 
		
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
		print(pump_on_intervals_pin)
		for pumpIntervalCount in pump_on_intervals_pin:
			if prevPin != pumpIntervalCount:
				#print("counter: ", str(counter))
				pinAlternatingCounter += 1
				prevPin = pumpIntervalCount
				print(counter)
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
			#print("cycle count: ", str(cycleIndex))
			
			# go through every other pin, compare to control
			for pinIndex in range(1, len(pumpPins)):
				control_data = id_data_total[cycleIndex][0]
				control_data = control_data[int(len(control_data)*1/4):int(len(control_data)*3/4)]
				other_data = id_data_total[cycleIndex][pinIndex]
				other_data = other_data[int(len(other_data)*1/4):int(len(other_data)*3/4)]
				u1 = np.mean(control_data)
				u2 = np.mean(other_data)
				#print("means")
				#print(u1, u2)
				
				signal = abs(u1 - u2)
				std1 = np.std(control_data)
				std2 = np.std(other_data)
				noise = (std1 + std2) / 2
				#print(std1, std2)
				
				'''
				print("gate voltage: ", str(currentVgs))
				if i == 0 or i == 1:
				
					print("control: ", str(u1))
					print("other: ", str(u2))
				
					print("std control: ", str(std1))
					print("std other: ", str(std2))
				'''
				individualPumpRatio.append(signal / noise)
			SNR.append(individualPumpRatio)
		#print("SNR")
		#print(SNR)
		
		# go through every possible pin combination (i), and average up the cycles (k)
		SNR_averaged_cycles = []
		SNR_averaged_cycles_std = []
		for i in range(0, len(pumpPins)-1):
			SNR_averaged_cycles.append([])
			SNR_averaged_cycles_std.append([])
			for k in range(1, cycleCount):
				SNR_averaged_cycles[i].append(SNR[k][i])
			a = np.mean(SNR_averaged_cycles[i])
			b = np.std(SNR_averaged_cycles[i])
			SNR_averaged_cycles[i] = a
			SNR_averaged_cycles_std[i] = b
					
			SNR_total.append(SNR_averaged_cycles)
			SNR_total_std.append(SNR_averaged_cycles_std)
			
		allVgs.append(currentVgs)
	
	#print("SNR TOTAL")
	#print(SNR_total)
	#print(allVgs, SNR_total)
	#plt.plot(allVgs, SNR_total, "ro")
	
	'''
	# go through every possible pin combination, and plot
	for x in range(0, len(pumpPins)-1):
		correspondingSNR = []
		for y in range(0, len(allVgs)):
			#print(x, y)
			correspondingSNR.append(SNR_total[y][x])
			
		ax.plot(allVgs, correspondingSNR, color=colors[x], linestyle=None, linewidth=0, marker='o', markersize=4)
	'''
	
	for x in range(0, len(pumpPins)-1):
		correspondingSNR = []
		snr_max_per = 0
		snr_max_per_index = 0
		for y in range(0, len(allVgs)):
			print(x, y)
			correspondingSNR.append(SNR_total[y][x])
			ax.plot([allVgs[y]], [SNR_total[y][x]], color=colors[y], linestyle=None, linewidth=0, marker='o', markersize=4)
			ax.errorbar([allVgs[y]], [SNR_total[y][x]], yerr=SNR_total_std[y][x], color=colors[y], linewidth=1, capsize=2, capthick=0.5, elinewidth=0.5)
			if SNR_total[y][x] > snr_max_per:
				snr_max_per = SNR_total[y][x]
				snr_max_per_index = y
		ax.axvline(allVgs[snr_max_per_index])
	
	
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOriginOnYaxis'])
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])		
			
	return (fig, (ax,))

		
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

