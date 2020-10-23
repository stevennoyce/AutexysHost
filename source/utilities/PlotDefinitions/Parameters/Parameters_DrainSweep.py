from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Drain Sweep',
	'plotCategory': 'parameters',
	'priority': 0,
	'dataFileDependencies': [],
	'plotDefaults': {
		'figsize':(2,2),
		'automaticAxisLabels':True,
		'colorMap':'white_red_black',
		'colorDefault': ['#3F51B5'],
		
		'xlabel':'Time',
		'ylabel':'$V_{{DS}}$ (V)',
	},
}

def plot(parameters, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build Color Map and Color Bar
	data_sets_collected = 1
	colors = setupColors(fig, data_sets_collected, colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False)
	
	start      = parameters['runConfigs']['DrainSweep']['drainVoltageMinimum']
	end        = parameters['runConfigs']['DrainSweep']['drainVoltageMaximum']
	points     = parameters['runConfigs']['DrainSweep']['stepsInVDSPerDirection']
	duplicates = parameters['runConfigs']['DrainSweep']['pointsPerVDS']
	ramps      = parameters['runConfigs']['DrainSweep']['drainVoltageRamps']
	
	# Plot
	for i in range(data_sets_collected):
		line = plotSweepParameters(ax, colors[i], start, end, points, duplicates, ramps)

	ax.set_title('Drain Voltage Waveform')

	return (fig, (ax,))
