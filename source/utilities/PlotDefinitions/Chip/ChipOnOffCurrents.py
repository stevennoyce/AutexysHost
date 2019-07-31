from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'chip',
	'priority': 1010,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'automaticAxisLabels':True,
		'xlabel':'Device',
		'ylabel':'$I_{{D}}$ ($\\mathregular{\\mu}$A)',
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

	recentOnCurrents, devices, recentOffCurrents = zip(*(reversed(sorted(zip(recentOnCurrents, devices, recentOffCurrents)))))

	# Plot
	line1 = ax.plot(range(len(devices)), recentOffCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], marker='o', markersize=8, linewidth=0, linestyle=None)[0]	
	line2 = ax.plot(range(len(devices)), recentOnCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)[0]

	# Set tick labels
	tickLabels(ax, devices, rotation=90)
	
	# Add Legend
	ax.legend([line1, line2], [plotDescription['plotDefaults']['leg_label1'], plotDescription['plotDefaults']['leg_label2']], loc=mode_parameters['legendLoc'])
	
	return (fig, (ax,))
