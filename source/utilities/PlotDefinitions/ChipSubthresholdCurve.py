from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'chip',
	'priority': 20,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'automaticAxisLabels':True,
		'colorMap':'viridis',
		'colorDefault': ['#f2b134'],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ (V)',
		'ylabel':'|$I_{{D}}$| (A)',
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Colors
	colors = setupColors(fig, len(specificRunChipHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.85, colorMapEnd=0, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=['', '', ''], colorBarAxisLabel='')		
	
	# Plot
	for i in range(len(specificRunChipHistory)):
		line = plotSubthresholdCurve(ax, specificRunChipHistory[i], colors[i], direction=mode_parameters['sweepDirection'], fitSubthresholdSwing=False, includeLabel=False, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])			
		if(len(specificRunChipHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
		
	# Set tick spacing
	ax.yaxis.set_major_locator(matplotlib.ticker.LogLocator(numticks=10))
	
	return (fig, (ax,))
	
