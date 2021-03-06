from utilities.MatplotlibUtility import *
from utilities import FET_Modeling as fet_model



plotDescription = {
	'plotCategory': 'device',
	'priority': 4010,
	'dataFileDependencies': ['GateSweep.json', 'disabled.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'colorMap':'white_yellow_black',
		'colorDefault': ['#1f77b4'],
		
		'xlabel':'$V_{{GS}}$ (V)',
		'ylabel':'$I_{{D}}$ ($\\mu$A)',
		'neg_ylabel':'$-I_{{D}}$ ($\\mu$A)'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	ax2 = ax.twinx()
	
	# Optional parameters to set the length of the regions that get fit for SS and gm
	ss_region_length_override = None
	gm_region_length_override = None
	
	# If first segment of device history is mostly negative current, flip data
	ylabel = plotDescription['plotDefaults']['ylabel']
	if((len(deviceHistory) > 0) and ((np.array(deviceHistory[0]['Results']['id_data']) < 0).sum() > (np.array(deviceHistory[0]['Results']['id_data']) >= 0).sum())):
		deviceHistory = scaledData(deviceHistory, 'Results', 'id_data', -1)
		ylabel = plotDescription['plotDefaults']['neg_ylabel']
	
	# Compute device metrics
	all_fitted_values = {'fwd_id_fitted':[], 'rev_id_fitted':[]}
	for deviceRun in deviceHistory:
		if(mode_parameters['sweepDirection'] in ['both', 'forward']):
			fwd_id_fitted = fet_model.FET_Fit_Simple(deviceRun['Results']['vgs_data'][0], deviceRun['Results']['id_data'][0], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'], gm_region_length_override=gm_region_length_override, ss_region_length_override=ss_region_length_override)
			all_fitted_values['fwd_id_fitted'].append(fwd_id_fitted)
		if(mode_parameters['sweepDirection'] in ['both', 'reverse']):
			rev_id_fitted = fet_model.FET_Fit_Simple(deviceRun['Results']['vgs_data'][1], deviceRun['Results']['id_data'][1], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'], gm_region_length_override=gm_region_length_override, ss_region_length_override=ss_region_length_override)
			all_fitted_values['rev_id_fitted'].append(rev_id_fitted)
	
	# Build Color Map and Color Bar	
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')			
	
	# Plot
	for i in range(len(deviceHistory)):
		# Plot transfer curve fit to show g_m
		line = plotTransferCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleYaxisBy=1e6, lineStyle='', errorBars=mode_parameters['enableErrorBars'])
		if(mode_parameters['sweepDirection'] in ['both', 'forward']):
			line = ax.plot(deviceHistory[i]['Results']['vgs_data'][0], np.abs(np.array(all_fitted_values['fwd_id_fitted'][i])) * 1e6, color=colors[i], linewidth=0.7)
		if(mode_parameters['sweepDirection'] in ['both', 'reverse']):
			line = ax.plot(deviceHistory[i]['Results']['vgs_data'][1], np.abs(np.array(all_fitted_values['rev_id_fitted'][i])) * 1e6, color=colors[i], linewidth=0.7)

		# Plot subthreshold curve fit to show SS
		line = plotSubthresholdCurve(ax2, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], lineStyle='', errorBars=mode_parameters['enableErrorBars'])
		if(mode_parameters['sweepDirection'] in ['both', 'forward']):
			line = ax2.plot(deviceHistory[i]['Results']['vgs_data'][0], np.abs(np.array(all_fitted_values['fwd_id_fitted'][i])), color=colors[i], linewidth=0.7)
		if(mode_parameters['sweepDirection'] in ['both', 'reverse']):
			line = ax2.plot(deviceHistory[i]['Results']['vgs_data'][1], np.abs(np.array(all_fitted_values['rev_id_fitted'][i])), color=colors[i], linewidth=0.7)

	# Label axes
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	return (fig, (ax, ax2))

