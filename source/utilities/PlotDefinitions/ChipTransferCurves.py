from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'chip',
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'includeOrigin':True,
		'colorMap':'magma',
		'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][1],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
		'ylabel':'$I_{{D}}$ [$\\mu$A]',
		'neg_label':'$-I_{{D}}$ [$\\mu$A]',
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title('Chip ' + str(identifiers['wafer']) + str(identifiers['chip']))
	
	# Colors
	colors = setupColors(fig, len(specificRunChipHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.85, colorMapEnd=0, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=['', '', ''], colorBarAxisLabel='')		
	
	# If first segment of device history is mostly negative current, flip data
	if((len(specificRunChipHistory) > 0) and (np.percentile(specificRunChipHistory[0]['Results']['id_data'], 75) < 0)):
		specificRunChipHistory = scaledData(specificRunChipHistory, 'Results', 'id_data', -1)
		plotDescription['plotDefaults']['ylabel'] = plotDescription['plotDefaults']['neg_label']
	
	# Plot
	for i in range(len(specificRunChipHistory)):
		line = plotTransferCurve(ax, specificRunChipHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(specificRunChipHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
		
	# Label axes
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOrigin'])
	
	# Save Figure
	adjustAndSaveFigure(fig, 'ChipTransferCurves', mode_parameters)
	return (fig, ax)
	
