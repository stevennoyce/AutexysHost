from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu
from utilities import FET_Modeling as fet_model



plotDescription = {
	'plotCategory': 'device',
	'priority': 120,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'include60mV':True,
		'colorMap':'white_purple_black',
		'colorDefault': ['#1f77b4'],
		'xlabel':'Trial',
		'ylabel':'SS (mV/dec)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
		
	# Compute device metrics
	all_fitted_parameters = {'V_T':[], 'mu_Cox_W_L':[], 'SS_mV_dec':[], 'I_OFF':[], 'g_m_max':[]}
	for deviceRun in deviceHistory:
		if(mode_parameters['sweepDirection'] in ['both', 'forward']):
			fwd_id_fitted, fwd_model_parameters, fwd_model_parameters_kw = fet_model.FET_Fit(deviceRun['Results']['vgs_data'][0], deviceRun['Results']['id_data'][0], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'])
			for parameter in all_fitted_parameters.keys():
				all_fitted_parameters[parameter].append(fwd_model_parameters_kw[parameter])
		if(mode_parameters['sweepDirection'] in ['both', 'reverse']):
			rev_id_fitted, rev_model_parameters, rev_model_parameters_kw = fet_model.FET_Fit(deviceRun['Results']['vgs_data'][1], deviceRun['Results']['id_data'][1], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'])
			for parameter in all_fitted_parameters.keys():
				all_fitted_parameters[parameter].append(rev_model_parameters_kw[parameter])
	VT_list = all_fitted_parameters['V_T']
	gm_list = all_fitted_parameters['g_m_max']
	SS_list = all_fitted_parameters['SS_mV_dec']
	VT_avg = np.mean(all_fitted_parameters['V_T'])
	gm_avg = np.mean(all_fitted_parameters['g_m_max'])	
	SS_avg = np.mean(all_fitted_parameters['SS_mV_dec'])
	
	# Build Color Map and Color Bar	
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(SS_list), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')			
	
	# Plot
	for i in range(len(SS_list)):
		line = ax.plot([i+1], [SS_list[i]], color=colors[i], marker='o', markersize=4, linewidth=0, linestyle=None)

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])

	# Show the 60 mV/dec thermal limit to SS (if desired)
	if(plotDescription['plotDefaults']['include60mV']):
		ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [60, 60], color='black', lw=1, ls='--')
		ax.set_ylim(bottom=0, top=ax.get_ylim()[1]*1.1)

	# Save figure	
	adjustAndSaveFigure(fig, 'SubthresholdSwing', mode_parameters)

	return (fig, ax)

