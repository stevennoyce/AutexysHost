from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu
import copy



plotDescription = {
	'plotCategory': 'chip',
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'xlabel':'Device',
		'ylabel':'Threshold Voltage (V)',
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, chipHistoryList, mode_parameters=None):
	# Load Defaults
	plotDescrip_current = copy.deepcopy(plotDescription)

	# Init Figure
	fig, ax = initFigure(1, 1, plotDescrip_current['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title('Chip ' + str(identifiers['wafer']) + str(identifiers['chip']))
		
	# Plot
	if chipHistoryList == None or len(chipHistoryList) <= 0:
		chipHistoryList = list()
		chipHistoryList.append(specificRunChipHistory)
	vtVals = list()
	for chipHistory in chipHistoryList:
		gm, vt, r2 = dpu.fitBasicDeviceModel(chipHistory)
		if not mode_parameters['useBoxWhiskerPlot']:
			line = ax.plot(range(len(vt)), vt, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)
		else: 
			vtVals.append(vt)
	if mode_parameters['useBoxWhiskerPlot']: 
		line = boxplot(ax, vtVals)
		axisLabels(ax, y_label=plotDescrip_current['plotDefaults']['ylabel'])
	else:
		axisLabels(ax, x_label=plotDescrip_current['plotDefaults']['xlabel'], y_label=plotDescrip_current['plotDefaults']['ylabel'])

	# Save figure	
	adjustAndSaveFigure(fig, 'ChipThreshold', mode_parameters)

	return (fig, ax)

