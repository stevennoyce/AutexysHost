from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 210,
	'dataFileDependencies': ['DrainSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'colorMap':'white_red_black',
		'colorDefault': ['#ed553b'],
		'xlabel':'$V_{{DS}}$ (V)',
		'ylabel':          '$I_{{D}}$ (A)',
		'milli_ylabel':    '$I_{{D}}$ (mA)',
		'micro_ylabel':    '$I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'nano_ylabel':     '$I_{{D}}$ (nA)',
		'pico_ylabel':     '$I_{{D}}$ (pA)',
		'neg_ylabel':      '$-I_{{D}}$ (A)',
		'neg_milli_ylabel':'$-I_{{D}}$ (mA)',
		'neg_micro_ylabel':'$-I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'neg_nano_ylabel': '$-I_{{D}}$ (nA)',
		'neg_pico_ylabel': '$-I_{{D}}$ (pA)',
		'leg_vgs_label':'$V_{{GS}}$\n  = {:}V',
		'leg_vgs_range_label':'$V_{{GS}}^{{min}} = $ {:}V\n'+'$V_{{GS}}^{{max}} = $ {:}V'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build Color Map and Color Bar
	startVGS = ('${:.1f} V$').format(deviceHistory[0]['runConfigs']['DrainSweep']['gateVoltageSetPoint'])
	endVGS = ('${:.1f} V$').format(deviceHistory[-1]['runConfigs']['DrainSweep']['gateVoltageSetPoint'])
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.9, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=[endVGS, '$V_{{GS}}$', startVGS], colorBarAxisLabel='')		
	
	# Adjust y-scale and y-axis labels 
	max_current = np.max([np.max(deviceRun['Results']['id_data']) for deviceRun in deviceHistory])
	min_current = np.min([np.min(deviceRun['Results']['id_data']) for deviceRun in deviceHistory])
	abs_max_current = max(max_current, abs(min_current)) if(mode_parameters['yscale'] is None) else mode_parameters['yscale']
	current_scale, ylabel = (1, plotDescription['plotDefaults']['ylabel']) if(abs_max_current >= 1) else ((1e3, plotDescription['plotDefaults']['milli_ylabel']) if(abs_max_current >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_ylabel']) if(abs_max_current >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_ylabel']) if(abs_max_current >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_ylabel']))))

	# If negative current maximum greater than positive current maximum, flip data
	if(abs(min_current) > max_current):
		current_scale = -current_scale
		ylabel = plotDescription['plotDefaults']['neg_ylabel'] if(abs_max_current >= 1) else (plotDescription['plotDefaults']['neg_milli_ylabel'] if(abs_max_current >= 1e-3) else (plotDescription['plotDefaults']['neg_micro_ylabel'] if(abs_max_current >= 1e-6) else (plotDescription['plotDefaults']['neg_nano_ylabel'] if(abs_max_current >= 1e-9) else (plotDescription['plotDefaults']['neg_pico_ylabel']))))

	# Plot
	for i in range(len(deviceHistory)):
		line = plotOutputCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleYaxisBy=current_scale, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Add Legend and save figure	
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'DrainSweep', mode_parameters, includeVgsSweep=True), mode_parameters=mode_parameters)

	return (fig, (ax,))

