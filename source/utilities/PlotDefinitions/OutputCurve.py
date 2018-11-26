from utilities.MatplotlibUtility import *
import copy



plotDescription = {
	'plotCategory': 'device',
	'dataFileDependencies': ['DrainSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'colorMap':'white_red_black',
		'colorDefault': ['#ed553b'],
		'xlabel':'$V_{{DS}}^{{Sweep}}$ [V]',
		'ylabel':'$I_{{D}}$ [$\\mu$A]',
		'neg_label':'$-I_{{D}}$ [$\\mu$A]',
		'leg_vgs_label':'$V_{{GS}}^{{Sweep}}$\n  = {:}V',
		'leg_vgs_range_label':'$V_{{GS}}^{{min}} = $ {:}V\n'+'$V_{{GS}}^{{max}} = $ {:}V'
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
	startVGS = ('${:.1f} V$').format(deviceHistory[0]['runConfigs']['DrainSweep']['gateVoltageSetPoint'])
	endVGS = ('${:.1f} V$').format(deviceHistory[-1]['runConfigs']['DrainSweep']['gateVoltageSetPoint'])
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescrip_current['plotDefaults']['colorDefault'], colorMapName=plotDescrip_current['plotDefaults']['colorMap'], colorMapStart=1.0, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=[endVGS, '$V_{{GS}}$', startVGS], colorBarAxisLabel='')		
	
	# If first segment of device history is mostly negative current, flip data
	if((len(deviceHistory) > 0) and ((np.array(deviceHistory[0]['Results']['id_data']) < 0).sum() > (np.array(deviceHistory[0]['Results']['id_data']) >= 0).sum())):
		deviceHistory = scaledData(deviceHistory, 'Results', 'id_data', -1)
		plotDescrip_current['plotDefaults']['ylabel'] = plotDescrip_current['plotDefaults']['neg_label']
	
	# Plot
	for i in range(len(deviceHistory)):
		line = plotOutputCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	axisLabels(ax, x_label=plotDescrip_current['plotDefaults']['xlabel'], y_label=plotDescrip_current['plotDefaults']['ylabel'])

	# Add Legend and save figure	
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescrip_current['plotDefaults'], 'runConfigs', 'DrainSweep', mode_parameters, includeVgsSweep=True), mode_parameters=mode_parameters)
	adjustAndSaveFigure(fig, 'OutputCurve', mode_parameters)

	return (fig, ax)

