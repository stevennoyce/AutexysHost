from utilities.MatplotlibUtility import *




plotDescription = {
	'plotCategory': 'device',
	'priority': 70,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'colorMap':'white_maroon_black',
		'colorDefault': ['#800000'],
		
		'xlabel':'$V_{{GS}}$ (V)',
		'unity_ylabel':'Hysteresis (V)',
		'milli_ylabel':'Hysteresis (mV)',
		'leg_vds_label':'$V_{{DS}}$  = {:}V',
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
		
	# Adjust y-scale and y-axis labels 
	vgs_fwd, id_fwd, vgs_rev, id_rev = deviceHistory[0]['Results']['vgs_data'][0], deviceHistory[0]['Results']['id_data'][0], deviceHistory[0]['Results']['vgs_data'][1], deviceHistory[0]['Results']['id_data'][1]
	max_hysteresis = np.max(fet_model.FET_Hysteresis(vgs_fwd, id_fwd, vgs_rev, id_rev, noise_floor=1e-10)['H']) if(mode_parameters['yscale'] is None) else mode_parameters['yscale']
	voltage_scale, ylabel = (1, plotDescription['plotDefaults']['unity_ylabel']) if(max_hysteresis >= 1) else (1e3, plotDescription['plotDefaults']['milli_ylabel'])
		
	# Plot
	for i in range(len(deviceHistory)):
		line = plotHysteresisCurve(ax, deviceHistory[i], colors[i], scaleYaxisBy=voltage_scale, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True), mode_parameters=mode_parameters)

	return (fig, (ax,))
