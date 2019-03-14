# Author: Matthew Barbano

from utilities.MatplotlibUtility import *
import statistics

plotDescription = {
	'plotCategory': 'device',
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'colorMap':'white_blue_black',
		'colorDefault': ['#1f77b4'],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ (V)',
		'ylabel':'Signal-to-Noise Ratio',
		'y2label':'Noise (A)',   #TODO figure out how to change unit here
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
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')

	# Calculate means and standard deviations
	normalize = False # Normalize by Vgs? (divides all SNRs by Vgs)
	noiseAxis = True # Plot noise on second y axis?

	for i in range(len(deviceHistory)):
		vgs_data_to_plot = [] # Measured, mean is used (better for plotting)
		snr_to_plot = []
		noise_to_plot = []

		steps = deviceHistory[i]['runConfigs']['GateSweep']['stepsInVGSPerDirection']

		pointsPerVGS = deviceHistory[i]['runConfigs']['GateSweep']['pointsPerVGS']
		if pointsPerVGS == 1:
			print("Warning - pointsPerVGS is 1. Standard deviations will be 0 and SNR graph will be blank.") # How to do error properly?

		# Forward direction
		if mode_parameters['sweepDirection'] == 'both' or mode_parameters['sweepDirection'] == 'forward':
			my_direction_vgs_data_to_plot = []
			my_direction_snr_to_plot = []
			my_direction_noise_to_plot = []
			for step in range(steps-1): # -1 because the last iteration does not have a step afterwards for mean calculation
				index = pointsPerVGS * step

				# Drain currents
				my_drain_current_list = deviceHistory[i]['Results']['id_data'][0][index:index+pointsPerVGS]

				next_drain_current_list = deviceHistory[i]['Results']['id_data'][0][index+pointsPerVGS:index+2*pointsPerVGS]
				my_drain_current_mean = statistics.mean(next_drain_current_list) - statistics.mean(my_drain_current_list)
				my_drain_current_stDev = statistics.pstdev(my_drain_current_list)
				if my_drain_current_stDev != 0:
					normTerm = 1
					if normalize:
						normTerm = deviceHistory[i]['Results']['vgs_data'][0][index+pointsPerVGS-1] - deviceHistory[i]['Results']['vgs_data'][0][index+pointsPerVGS] # Don't care about negative
					my_direction_snr_to_plot.append(abs(my_drain_current_mean / (my_drain_current_stDev * normTerm)))  # abs value takes care of negative case

					# Gate voltages - put inside the if statement so that the two lists are same length
					my_direction_vgs_data_to_plot.append(statistics.mean(deviceHistory[i]['Results']['vgs_data'][0][index:index+pointsPerVGS]))

					# Same with noise axis data - inside if statement so the two lists are same length
					my_direction_noise_to_plot.append(my_drain_current_stDev)

			vgs_data_to_plot.append(my_direction_vgs_data_to_plot)
			snr_to_plot.append(my_direction_snr_to_plot)
			noise_to_plot.append(my_direction_noise_to_plot)

		# Reverse direction
		if mode_parameters['sweepDirection'] == 'both' or mode_parameters['sweepDirection'] == 'reverse':
			my_direction_vgs_data_to_plot = []
			my_direction_snr_to_plot = []
			my_direction_noise_to_plot = []

			if mode_parameters['sweepDirection'] == 'both':
				sweep_index = 1
			else:
				sweep_index = 0
			for step in range(1, steps):  # skips the first value like skipping last value with forward direction
				index = pointsPerVGS * step

				# Drain currents
				my_drain_current_list = deviceHistory[i]['Results']['id_data'][sweep_index][index:index+pointsPerVGS]

				prev_drain_current_list = deviceHistory[i]['Results']['id_data'][sweep_index][index-pointsPerVGS:index]
				my_drain_current_mean = statistics.mean(prev_drain_current_list) - statistics.mean(my_drain_current_list)
				my_drain_current_stDev = statistics.pstdev(my_drain_current_list)
				if my_drain_current_stDev != 0:
					normTerm = 1
					if normalize:
						normTerm = deviceHistory[i]['Results']['vgs_data'][sweep_index][index] - deviceHistory[i]['Results']['vgs_data'][sweep_index][index-1] # Don't care about negative
					my_direction_snr_to_plot.append(abs(my_drain_current_mean / (my_drain_current_stDev * normTerm)))  # abs value takes care of negative case

					# Gate voltages - inside if statement so that lists are same length
					my_direction_vgs_data_to_plot.append(statistics.mean(deviceHistory[i]['Results']['vgs_data'][sweep_index][index:index+pointsPerVGS]))

					# Same with noise axis data - inside if statement so the two lists are same length
					my_direction_noise_to_plot.append(my_drain_current_stDev)

			vgs_data_to_plot.append(my_direction_vgs_data_to_plot)
			snr_to_plot.append(my_direction_snr_to_plot)
			noise_to_plot.append(my_direction_noise_to_plot)

		# Plot (both directions on same plot)
		deviceHistory[i]['Results']['vgs_data_to_plot'] = vgs_data_to_plot
		deviceHistory[i]['Results']['snr_to_plot'] = snr_to_plot

		# print('vgs_data_to_plot', vgs_data_to_plot)
		# print('snr_to_plot', snr_to_plot)

		line = plotSNR(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])

		# Add second noise axis
		if noiseAxis:
			ax2, line2 = plotNoiseAxis(ax, vgs_data_to_plot, noise_to_plot, colors[i], lineStyle=None)

		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
			setLabel(line2, mode_parameters['legendLabels'][i])

	# Set axis labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])
	axisLabels(ax2, x_label=None, y_label=plotDescription['plotDefaults']['y2label'])
	ax.yaxis.set_major_locator(matplotlib.ticker.LinearLocator(numticks=10))
	ax2.yaxis.set_major_locator(matplotlib.ticker.LinearLocator(numticks=10))

	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'GateSweep', mode_parameters, includeDataMin=True, includeDataMax=True, includeVgsChange=True, includeVdsSweep=True, includeIdVgsFit=True), mode_parameters=mode_parameters)
	adjustAndSaveFigure(fig, 'SignalToNoiseRatio', mode_parameters)

	return (fig, (ax,))

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
