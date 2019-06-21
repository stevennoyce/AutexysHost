from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 220,
	'dataFileDependencies': ['DrainSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':False,
		'colorMap':'white_green_black',
		'colorDefault': ['#4FB99F'],
		'xlabel':'$V_{{DS}}$ (V)',
		'ylabel':'$I_{{G}}$ (A)',
		'micro_ylabel':'$I_{{G}}$ ($\\mathregular{\\mu}$A)',
		'nano_ylabel':'$I_{{G}}$ (nA)',
		'pico_ylabel':'$I_{{G}}$ (pA)',
		'leg_vgs_label':'$V_{{GS}} = ${:}V',
		'leg_vgs_range_label':'$V_{{GS}}^{{min}} = $ {:}V\n'+'$V_{{GS}}^{{max}} = $ {:}V'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build Color Map and Color Bar
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.1, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')

	# Adjust y-scale and y-axis labels 
	max_current = np.max([np.max(deviceRun['Results']['ig_data']) for deviceRun in deviceHistory])
	min_current = np.min([np.min(deviceRun['Results']['ig_data']) for deviceRun in deviceHistory])
	abs_max_current = max(max_current, abs(min_current))
	current_scale, ylabel = (1, plotDescription['plotDefaults']['ylabel']) if(abs_max_current >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_ylabel']) if(abs_max_current >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_ylabel']) if(abs_max_current >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_ylabel'])))

	# Plot
	for i in range(len(deviceHistory)):
		line = plotOutputGateCurrent(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleYaxisBy=current_scale, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
	
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'DrainSweep', mode_parameters, includeVgsSweep=True), mode_parameters=mode_parameters)

	return (fig, (ax,))
