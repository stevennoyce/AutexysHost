from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Rapid Bias',
	'plotCategory': 'parameters',
	'priority': 0,
	'dataFileDependencies': [],
	'plotDefaults': {
		'figsize':(2,2),
		'automaticAxisLabels':True,
		'colorMap':'white_blue_black',
		'colorDefault1': ['#3F51B5'],
		'colorDefault2': ['#880E7F'],
		
		'xlabel':'Time',
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
	
	waveform              = parameters['runConfigs']['RapidBias']['waveform']
	drainVoltageSetPoints = parameters['runConfigs']['RapidBias']['drainVoltageSetPoints']
	gateVoltageSetPoints  = parameters['runConfigs']['RapidBias']['gateVoltageSetPoints']
	measurementPoints     = parameters['runConfigs']['RapidBias']['measurementPoints']
	maxStepInVDS          = parameters['runConfigs']['RapidBias']['maxStepInVDS']
	maxStepInVGS          = parameters['runConfigs']['RapidBias']['maxStepInVGS']
	
	# Plot
	for i in range(waverforms):
		line = plotRapidParameter(ax, colors[i], waveform, [drainVoltageSetPoints, gateVoltageSetPoints][i], measurementPoints, [maxStepInVDS, maxStepInVGS][i], other_length=[len(gateVoltageSetPoints), len(drainVoltageSetPoints)][i])
		setLabel(line, plotDescription['plotDefaults']['legend_labels'][i])

	ax.set_title('Rapid Voltage Waveforms')
	ax.set_yticks([0]+drainVoltageSetPoints+gateVoltageSetPoints)
	ax.legend(loc='best')

	return (fig, (ax,))
