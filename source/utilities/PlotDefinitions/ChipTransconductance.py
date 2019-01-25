from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu
import copy



plotDescription = {
	'plotCategory': 'chip',
	'priority': 130,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'ylabel':'Transconductance ($\\mu$A/V)',
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory, mode_parameters=None):
	# Load Defaults
	plotDescrip_current = copy.deepcopy(plotDescription)

	# Init Figure
	fig, ax = initFigure(1, 1, plotDescrip_current['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title('Chip ' + str(identifiers['wafer']) + str(identifiers['chip']))
		
	# Plot

	# Plot
	if groupedChipHistory == None or len(groupedChipHistory) <= 0:
		groupedChipHistory = list()
		groupedChipHistory.append(specificRunChipHistory)
	gmVals = list()
	for chipHistory in groupedChipHistory:
		gm, vt, r2 = dpu.fitBasicDeviceModel(chipHistory)
		gm = [val*1000000 for val in gm] #Convert to uA
		if not mode_parameters['useBoxWhiskerPlot']:
			line = ax.plot(range(len(gm)), gm, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)
		else: 
			gmVals.append(gm)
	if mode_parameters['useBoxWhiskerPlot']: 
		line = boxplot(ax, gmVals)
		axisLabels(ax, y_label=plotDescrip_current['plotDefaults']['ylabel'])
	else:
		axisLabels(ax, x_label=plotDescrip_current['plotDefaults']['xlabel'], y_label=plotDescrip_current['plotDefaults']['ylabel'])


	axisLabels(ax, y_label=plotDescrip_current['plotDefaults']['ylabel'])


	# Save figure	
	adjustAndSaveFigure(fig, 'ChipTransconductance', mode_parameters)

	return (fig, ax)

