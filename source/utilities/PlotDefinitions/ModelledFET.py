from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu
from utilities import FET_Modeling as fet_model



plotDescription = {
	'plotCategory': 'device',
	'priority': 150,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'colorMap':'white_yellow_black',
		'colorDefault': ['#1f77b4'],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ (V)',
		'ylabel':'$I_{{D}}$ ($\\mu$A)',
		'neg_ylabel':'$-I_{{D}}$ ($\\mu$A)'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	ax2 = ax.twinx()
	
	# If first segment of device history is mostly negative current, flip data
	ylabel = plotDescription['plotDefaults']['ylabel']
	if((len(deviceHistory) > 0) and ((np.array(deviceHistory[0]['Results']['id_data']) < 0).sum() > (np.array(deviceHistory[0]['Results']['id_data']) >= 0).sum())):
		deviceHistory = scaledData(deviceHistory, 'Results', 'id_data', -1)
		ylabel = plotDescription['plotDefaults']['neg_ylabel']
	
	# Compute device metrics
	all_fitted_values = {'fwd_id_fitted':[], 'rev_id_fitted':[]}
	for deviceRun in deviceHistory:
		if(mode_parameters['sweepDirection'] in ['both', 'forward']):
			fwd_id_fitted, fwd_model_parameters, fwd_model_parameters_kw = fet_model.FET_Fit(deviceRun['Results']['vgs_data'][0], deviceRun['Results']['id_data'][0], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'])
			all_fitted_values['fwd_id_fitted'].append(fwd_id_fitted)
		if(mode_parameters['sweepDirection'] in ['both', 'reverse']):
			rev_id_fitted, rev_model_parameters, rev_model_parameters_kw = fet_model.FET_Fit(deviceRun['Results']['vgs_data'][1], deviceRun['Results']['id_data'][1], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'])
			all_fitted_values['rev_id_fitted'].append(rev_id_fitted)
	
	# Build Color Map and Color Bar	
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')			
	
	# Plot
	for i in range(len(deviceHistory)):
		line = plotTransferCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle='', errorBars=mode_parameters['enableErrorBars'])
		
		if(mode_parameters['sweepDirection'] in ['both', 'forward']):
			line = ax.plot(deviceHistory[i]['Results']['vgs_data'][0], np.array(all_fitted_values['fwd_id_fitted'][i]) * 1e6, color=colors[i], linewidth=0.7)
		if(mode_parameters['sweepDirection'] in ['both', 'reverse']):
			line = ax.plot(deviceHistory[i]['Results']['vgs_data'][1], np.array(all_fitted_values['rev_id_fitted'][i]) * 1e6, color=colors[i], linewidth=0.7)

		line = plotSubthresholdCurve(ax2, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], fitSubthresholdSwing=False, includeLabel=False, lineStyle='', errorBars=mode_parameters['enableErrorBars'])
		
		if(mode_parameters['sweepDirection'] in ['both', 'forward']):
			line = ax2.plot(deviceHistory[i]['Results']['vgs_data'][0], np.array(all_fitted_values['fwd_id_fitted'][i]), color=colors[i], linewidth=0.7)
		if(mode_parameters['sweepDirection'] in ['both', 'reverse']):
			line = ax2.plot(deviceHistory[i]['Results']['vgs_data'][1], np.array(all_fitted_values['rev_id_fitted'][i]), color=colors[i], linewidth=0.7)


	# Label axes
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Save figure	
	adjustAndSaveFigure(fig, 'ModelledFET', mode_parameters)

	return (fig, ax)

