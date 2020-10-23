from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Gate Sweep',
	'plotCategory': 'parameters',
	'priority': 0,
	'dataFileDependencies': [],
	'plotDefaults': {
		'figsize':(2,2),
		'automaticAxisLabels':True,
		'colorMap':'white_blue_black',
		'colorDefault': ['#880E7F'],
		
		'xlabel':'Time',
		'ylabel':'$V_{{GS}}$ (V)',
	},
}

def plot(parameters, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build Color Map and Color Bar
	waveforms = 1
	colors = setupColors(fig, waveforms, colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False)
	
	start      = parameters['runConfigs']['GateSweep']['gateVoltageMinimum']
	end        = parameters['runConfigs']['GateSweep']['gateVoltageMaximum']
	points     = parameters['runConfigs']['GateSweep']['stepsInVGSPerDirection']
	duplicates = parameters['runConfigs']['GateSweep']['pointsPerVGS']
	ramps      = parameters['runConfigs']['GateSweep']['gateVoltageRamps']
	
	# Plot
	for i in range(waveforms):
		line = plotSweepParameters(ax, colors[i], start, end, points, duplicates, ramps)

	ax.set_title('Gate Voltage Waveform')

	return (fig, (ax,))
