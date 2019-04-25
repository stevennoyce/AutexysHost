from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu



plotDescription = {
	'plotCategory': 'chip',
	'priority': 1040,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		
		'spacing':1,
		'x_padding':0.8,
		'width':0.5,
		
		'ylabel':'Transconductance ($\\mathregular{\\mu}$S)',
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
		gmVals.append(gm)
			
	colors = ['#000000']		
	for i in [0]:		
		line = ax.boxplot(gmVals, positions=range(len(gmVals)), widths=[plotDescription['plotDefaults']['width']], meanline=False, showmeans=False, showfliers=False, boxprops={'color':colors[i]}, capprops={'color':colors[i]}, whiskerprops={'color':colors[i]}, medianprops={'color':colors[i]}, meanprops={'color':colors[i]})	
	
	axisLabels(ax, y_label=plotDescription['plotDefaults']['ylabel'])
	
	return (fig, (ax,))

