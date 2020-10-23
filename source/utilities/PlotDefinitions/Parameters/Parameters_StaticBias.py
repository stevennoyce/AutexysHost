from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Static Bias',
	'plotCategory': 'parameters',
	'priority': 0,
	'dataFileDependencies': ['disabled.json'],
	'plotDefaults': {
		'figsize':(2,2),
		'automaticAxisLabels':True,
		'colorDefault_Drain': ['#3F51B5'],
		'colorDefault_Gate': ['#880E7F'],
		
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
	colors = [plotDescription['plotDefaults']['colorDefault_Drain'][0], plotDescription['plotDefaults']['colorDefault_Gate'][0]]
	
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
