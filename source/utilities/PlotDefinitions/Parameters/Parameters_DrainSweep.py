from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Drain Sweep',
	'plotCategory': 'parameters',
	'priority': 0,
	'dataFileDependencies': [],
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
	
	start      = parameters['runConfigs']['DrainSweep']['drainVoltageMinimum']
	end        = parameters['runConfigs']['DrainSweep']['drainVoltageMaximum']
	points     = parameters['runConfigs']['DrainSweep']['stepsInVDSPerDirection']
	duplicates = parameters['runConfigs']['DrainSweep']['pointsPerVDS']
	ramps      = parameters['runConfigs']['DrainSweep']['drainVoltageRamps']
	
	gate       = parameters['runConfigs']['DrainSweep']['gateVoltageSetPoint']
	
	# Plot Sweeping Drain Voltage
	line = plotSweepParameters(ax, colors[0], start, end, points, duplicates, ramps)
	setLabel(line, plotDescription['plotDefaults']['legend_labels'][0])
	
	# Plot Constant Gate Voltage
	line = plotSweepParameters(ax, colors[1], gate, gate, points, duplicates, ramps)
	setLabel(line, plotDescription['plotDefaults']['legend_labels'][1])
	
	ax.set_title('Drain Sweep Voltage Waveform')
	ax.set_yticks([0] + [start, end, gate])
	ax.legend(loc='best')

	return (fig, (ax,))
