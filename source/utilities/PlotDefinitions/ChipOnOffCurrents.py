from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'chip',
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'xlabel':'Device',
		'ylabel':'$I_{{ON}}$ [$\\mu$A]',
		'ylabel_dual_axis':'$I_{{OFF}}$ [$\\mu$A]'
	},
}
	
def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, mode_parameters=None):
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

	recentOnCurrents, devices, recentOffCurrents = zip(*(reversed(sorted(zip(recentOnCurrents, devices, recentOffCurrents)))))

	# Plot
	if(mode_parameters['includeOffCurrent']):
		line = ax.plot(range(len(devices)), recentOffCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], marker='o', markersize=8, linewidth=0, linestyle=None)[0]
		setLabel(line, 'Off Currents')
	line = ax.plot(range(len(devices)), recentOnCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)[0]
	setLabel(line, 'On Currents')

	# Label axes
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])
	tickLabels(ax, devices, rotation=90)
	
	# Add Legend
	ax.legend(loc=mode_parameters['legendLoc'])
	
	# Save Figure
	adjustAndSaveFigure(fig, 'ChipOnOffCurrents', mode_parameters)
	return (fig, ax)
