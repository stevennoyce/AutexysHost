from utilities.MatplotlibUtility import *



plotDescription = {
	'name':'Chip Experiments',
	'plotCategory': '',#'chip',
	'priority': 1010,
	'dataFileDependencies': ['index.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'automaticAxisLabels':True,
		'xlabel':'Device',
		'ylabel':'Experiments'
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory, mode_parameters=None):
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

	# Label ticks
	tickLabels(ax, devices, rotation=90)

	return (fig, (ax,))

