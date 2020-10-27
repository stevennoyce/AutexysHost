from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Auto Drain Sweep',
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
	
	start      = parameters['runConfigs']['DrainSweep']['drainVoltageMinimum']
	end        = parameters['runConfigs']['DrainSweep']['drainVoltageMaximum']
	points     = parameters['runConfigs']['DrainSweep']['stepsInVDSPerDirection']
	duplicates = parameters['runConfigs']['DrainSweep']['pointsPerVDS']
	ramps      = parameters['runConfigs']['DrainSweep']['drainVoltageRamps']
	
	gates       = parameters['runConfigs']['AutoDrainSweep']['gateVoltageSetPoints'] if(len(parameters['runConfigs']['AutoDrainSweep']['gateVoltageSetPoints']) > 0) else [parameters['runConfigs']['DrainSweep']['gateVoltageSetPoint']]
	
	# Plot Sweeping Drain Voltage
	for i in range(len(gates)*parameters['runConfigs']['AutoDrainSweep']['sweepsPerVGS']):
		line = plotSweepParameters(ax, colors[0], start, end, points, duplicates, ramps, time_offset=i)
	setLabel(line, plotDescription['plotDefaults']['legend_labels'][0])
	
	# Plot Constant Gate Voltage
	for i,gate in enumerate(gates):
		for j in range(parameters['runConfigs']['AutoDrainSweep']['sweepsPerVGS']):
			line = plotSweepParameters(ax, colors[1], gate, gate, points, duplicates, ramps, time_offset=i*parameters['runConfigs']['AutoDrainSweep']['sweepsPerVGS']+j)
	setLabel(line, plotDescription['plotDefaults']['legend_labels'][1])
	
	ax.set_title('Drain Sweep Voltage Waveform')
	ax.set_yticks([0] + [start, end] + gates)
	ax.legend(loc='best', title='Sweeps: {:}'.format(len(gates)*parameters['runConfigs']['AutoDrainSweep']['sweepsPerVGS']))

	return (fig, (ax,))
