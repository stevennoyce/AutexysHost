from utilities.MatplotlibUtility import *
from utilities import FET_Modeling as fet_model



plotDescription = {
	'plotCategory': 'device',
	'priority': 60,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'automaticAxisLabels':True,
		'colorMap':'white_purple_black',
		'colorDefault': ['#7363af'],
		
		'xlabel':'|$I_{{D}}$| (A)',
		'ylabel':'SS (mV/dec)',
		'leg_vds_label':'$V_{{DS}}^{{Sweep}}$  = {:}V',
		'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build Color Map and Color Bar
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')
		
	# Plot
	for i in range(len(deviceHistory)):
		line = plotSubthresholdCurveSlope(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], lineStyle=None, errorBars=mode_parameters['enableErrorBars'], x_axis='drain current')
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	ax.set_xscale('log')
	
	# Set Y-lim based on miniumum SS
	directions = ([0]) if(mode_parameters['sweepDirection'] == 'forward') else (([1]) if(mode_parameters['sweepDirection'] == 'reverse') else([0,1]))
	vgs_data_list = [deviceRun['Results']['vgs_data'][i]  for deviceRun in deviceHistory for i in directions]
	id_data_list  = [deviceRun['Results']['id_data'][i]   for deviceRun in deviceHistory for i in directions]
	metrics = fet_model.FET_Metrics_Multiple(vgs_data_list, id_data_list)
	SS_list = metrics['SS_mV_dec']
	ax.set_ylim(bottom=0, top=5*min(SS_list))

	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True, includeIdVgsFit=True), mode_parameters=mode_parameters)

	return (fig, (ax,))
