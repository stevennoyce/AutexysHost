from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu



plotDescription = {
	'plotCategory': 'chip',
	'priority': 1050,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		
		'spacing':1,
		'x_padding':0.8,
		'width':0.5,
		
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
		vtVals.append(vt)
		
	colors = ['#000000']		
	for i in [0]:
		line = ax.boxplot(vtVals, positions=range(len(vtVals)), widths=[plotDescription['plotDefaults']['width']], meanline=False, showmeans=False, showfliers=False, boxprops={'color':colors[i]}, capprops={'color':colors[i]}, whiskerprops={'color':colors[i]}, medianprops={'color':colors[i]}, meanprops={'color':colors[i]})	
	
	axisLabels(ax, y_label=plotDescription['plotDefaults']['ylabel'])
	
	return (fig, (ax,))

