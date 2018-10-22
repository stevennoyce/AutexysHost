from utilities.MatplotlibUtility import *
import copy



plotDescription = {
	'plotCategory': 'device',
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'includeOrigin':True,
		'colorMap':'magma',
		'colorDefault': '#f2b134',
		'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
		'ylabel':'$I_{{D}}$ [$\\mu$A]',
		'neg_label':'$-I_{{D}}$ [$\\mu$A]',
		'ii_label':'$I_{{D}}$, $I_{{G}}$ [$\\mu$A]',
		'neg_ii_label':'$-I_{{D}}$, $I_{{G}}$ [$\\mu$A]',
		'leg_vds_label':'$V_{{DS}}^{{Sweep}}$\n  = {:}V',
		'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Load Defaults
	plotDescrip_current = copy.deepcopy(plotDescription)

	# Init Figure
	fig, ax = initFigure(1, 1, plotDescrip_current['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
	# Build Color Map and Color Bar
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescrip_current['plotDefaults']['colorDefault'], colorMapName=plotDescrip_current['plotDefaults']['colorMap'], colorMapStart=0.85, colorMapEnd=0, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')		
	
	print((np.array(deviceHistory[0]['Results']['id_data']) < 0).sum())
	
	# If first segment of device history is mostly negative current, flip data
	if((len(deviceHistory) > 0) and ((np.array(deviceHistory[0]['Results']['id_data']) < 0).sum() > (np.array(deviceHistory[0]['Results']['id_data']) >= 0).sum()):
		deviceHistory = scaledData(deviceHistory, 'Results', 'id_data', -1)
		plotDescrip_current['plotDefaults']['ylabel'] = plotDescrip_current['plotDefaults']['neg_label']
	
	# Plot
	for i in range(len(deviceHistory)):
		line = plotTransferCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	axisLabels(ax, x_label=plotDescrip_current['plotDefaults']['xlabel'], y_label=plotDescrip_current['plotDefaults']['ylabel'])

	# Add gate current to axis
	if(mode_parameters['includeGateCurrent']):
		if(len(deviceHistory) == 1):
			gate_colors = [plt.rcParams['axes.prop_cycle'].by_key()['color'][2]]
			gate_linestyle = None
		else:	
			gate_colors = colors
			gate_linestyle = '--'
		for i in range(len(deviceHistory)):
			plotGateCurrent(ax, deviceHistory[i], gate_colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=gate_linestyle, errorBars=mode_parameters['enableErrorBars'])
		if(plotDescrip_current['plotDefaults']['ylabel'] == plotDescrip_current['plotDefaults']['neg_label']):
			plotDescrip_current['plotDefaults']['ylabel'] = plotDescrip_current['plotDefaults']['neg_ii_label']
		else:
			plotDescrip_current['plotDefaults']['ylabel'] = plotDescrip_current['plotDefaults']['ii_label']
		axisLabels(ax, x_label=plotDescrip_current['plotDefaults']['xlabel'], y_label=plotDescrip_current['plotDefaults']['ylabel'])

	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescrip_current['plotDefaults']['includeOrigin'])

	# Add Legend and save figure	
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescrip_current['plotDefaults'], 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True))
	adjustAndSaveFigure(fig, 'FullTransferCurves', mode_parameters)

	return (fig, ax)

