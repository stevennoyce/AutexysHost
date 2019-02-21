from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu



plotDescription = {
	'plotCategory': 'chip',
	'priority': 1040,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'ylabel':'Transconductance ($\\mu$A/V)',
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
		
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
		axisLabels(ax, y_label=plotDescription['plotDefaults']['ylabel'])
	else:
		axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])

	return (fig, (ax,))

