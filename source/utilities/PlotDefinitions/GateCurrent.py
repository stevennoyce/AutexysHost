from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOrigin':False,
		'colorMap':'white_green_black',
		'colorDefault': ['#4FB99F'],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
		'ylabel':'$I_{{G}}$ [$\\mu$A]',
		'nano_ylabel':'$I_{{G}}$ [nA]',
		'leg_vds_label':'$V_{{DS}}^{{Sweep}} = ${:}V',
		'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V'
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
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.1, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')		
	
	ylabel=plotDescription['plotDefaults']['ylabel']
	
	# Plot
	# If the maximum current is smaller than one microamp, change the unit to nanoamp
	if(np.max(np.abs(np.array(deviceHistory[0]['Results']['ig_data'])))>= 1e-6):
		for i in range(len(deviceHistory)):
			line = plotGateCurrent(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
			if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
				setLabel(line, mode_parameters['legendLabels'][i])
	else:
		ylabel = plotDescription['plotDefaults']['nano_ylabel']
		for i in range(len(deviceHistory)):
			line = plotGateCurrent(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e9, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
			if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
				setLabel(line, mode_parameters['legendLabels'][i])

	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOrigin'])

	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True))
	adjustAndSaveFigure(fig, 'FullGateCurrents', mode_parameters)

	return (fig, ax)
	
	

