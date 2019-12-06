from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'chip',
	'priority': 1020,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.75,4.5),
		'automaticAxisLabels':True,
		'xlabel':'$I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'ylabel':'Device',
		'leg_label1':'Off Currents',
		'leg_label2':'On Currents',
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

	# Plot
	line1 = ax.plot(recentOffCurrents, range(len(devices)), color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], marker='o', markersize=8, linewidth=0, linestyle=None)[0]	
	line2 = ax.plot(recentOnCurrents,  range(len(devices)), color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)[0]

	# Set tick labels
	ax.set_yticklabels(devices)
	ax.set_yticks(range(len(devices)))
	
	# Add Legend
	ax.legend([line1, line2], [plotDescription['plotDefaults']['leg_label1'], plotDescription['plotDefaults']['leg_label2']], loc=mode_parameters['legendLoc'])
	
	return (fig, (ax,))
