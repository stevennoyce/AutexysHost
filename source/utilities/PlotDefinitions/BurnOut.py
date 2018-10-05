from utilities.MatplotlibUtility import *



plotDescription = {
	'plotDefaults': {
		'figsize':(8,4.5),
		'subplot_height_ratio':[1],
		'subplot_width_ratio':[1,1],
		'colorMap':'hot',
		'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][0],
		'vds_label':'$V_{{DS}}$ [V]',
		'id_micro_label':'$I_{{D}}$ [$\\mu$A]',
		'time_label':'Time [sec]',
		'id_annotation':'burn current',
		'legend_title':'$V_{{GS}}$ = {:}V'
	},
	'dataFileNames': ['BurnOut.json']
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure	
	fig, (ax1, ax2) = initFigure(1, 2, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'], shareX=False, subplotWidthRatio=plotDescription['plotDefaults']['subplot_width_ratio'], subplotHeightRatio=plotDescription['plotDefaults']['subplot_height_ratio'])
	ax2 = plt.subplot(222)
	ax3 = plt.subplot(224)
	if(not mode_parameters['publication_mode']):
		ax1.set_title(getTestLabel(deviceHistory, identifiers))

	# Build Color Map and Color Bar
	plt.sca(ax1)
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.7, colorMapEnd=0, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,1], colorBarTickLabels=['Final', 'Initial'], colorBarAxisLabel='Burnouts')		

	# Plot
	for i in range(len(deviceHistory)):
		plotBurnOut(ax1, ax2, ax3, deviceHistory[i], colors[i], lineStyle=None, annotate=False, annotation=plotDescription['plotDefaults']['id_annotation'])

	axisLabels(ax1, x_label=plotDescription['plotDefaults']['vds_label'], y_label=plotDescription['plotDefaults']['id_micro_label'])
	axisLabels(ax2, x_label=plotDescription['plotDefaults']['time_label'], y_label=plotDescription['plotDefaults']['id_micro_label'])
	axisLabels(ax3, x_label=plotDescription['plotDefaults']['time_label'], y_label=plotDescription['plotDefaults']['vds_label'])

	# Add Legend and save figure
	addLegend(ax1, loc=mode_parameters['legendLoc'], title=plotDescription['plotDefaults']['legend_title'].format(np.mean([deviceRun['runConfigs']['BurnOut']['gateVoltageSetPoint'] for deviceRun in deviceHistory])))
	addLegend(ax2, loc=mode_parameters['legendLoc'], title=plotDescription['plotDefaults']['legend_title'].format(np.mean([deviceRun['runConfigs']['BurnOut']['gateVoltageSetPoint'] for deviceRun in deviceHistory])))
	addLegend(ax3, loc=mode_parameters['legendLoc'], title=plotDescription['plotDefaults']['legend_title'].format(np.mean([deviceRun['runConfigs']['BurnOut']['gateVoltageSetPoint'] for deviceRun in deviceHistory])))
	adjustAndSaveFigure(fig, 'FullBurnOut', mode_parameters, subplotWidthPad=0.25, subplotHeightPad=0.8)

	return (fig, (ax1, ax2, ax3))

