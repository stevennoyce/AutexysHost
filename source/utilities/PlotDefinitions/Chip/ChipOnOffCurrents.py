from utilities.MatplotlibUtility import *



plotDescription = {
	'name':'Chip On/Off Current',
	'plotCategory': 'chip',
	'priority': 1020,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.75,4.5),
		'automaticAxisLabels':True,
		'colorMap':'white_blue_black',
		'colorDefault':[],
		
		'xlabel':'$I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'ylabel':'Device',
		'leg_label1':'Off Currents',
		'leg_label2':'On Currents',
		
		'markerSizeSmall': 4,
		'markerSizeLarge': 6,
	},
}
	
def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build On Current lists
	devices = []
	recentOnCurrents = []
	recentOffCurrents = []
	for deviceRun in recentRunChipHistory:
		devices.append(deviceRun['Identifiers']['device']) 
		recentOnCurrents.append(deviceRun['Computed']['onCurrent'] * 10**6)
		recentOffCurrents.append(deviceRun['Computed']['offCurrent'] * 10**6)

	recentOnCurrents, devices, recentOffCurrents = zip(*(sorted(zip(recentOnCurrents, devices, recentOffCurrents))))

	# Colors
	colors = setupColors(None, 2, colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.7, colorMapEnd=0.3, enableColorBar=False)

	# Plot
	line1 = ax.plot(recentOffCurrents, range(len(devices)), color=colors[0], marker='o', markersize=plotDescription['plotDefaults']['markerSizeLarge'], linewidth=0, linestyle=None)[0]	
	line2 = ax.plot(recentOnCurrents,  range(len(devices)), color=colors[1], marker='o', markersize=plotDescription['plotDefaults']['markerSizeSmall'], linewidth=0, linestyle=None)[0]

	# Set tick labels
	ax.set_yticklabels(devices)
	ax.set_yticks(range(len(devices)))
	
	# Add Legend
	ax.legend([line1, line2], [plotDescription['plotDefaults']['leg_label1'], plotDescription['plotDefaults']['leg_label2']], loc=mode_parameters['legendLoc'])
	
	# Adjust X-lim
	includeOriginOnXaxis(ax, include=True, stretchfactor=1)
	
	return (fig, (ax,))
