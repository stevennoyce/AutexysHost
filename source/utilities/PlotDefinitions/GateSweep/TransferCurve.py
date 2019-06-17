from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 10,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'colorMap':'white_blue_black',
		'colorDefault': ['#f2b134'],
		'xlabel':'$V_{{GS}}$ (V)',
		'micro_ylabel':'$I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'nano_ylabel':'$I_{{D}}$ (nA)',
		'pico_ylabel':'$I_{{D}}$ (pA)',
		'neg_micro_ylabel':'$-I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'neg_nano_ylabel':'$-I_{{D}}$ (nA)',
		'neg_pico_ylabel':'$-I_{{D}}$ (pA)',
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
	max_current = np.max(np.abs(np.array(deviceHistory[0]['Results']['id_data'])))
	current_scale, ylabel = (1e6, plotDescription['plotDefaults']['micro_ylabel']) if(max_current >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_ylabel']) if(max_current >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_ylabel']))
	
	# If first segment of device history is mostly negative current, flip data
	if((len(deviceHistory) > 0) and ((np.array(deviceHistory[0]['Results']['id_data']) < 0).sum() > (np.array(deviceHistory[0]['Results']['id_data']) >= 0).sum())):
		deviceHistory = scaledData(deviceHistory, 'Results', 'id_data', -1)
		ylabel = plotDescription['plotDefaults']['neg_micro_ylabel'] if(max_current >= 1e-6) else (plotDescription['plotDefaults']['neg_nano_ylabel'] if(max_current >= 1e-9) else (plotDescription['plotDefaults']['neg_pico_ylabel']))

	# Plot
	for i in range(len(deviceHistory)):
		line = plotTransferCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleYaxisBy=current_scale, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True), mode_parameters=mode_parameters)

	return (fig, (ax,))
