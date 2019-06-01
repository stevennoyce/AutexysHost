from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'chip',
	'priority': 10,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'includeOriginOnYaxis':True,
		'colorMap':'magma',
		'colorDefault': ['#f2b134'],
		'xlabel':'$V_{{GS}}$ (V)',
		'ylabel':'$I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'neg_ylabel':'$-I_{{D}}$ ($\\mathregular{\\mu}$A)',
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Colors
	colors = setupColors(fig, len(specificRunChipHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.85, colorMapEnd=0, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=['', '', ''], colorBarAxisLabel='')		
	
	# If first segment of device history is mostly negative current, flip data
	ylabel = plotDescription['plotDefaults']['ylabel']
	if((len(specificRunChipHistory) > 0) and ((np.array(specificRunChipHistory[0]['Results']['id_data']) < 0).sum() > (np.array(specificRunChipHistory[0]['Results']['id_data']) >= 0).sum())):
		specificRunChipHistory = scaledData(specificRunChipHistory, 'Results', 'id_data', -1)
		ylabel = plotDescription['plotDefaults']['neg_ylabel']
	
	# Plot
	for i in range(len(specificRunChipHistory)):
		line = plotTransferCurve(ax, specificRunChipHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleYaxisBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(specificRunChipHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
		
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)
		
	return (fig, (ax,))
	
