from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Small Signal',
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
	
	drainVoltageSetPoint  = parameters['runConfigs']['SmallSignal']['drainVoltageSetPoint']
	gateVoltageSetPoint   = parameters['runConfigs']['SmallSignal']['gateVoltageSetPoint']
	drainVoltageAmplitude = parameters['runConfigs']['SmallSignal']['drainVoltageAmplitude']
	gateVoltageAmplitude  = parameters['runConfigs']['SmallSignal']['gateVoltageAmplitude']
	frequencies           = parameters['runConfigs']['SmallSignal']['frequencies']
	periods               = parameters['runConfigs']['SmallSignal']['periods']
	stepsPerPeriod        = parameters['runConfigs']['SmallSignal']['stepsPerPeriod']
	
	# Plot
	for i in range(waverforms):
		line = plotSmallSignalParameter(ax, colors[i], [drainVoltageSetPoint, gateVoltageSetPoint][i], [drainVoltageAmplitude, gateVoltageAmplitude][i], periods, stepsPerPeriod, frequencies)
		setLabel(line, plotDescription['plotDefaults']['legend_labels'][i])

	ax.set_title('Small Signal Voltage Waveforms')
	ax.set_yticks([0] + [drainVoltageSetPoint, gateVoltageSetPoint, drainVoltageSetPoint + drainVoltageAmplitude, drainVoltageSetPoint - drainVoltageAmplitude, gateVoltageSetPoint + gateVoltageAmplitude, gateVoltageSetPoint - gateVoltageAmplitude])
	ax.legend(loc='best')

	return (fig, (ax,))
