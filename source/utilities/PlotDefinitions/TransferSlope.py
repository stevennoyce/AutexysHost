from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 40,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOrigin':True,
		'colorMap':'white_blue_black',
		'colorDefault': ['#f2b134'],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ (V)',
		'micro_ylabel':'$g_{{m}}$ ($\\mu$S)',
		'nano_ylabel':'$g_{{m}}$ (nS)',
		'neg_micro_ylabel':'$g_{{m}}$ ($\\mu$S)',
		'neg_nano_ylabel':'$g_{{m}}$ (nS)',
		'leg_vds_label':'$V_{{DS}}^{{Sweep}}$  = {:}V',
		'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))

	# Build Color Map and Color Bar
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')
		
	# Adjust y-scale and y-axis labels 
	max_current = np.max(np.abs(np.array(deviceHistory[0]['Results']['id_data'])))
	current_scale, ylabel = (1e6, plotDescription['plotDefaults']['micro_ylabel']) if(max_current >= 1e-6) else (1e9, plotDescription['plotDefaults']['nano_ylabel'])
	
	# If first segment of device history is mostly negative current, flip data
	if((len(deviceHistory) > 0) and ((np.array(deviceHistory[0]['Results']['id_data']) < 0).sum() > (np.array(deviceHistory[0]['Results']['id_data']) >= 0).sum())):
		deviceHistory = scaledData(deviceHistory, 'Results', 'id_data', -1)
		ylabel = plotDescription['plotDefaults']['neg_micro_ylabel'] if(max_current >= 1e-6) else (plotDescription['plotDefaults']['neg_nano_ylabel'])

	# Plot
	for i in range(len(deviceHistory)):
		line = plotTransferCurveSlope(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=current_scale, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Add gate current to axis
	if(mode_parameters['includeGateCurrent']):
		if(len(deviceHistory) == 1):
			gate_colors = [plt.rcParams['axes.prop_cycle'].by_key()['color'][2]]
			gate_linestyle = None
		else:
			gate_colors = colors
			gate_linestyle = '--'
		for i in range(len(deviceHistory)):
			plotGateCurrent(ax, deviceHistory[i], gate_colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=current_scale, lineStyle=gate_linestyle, errorBars=mode_parameters['enableErrorBars'])

	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOrigin'])

	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True, includeIdVgsFit=True), mode_parameters=mode_parameters)
	adjustAndSaveFigure(fig, 'TransferCurve', mode_parameters)

	return (fig, ax)
