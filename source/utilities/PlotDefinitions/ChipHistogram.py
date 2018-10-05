from utilities.MatplotlibUtility import *



plotDescription = {
	'plotDefaults': {
		'figsize':(5,4),
		'xlabel':'Device',
		'ylabel':'Experiments'
	},
	'dataFileNames': []
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build index, experiment lists
	devices = list(chipIndexes.keys())
	deviceExperiments = len(devices)*[0]
	for device, indexData in chipIndexes.items():
		deviceExperiments[devices.index(device)] = indexData['experimentNumber']
	
	deviceExperiments, devices = zip(*(reversed(sorted(zip(deviceExperiments, devices)))))

	# Plot
	ax.bar(devices, deviceExperiments)

	# Label axes
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])
	tickLabels(ax, devices, rotation=90)

	# Save figure
	adjustAndSaveFigure(fig, 'ChipHistogram', mode_parameters)
	return (fig, ax)

