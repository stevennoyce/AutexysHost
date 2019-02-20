from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'chip',
	'priority': 10,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'includeOrigin':True,
		'colorMap':'magma',
		'colorDefault': ['#f2b134'],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ (V)',
		'ylabel':'$I_{{D}}$ ($\\mu$A)',
		'neg_ylabel':'$-I_{{D}}$ ($\\mu$A)',
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title('Chip ' + str(identifiers['wafer']) + str(identifiers['chip']))
	
	# Colors
	colors = setupColors(fig, len(specificRunChipHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.85, colorMapEnd=0, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=['', '', ''], colorBarAxisLabel='')		
	
	# If first segment of device history is mostly negative current, flip data
	ylabel = plotDescription['plotDefaults']['ylabel']
	if((len(specificRunChipHistory) > 0) and ((np.array(specificRunChipHistory[0]['Results']['id_data']) < 0).sum() > (np.array(specificRunChipHistory[0]['Results']['id_data']) >= 0).sum())):
		specificRunChipHistory = scaledData(specificRunChipHistory, 'Results', 'id_data', -1)
		ylabel = plotDescription['plotDefaults']['neg_ylabel']
	
	# Plot
	for i in range(len(specificRunChipHistory)):
		line = plotTransferCurve(ax, specificRunChipHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(specificRunChipHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
		
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOrigin'])
	
	return (fig, ax)
	
