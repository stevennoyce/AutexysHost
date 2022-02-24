from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Resistance',
	'plotCategory': 'device',
	'priority': 10,
	'dataFileDependencies': ['FourPointProbe.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'colorMap':'white_red_black',
		'colorDefault': ['#ed553b'],
		
		'xlabel':'$I$ (A)',
		'ylabel':'$R$ ($\\mathregular{\\Omega}$)',
		'kilo_ylabel':'$R$ (k$\\mathregular{\\Omega}$)',
		'mega_ylabel':'$R$ (M$\\mathregular{\\Omega}$)',
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
	max_voltage = np.max([np.max(deviceRun['Results']['vds_data']) for deviceRun in deviceHistory])
	max_resistance = max_voltage/np.min(np.abs(np.array(deviceHistory[0]['Results']['id_data'])))
	resistance_scale, ylabel = (1e-6, plotDescription['plotDefaults']['mega_ylabel']) if(max_resistance >= 1e6) else ((1e-3, plotDescription['plotDefaults']['kilo_ylabel']) if(max_resistance >= 1e3) else (1, plotDescription['plotDefaults']['ylabel']))
	
	# Plot
	for i in range(len(deviceHistory)):
		line = plotFourPointResistanceCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleYaxisBy=resistance_scale, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Add Legend and save figure
	#addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'DrainSweep', mode_parameters, includeVgsSweep=True), mode_parameters=mode_parameters)

	return (fig, (ax,))
