from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'chip',
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'colorMap':'plasma',
		'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
		'ylabel':'$I_{{D}}$ [$\\mu$A]',
		'neg_label':'$-I_{{D}}$ [$\\mu$A]',
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title('Chip ' + str(identifiers['wafer']) + str(identifiers['chip']))
	
	# Colors
	colorMap = colorsFromMap(plotDescription['plotDefaults']['colorMap'], 0, 0.87, len(recentRunChipHistory))
	colors = colorMap['colors']
	if(len(recentRunChipHistory) == 1):
		colors = [plt.rcParams['axes.prop_cycle'].by_key()['color'][1]]
	elif(len(recentRunChipHistory) == 2):
		colors = [plt.rcParams['axes.prop_cycle'].by_key()['color'][1], plt.rcParams['axes.prop_cycle'].by_key()['color'][0]]
	
	# If first segment of device history is mostly negative current, flip data
	if((len(recentRunChipHistory) > 0) and (np.percentile(recentRunChipHistory[0]['Results']['id_data'], 75) < 0)):
		recentRunChipHistory = scaledData(recentRunChipHistory, 'Results', 'id_data', -1)
		plotDescription['plotDefaults']['ylabel'] = plotDescription['plotDefaults']['neg_label']
	
	# Plot
	for i in range(len(recentRunChipHistory)):
		line = plotTransferCurve(ax, recentRunChipHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(recentRunChipHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
		
	# Label axes
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])
	
	# Save Figure
	adjustAndSaveFigure(fig, 'ChipTransferCurves', mode_parameters)
	return (fig, ax)
	
