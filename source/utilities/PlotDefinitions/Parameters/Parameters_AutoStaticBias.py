from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Auto Static Bias',
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
	colors = [plotDescription['plotDefaults']['colorDefault_Drain'][0], plotDescription['plotDefaults']['colorDefault_Gate'][0]]
	
	sb_parameters  = parameters['runConfigs']['StaticBias']
	asb_parameters = parameters['runConfigs']['AutoStaticBias']
	
	importantListLengths = [len(asb_parameters['biasTimeList']), len(asb_parameters['gateVoltageSetPointList']), len(asb_parameters['drainVoltageSetPointList']), len(asb_parameters['gateVoltageWhenDoneList']), len(asb_parameters['drainVoltageWhenDoneList']), len(asb_parameters['delayWhenDoneList'])]
	numberOfStaticBiases = max(asb_parameters['numberOfStaticBiases'], max(importantListLengths))
	
	drainVoltages 	= asb_parameters['drainVoltageSetPointList'] 	+ [sb_parameters['drainVoltageSetPoint']]*(numberOfStaticBiases-len(asb_parameters['drainVoltageSetPointList']))
	gateVoltages 	= asb_parameters['gateVoltageSetPointList'] 	+ [sb_parameters['gateVoltageSetPoint']] *(numberOfStaticBiases-len(asb_parameters['gateVoltageSetPointList']))
	durations 		= asb_parameters['biasTimeList'] 				+ [sb_parameters['totalBiasTime']]       *(numberOfStaticBiases-len(asb_parameters['biasTimeList']))
	
	measurementTime = parameters['runConfigs']['StaticBias']['measurementTime']
	
	# Plot Constant Drain Voltages
	time_elapsed = 0
	for i in range(len(drainVoltages)):
		line = plotStaticParameter(ax, colors[0], drainVoltages[i], durations[i], measurementTime, time_offset=time_elapsed)
		time_elapsed += durations[i]
	setLabel(line, plotDescription['plotDefaults']['legend_labels'][0])
	
	# Plot Constant Gate Voltages
	time_elapsed = 0
	for i in range(len(gateVoltages)):
		line = plotStaticParameter(ax, colors[1], gateVoltages[i], durations[i], measurementTime, time_offset=time_elapsed)
		time_elapsed += durations[i]
	setLabel(line, plotDescription['plotDefaults']['legend_labels'][1])

	ax.set_title('Static Voltage Waveforms')
	ax.set_yticks([0] + drainVoltages + gateVoltages)
	ax.legend(loc='best', title='Segments: {:}'.format(numberOfStaticBiases))

	return (fig, (ax,))
