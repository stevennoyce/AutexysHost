from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'chip',
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'xlabel':'Device',
		'ylabel':'On/Off Ratio, (Order of Mag)'
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

	lastOnOffRatios, devices, firstOnOffRatios = zip(*(reversed(sorted(zip(lastOnOffRatios, devices, firstOnOffRatios)))))

	# Plot
	line = ax.plot(range(len(devices)), firstOnOffRatios, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], marker='o', markersize=6, linewidth=0, linestyle=None)[0]
	setLabel(line, 'First Run')
	line = ax.plot(range(len(devices)), lastOnOffRatios, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)[0]
	setLabel(line, 'Most Recent Run')

	# Label axes
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])
	tickLabels(ax, devices, rotation=90)
	
	# Add Legend and save figure
	ax.legend(loc=mode_parameters['legendLoc'])
	adjustAndSaveFigure(fig, 'ChipOnOffRatios', mode_parameters)
	return (fig, ax)
	