from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Differential Resistance',
	'plotCategory': 'device',
	'priority': 240,
	'dataFileDependencies': ['DrainSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeAtLeastOrderOfMagnitudeOnYaxis':True,
		'colorMap':'white_orange_black',
		'colorDefault': ['#ee7539'],
		
		'xlabel':'$V_{{DS}}$ (V)',		
		'ylabel':     '$r_{{ds}}$ ($\\mathregular{\\Omega}$)',
		'kilo_ylabel':'$r_{{ds}}$ (k$\\mathregular{\\Omega}$)',
		'leg_vgs_label':'$V_{{GS}}$  = {:}V',
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
	#max_voltage = max(abs(deviceHistory[0]['runConfigs']['DrainSweep']['drainVoltageStart']), abs(deviceHistory[0]['runConfigs']['DrainSweep']['drainVoltageEnd']))
	#max_resistance = max_voltage/np.min(np.abs(np.array(deviceHistory[0]['Results']['id_data'])))
	#resistance_scale, ylabel = (1e-3, plotDescription['plotDefaults']['kilo_ylabel']) if(max_resistance >= 1e3) else (1, plotDescription['plotDefaults']['ylabel'])
	resistance_scale, ylabel = (1, plotDescription['plotDefaults']['ylabel'])
	
	# Plot
	for i in range(len(deviceHistory)):
		line = plotOutputResistanceCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleYaxisBy=resistance_scale, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'DrainSweep', mode_parameters, includeVgsSweep=True), mode_parameters=mode_parameters)

	return (fig, (ax,))
