from utilities.MatplotlibUtility import *

plot_parameters = {
	
}

plotDescription = {}

def plot():
	pass



	




plot_parameters['ChipHistogram'] = {
	'figsize':(5,4),
	'xlabel':'Device',
	'ylabel':'Experiments'
}

def plotChipHistogram(chipIndexes, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['ChipHistogram']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build index, experiment lists
	devices = list(chipIndexes.keys())
	deviceExperiments = len(devices)*[0]
	for device, indexData in chipIndexes.items():
		deviceExperiments[devices.index(device)] = indexData['experimentNumber']
	
	deviceExperiments, devices = zip(*(reversed(sorted(zip(deviceExperiments, devices)))))

	# Plot
	ax.bar(devices, deviceExperiments)

	# Label axes
	axisLabels(ax, x_label=plot_parameters['ChipHistogram']['xlabel'], y_label=plot_parameters['ChipHistogram']['ylabel'])
	tickLabels(ax, devices, rotation=90)

	# Save figure
	adjustAndSaveFigure(fig, 'ChipHistogram', mode_parameters)
	return (fig, ax)



plot_parameters['ChipOnOffRatios'] = {
	'figsize':(5,4),
	'xlabel':'Device',
	'ylabel':'On/Off Ratio, (Order of Mag)'
}

def plotChipOnOffRatios(firstRunChipHistory, recentRunChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['ChipOnOffRatios']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build On/Off Ratio lists
	devices = []
	firstOnOffRatios = []
	for deviceRun in firstRunChipHistory:
		devices.append(deviceRun['Identifiers']['device']) 
		firstOnOffRatios.append(np.log10(deviceRun['Computed']['onOffRatio']))
	lastOnOffRatios = len(devices)*[0]
	for deviceRun in recentRunChipHistory:
		lastOnOffRatios[devices.index(deviceRun['Identifiers']['device'])] = np.log10(deviceRun['Computed']['onOffRatio'])

	lastOnOffRatios, devices, firstOnOffRatios = zip(*(reversed(sorted(zip(lastOnOffRatios, devices, firstOnOffRatios)))))

	# Plot
	line = ax.plot(range(len(devices)), firstOnOffRatios, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], marker='o', markersize=6, linewidth=0, linestyle=None)[0]
	setLabel(line, 'First Run')
	line = ax.plot(range(len(devices)), lastOnOffRatios, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)[0]
	setLabel(line, 'Most Recent Run')

	# Label axes
	axisLabels(ax, x_label=plot_parameters['ChipOnOffRatios']['xlabel'], y_label=plot_parameters['ChipOnOffRatios']['ylabel'])
	tickLabels(ax, devices, rotation=90)
	
	# Add Legend and save figure
	ax.legend(loc=mode_parameters['legendLoc'])
	adjustAndSaveFigure(fig, 'ChipOnOffRatios', mode_parameters)
	return (fig, ax)
	


plot_parameters['ChipOnOffCurrents'] = {
	'figsize':(5,4),
	'xlabel':'Device',
	'ylabel':'$I_{{ON}}$ [$\\mu$A]',
	'ylabel_dual_axis':'$I_{{OFF}}$ [$\\mu$A]'
}	
	
def plotChipOnOffCurrents(recentRunChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['ChipOnOffCurrents']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build On Current lists
	devices = []
	recentOnCurrents = []
	recentOffCurrents = []
	for deviceRun in recentRunChipHistory:
		devices.append(deviceRun['Identifiers']['device']) 
		recentOnCurrents.append(deviceRun['Computed']['onCurrent'] * 10**6)
		recentOffCurrents.append(deviceRun['Computed']['offCurrent'] * 10**6)

	recentOnCurrents, devices, recentOffCurrents = zip(*(reversed(sorted(zip(recentOnCurrents, devices, recentOffCurrents)))))

	# Plot
	if(mode_parameters['inlcudeOffCurrent']):
		line = ax.plot(range(len(devices)), recentOffCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], marker='o', markersize=8, linewidth=0, linestyle=None)[0]
		setLabel(line, 'Off Currents')
	line = ax.plot(range(len(devices)), recentOnCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)[0]
	setLabel(line, 'On Currents')

	# Label axes
	axisLabels(ax, x_label=plot_parameters['ChipOnOffCurrents']['xlabel'], y_label=plot_parameters['ChipOnOffCurrents']['ylabel'])
	tickLabels(ax, devices, rotation=90)
	
	# Add Legend
	ax.legend(loc=mode_parameters['legendLoc'])
	
	# Save Figure
	adjustAndSaveFigure(fig, 'ChipOnOffCurrents', mode_parameters)
	return (fig, ax)



plot_parameters['plotChipTransferCurves'] = {
	'figsize':(2.8,3.2),
	'colorMap':'plasma',
	'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
	'ylabel':'$I_{{D}}$ [$\\mu$A]',
	'neg_label':'$-I_{{D}}$ [$\\mu$A]',
}

def plotChipTransferCurves(recentRunChipHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['ChipTransferCurves']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title('Chip ' + str(identifiers['wafer']) + str(identifiers['chip']))
	
	# Colors
	colorMap = colorsFromMap(plot_parameters['ChipTransferCurves']['colorMap'], 0, 0.87, len(recentRunChipHistory))
	colors = colorMap['colors']
	if(len(recentRunChipHistory) == 1):
		colors = [plt.rcParams['axes.prop_cycle'].by_key()['color'][1]]
	elif(len(recentRunChipHistory) == 2):
		colors = [plt.rcParams['axes.prop_cycle'].by_key()['color'][1], plt.rcParams['axes.prop_cycle'].by_key()['color'][0]]
	
	# If first segment of device history is mostly negative current, flip data
	if((len(recentRunChipHistory) > 0) and (np.percentile(recentRunChipHistory[0]['Results']['id_data'], 75) < 0)):
		recentRunChipHistory = scaledData(recentRunChipHistory, 'Results', 'id_data', -1)
		plot_parameters['ChipTransferCurves']['ylabel'] = plot_parameters['ChipTransferCurves']['neg_label']
	
	# Plot
	for i in range(len(recentRunChipHistory)):
		line = plotTransferCurve(ax, recentRunChipHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(recentRunChipHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
		
	# Label axes
	axisLabels(ax, x_label=plot_parameters['ChipTransferCurves']['xlabel'], y_label=plot_parameters['ChipTransferCurves']['ylabel'])
	
	# Save Figure
	adjustAndSaveFigure(fig, 'ChipTransferCurves', mode_parameters)
	return (fig, ax)
	
