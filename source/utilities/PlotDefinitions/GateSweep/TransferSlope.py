from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 40,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'colorMap':'white_orange_black',
		'colorDefault': ['#ee7539'],
		
		'xlabel':'$V_{{GS}}$ (V)',
		'ylabel':      '$g_{{m}}$ (S)',
		'milli_ylabel':'$g_{{m}}$ (mS)',
		'micro_ylabel':'$g_{{m}}$ ($\\mathregular{\\mu}$S)',
		'nano_ylabel': '$g_{{m}}$ (nS)',
		'pico_ylabel': '$g_{{m}}$ (pS)',
		'leg_vds_label':'$V_{{DS}}$  = {:}V',
		'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build Color Map and Color Bar
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')
	
	# Adjust y-scale and y-axis labels 
	max_current = np.max([np.max(deviceRun['Results']['id_data']) for deviceRun in deviceHistory])
	min_current = np.min([np.min(deviceRun['Results']['id_data']) for deviceRun in deviceHistory])
	abs_max_current = max(max_current, abs(min_current))
	max_voltage = np.max([np.max(deviceRun['Results']['vgs_data']) for deviceRun in deviceHistory])
	min_voltage = np.min([np.min(deviceRun['Results']['vgs_data']) for deviceRun in deviceHistory])
	abs_max_voltage = max(max_voltage, abs(min_voltage)) 
	approx_max_value = (abs_max_current/abs_max_voltage if(abs_max_voltage > 0) else abs_max_current) if(mode_parameters['yscale'] is None) else mode_parameters['yscale']
	yscale, ylabel = (1, plotDescription['plotDefaults']['ylabel']) if(approx_max_value >= 1) else ((1e3, plotDescription['plotDefaults']['milli_ylabel']) if(approx_max_value >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_ylabel']) if(approx_max_value >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_ylabel']) if(approx_max_value >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_ylabel']))))

	# Plot
	for i in range(len(deviceHistory)):
		line = plotTransferCurveSlope(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleYaxisBy=yscale, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True), mode_parameters=mode_parameters)

	return (fig, (ax,))
