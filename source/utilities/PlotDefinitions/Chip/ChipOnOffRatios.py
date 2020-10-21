from utilities.MatplotlibUtility import *



plotDescription = {
	'name':'Chip On/Off Ratio',
	'plotCategory': 'chip',
	'priority': 1010,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.75,4.5),
		'automaticAxisLabels':True,
		'colorMap':'white_blue_black',
		'colorDefault':[],
		
		'xlabel':'On/Off Ratio, (Order of Mag)',
		'ylabel':'Device',
		
		'markerSizeSmall': 4,
		'markerSizeLarge': 6,
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build On/Off Ratio lists
	devices = []
	firstOnOffRatios = []
	for deviceRun in firstRunChipHistory:
		devices.append(deviceRun['Identifiers']['device']) 
		firstOnOffRatios.append(np.log10(deviceRun['Computed']['onOffRatio']))
	lastOnOffRatios = len(devices)*[0]
	for deviceRun in recentRunChipHistory:
		lastOnOffRatios[devices.index(deviceRun['Identifiers']['device'])] = np.log10(deviceRun['Computed']['onOffRatio'])

	lastOnOffRatios, devices, firstOnOffRatios = zip(*(sorted(zip(lastOnOffRatios, devices, firstOnOffRatios))))

	# Colors
	colors = setupColors(None, 2, colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.7, colorMapEnd=0.3, enableColorBar=False)

	# Plot
	line = ax.plot(firstOnOffRatios, range(len(devices)), color=colors[0], marker='o', markersize=plotDescription['plotDefaults']['markerSizeLarge'], linewidth=0, linestyle=None, label='First Run')[0]
	line = ax.plot(lastOnOffRatios,  range(len(devices)), color=colors[1], marker='o', markersize=plotDescription['plotDefaults']['markerSizeSmall'], linewidth=0, linestyle=None, label='Most Recent Run')[0]

	# Set tick label rotation
	ax.set_yticklabels(devices)
	ax.set_yticks(range(len(devices)))
	
	# Add Legend
	ax.legend(loc=mode_parameters['legendLoc'])
	
	# Adjust X-lim
	includeOriginOnXaxis(ax, include=True, stretchfactor=1)
	
	return (fig, (ax,))
	