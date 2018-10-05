from utilities.MatplotlibUtility import *



plotDescription = {
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'colorMap':'plasma',
		'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][0],
		'xlabel':'$V_{{DS}}^{{Sweep}}$ [V]',
		'ylabel':'$I_{{D}}$ [$\\mu$A]',
		'neg_label':'$-I_{{D}}$ [$\\mu$A]',
		'leg_vgs_label':'$V_{{GS}}^{{Sweep}}$\n  = {:}V',
		'leg_vgs_range_label':'$V_{{GS}}^{{min}} = $ {:}V\n'+'$V_{{GS}}^{{max}} = $ {:}V'
	},
	'dataFileNames': ['DrainSweep.json']
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))

	# Build Color Map and Color Bar
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0, colorMapEnd=0.87, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')		
	
	# If first segment of device history is mostly negative current, flip data
	if((len(deviceHistory) > 0) and (np.percentile(deviceHistory[0]['Results']['id_data'], 75) < 0)):
		deviceHistory = scaledData(deviceHistory, 'Results', 'id_data', -1)
		plotDescription['plotDefaults']['ylabel'] = plotDescription['plotDefaults']['neg_label']
	
	# Plot
	for i in range(len(deviceHistory)):
		line = plotOutputCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])

	# Add Legend and save figure	
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'DrainSweep', mode_parameters, includeVgsSweep=True))
	adjustAndSaveFigure(fig, 'FullOutputCurves', mode_parameters)

	return (fig, ax)

