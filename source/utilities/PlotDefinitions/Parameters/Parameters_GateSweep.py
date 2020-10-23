from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Gate Sweep',
	'plotCategory': 'parameters',
	'priority': 0,
	'dataFileDependencies': ['disabled.json'],
	'plotDefaults': {
		'figsize':(2,2),
		'automaticAxisLabels':True,
		'colorDefault_Drain': ['#3F51B5'],
		'colorDefault_Gate': ['#880E7F'],
		
		'xlabel':'Time',
		'ylabel':'Voltage (V)',
		'legend_labels':['$V_{{DS}}$', '$V_{{GS}}$'],
	},
}

def plot(parameters, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build Color Map and Color Bar
	colors = [plotDescription['plotDefaults']['colorDefault_Drain'][0], plotDescription['plotDefaults']['colorDefault_Gate'][0]]
	
	start      = parameters['runConfigs']['GateSweep']['gateVoltageMinimum']
	end        = parameters['runConfigs']['GateSweep']['gateVoltageMaximum']
	points     = parameters['runConfigs']['GateSweep']['stepsInVGSPerDirection']
	duplicates = parameters['runConfigs']['GateSweep']['pointsPerVGS']
	ramps      = parameters['runConfigs']['GateSweep']['gateVoltageRamps']
	
	drain      = parameters['runConfigs']['GateSweep']['drainVoltageSetPoint']
	
	# Plot Constant Drain Voltage
	line = plotSweepParameters(ax, colors[0], drain, drain, points, duplicates, ramps)
	setLabel(line, plotDescription['plotDefaults']['legend_labels'][0])
	
	# Plot Sweeping Gate Voltage
	line = plotSweepParameters(ax, colors[1], start, end, points, duplicates, ramps)
	setLabel(line, plotDescription['plotDefaults']['legend_labels'][1])

	ax.set_title('Gate Sweep Voltage Waveform')
	ax.set_yticks([0] + [start, end, drain])
	ax.legend(loc='best')

	return (fig, (ax,))
