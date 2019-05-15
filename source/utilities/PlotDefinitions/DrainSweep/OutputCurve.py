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
		'ylabel':'$I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'neg_ylabel':'$-I_{{D}}$ ($\\mathregular{\\mu}$A)',
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
	
	# If first segment of device history is mostly negative current, flip data
	ylabel = plotDescription['plotDefaults']['ylabel']
	if((len(deviceHistory) > 0) and ((np.array(deviceHistory[0]['Results']['id_data']) < 0).sum() > (np.array(deviceHistory[0]['Results']['id_data']) >= 0).sum())):
		deviceHistory = scaledData(deviceHistory, 'Results', 'id_data', -1)
		ylabel = plotDescription['plotDefaults']['neg_ylabel']
	
	# Plot
	for i in range(len(deviceHistory)):
		line = plotOutputCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Add Legend and save figure	
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'DrainSweep', mode_parameters, includeVgsSweep=True), mode_parameters=mode_parameters)

	return (fig, (ax,))

