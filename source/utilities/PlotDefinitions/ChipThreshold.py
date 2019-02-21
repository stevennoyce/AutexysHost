from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu



plotDescription = {
	'plotCategory': 'chip',
	'priority': 1050,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'xlabel':'Device',
		'ylabel':'Threshold Voltage (V)',
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
		
	# Plot
	if groupedChipHistory == None or len(groupedChipHistory) <= 0:
		groupedChipHistory = list()
		groupedChipHistory.append(specificRunChipHistory)
	vtVals = list()
	for chipHistory in groupedChipHistory:
		gm, vt, r2 = dpu.fitBasicDeviceModel(chipHistory)
		if not mode_parameters['useBoxWhiskerPlot']:
			line = ax.plot(range(len(vt)), vt, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)
		else: 
			vtVals.append(vt)
			
	if mode_parameters['useBoxWhiskerPlot']: 
		line = boxplot(ax, vtVals)
		axisLabels(ax, y_label=plotDescription['plotDefaults']['ylabel'])
	else:
		axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])

	return (fig, (ax,))

