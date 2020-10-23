from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Static Bias',
	'plotCategory': 'parameters',
	'priority': 0,
	'dataFileDependencies': [],
	'plotDefaults': {
		'figsize':(2,2),
		'automaticAxisLabels':True,
		'colorMap':'white_blue_black',
		'colorDefault1': ['#3F51B5'],
		'colorDefault2': ['#880E7F'],
		
		'xlabel':'Time (s)',
		'ylabel':'Voltage (V)',
		'legend_labels':['$V_{{DS}}$', '$V_{{GS}}$'],
	},
}

def plot(parameters, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build Color Map and Color Bar
	waverforms = 2
	colors = setupColors(fig, waverforms, colorOverride=[plotDescription['plotDefaults']['colorDefault1'][0], plotDescription['plotDefaults']['colorDefault2'][0]], colorDefault=plotDescription['plotDefaults']['colorDefault1'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False)
	
	drainVoltage    = parameters['runConfigs']['StaticBias']['drainVoltageSetPoint']
	gateVoltage     = parameters['runConfigs']['StaticBias']['gateVoltageSetPoint']
	duration        = parameters['runConfigs']['StaticBias']['totalBiasTime']
	measurementTime = parameters['runConfigs']['StaticBias']['measurementTime']
	
	# Plot
	for i in range(waverforms):
		line = plotStaticParameter(ax, colors[i], [drainVoltage, gateVoltage][i], duration, measurementTime)
		setLabel(line, plotDescription['plotDefaults']['legend_labels'][i])

	ax.set_title('Static Voltage Waveforms')
	ax.set_yticks([drainVoltage, gateVoltage, 0])
	ax.legend(loc='best')

	return (fig, (ax,))
