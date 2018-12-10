from utilities.MatplotlibUtility import *
import copy


plotDescription = {
	'plotCategory': 'chip',
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'includeOrigin':True,
		'colorMap':'magma',
		'colorDefault': ['#f2b134'],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ (V)',
		'ylabel':'$I_{{D}}$ ($\\mu$A)',
		'neg_label':'$-I_{{D}}$ ($\\mu$A)',
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, chipHistoryList, mode_parameters=None):
	# Load Defaults
	plotDescrip_current = copy.deepcopy(plotDescription)

	# Init Figure
	fig, ax = initFigure(1, 1, plotDescrip_current['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title('Chip ' + str(identifiers['wafer']) + str(identifiers['chip']))
	
	# Colors
	colors = setupColors(fig, len(specificRunChipHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescrip_current['plotDefaults']['colorDefault'], colorMapName=plotDescrip_current['plotDefaults']['colorMap'], colorMapStart=0.85, colorMapEnd=0, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=['', '', ''], colorBarAxisLabel='')		
	
	# If first segment of device history is mostly negative current, flip data
	if((len(specificRunChipHistory) > 0) and ((np.array(specificRunChipHistory[0]['Results']['id_data']) < 0).sum() > (np.array(specificRunChipHistory[0]['Results']['id_data']) >= 0).sum())):
		specificRunChipHistory = scaledData(specificRunChipHistory, 'Results', 'id_data', -1)
		plotDescrip_current['plotDefaults']['ylabel'] = plotDescrip_current['plotDefaults']['neg_label']
	
	# Plot
	for i in range(len(specificRunChipHistory)):
		line = plotTransferCurve(ax, specificRunChipHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(specificRunChipHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
		
	# Label axes
	axisLabels(ax, x_label=plotDescrip_current['plotDefaults']['xlabel'], y_label=plotDescrip_current['plotDefaults']['ylabel'])
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescrip_current['plotDefaults']['includeOrigin'])
	
	# Save Figure
	adjustAndSaveFigure(fig, 'ChipTransferCurves', mode_parameters)
	return (fig, ax)
	
