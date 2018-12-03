from utilities.MatplotlibUtility import *
import copy



plotDescription = {
	'plotCategory': 'device',
	'dataFileDependencies': ['InverterSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOrigin':True,
		'colorMap':'white_blue_black',
		'colorDefault': ['#56638A'],
		'xlabel':'$V_{{IN}}$ (V)',
		'ylabel':'$V_{{OUT}}$ (V)',
		'leg_vds_label':'$V_{{DD}}$  = {:}V',
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
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescrip_current['plotDefaults']['colorDefault'], colorMapName=plotDescrip_current['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')		
		
	# Plot
	for i in range(len(deviceHistory)):
		line = plotInverterVTC(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	axisLabels(ax, x_label=plotDescrip_current['plotDefaults']['xlabel'], y_label=plotDescrip_current['plotDefaults']['ylabel'])

	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescrip_current['plotDefaults']['includeOrigin'])

	# Add Legend and save figure	
	#addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescrip_current['plotDefaults'], 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True, includeIdVgsFit=True), mode_parameters=mode_parameters)
	adjustAndSaveFigure(fig, 'InverterVTC', mode_parameters)

	return (fig, ax)

