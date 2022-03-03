from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Voltage',
	'plotCategory': 'device',
	'priority': 10,
	'dataFileDependencies': ['FourPointProbe.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':False,
		'colorMap':'white_red_black',
		'colorDefault': ['#ed553b'],
		
		'xlabel':'$I$ (A)',
		'ylabel':'$V$ (mV)',
		'leg_vds_label':'$V = ${:}V',
		'leg_vds_range_label':'$V^{{min}} = $ {:}V\n'+'$V^{{max}} = $ {:}V'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
    # Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build Color Map and Color Bar
	# startI = ('${:.1f} V$').format(deviceHistory[0]['runConfigs']['FourPointProbe']['gateCurrentSetPoint'])
	# endI = ('${:.1f} V$').format(deviceHistory[-1]['runConfigs']['FourPointProbe']['gateCurrentSetPoint'])
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.9, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1])#, colorBarTickLabels=[endI, '$I$', startI], colorBarAxisLabel='')		
		
	# Adjust y-scale and y-axis labels 
	voltage_scale = 1000

	# Plot
	for i in range(len(deviceHistory)):
		line = plotFourPointVoltageCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleYaxisBy=voltage_scale, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])

	# Add Legend and save figure
	#addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'DrainSweep', mode_parameters, includeVgsSweep=True), mode_parameters=mode_parameters)

	return (fig, (ax,))
