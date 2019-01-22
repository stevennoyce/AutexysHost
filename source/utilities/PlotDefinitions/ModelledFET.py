from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu
from utilities import FET_Modeling as fet_model
import copy



plotDescription = {
	'plotCategory': 'device',
	'priority': 150,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'colorMap':'white_yellow_black',
		'colorDefault': ['#1f77b4'],
		'xlabel':'Trial',
		'ylabel':'$g_{{m}}^{{max}}$ ($\\mu$A/V)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Load Defaults
	plotDescrip_current = copy.deepcopy(plotDescription)

	# Init Figure
	fig, ax = initFigure(1, 1, plotDescrip_current['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
		
	# Compute device metrics
	all_fitted_values = {'fwd_id_fitted':[], 'rev_id_fitted':[]}
	for deviceRun in deviceHistory:
		if(mode_parameters['sweepDirection'] in ['both', 'forward']):
			if(abs(deviceRun['Results']['id_data'][0][0]) > abs(deviceRun['Results']['id_data'][0][-1]) and (deviceRun['Results']['vgs_data'][0][0] < deviceRun['Results']['vgs_data'][0][-1])):
				fwd_id_fitted, fwd_model_parameters, fwd_model_parameters_kw = fet_model.PMOSFET_Fit(deviceRun['Results']['vgs_data'][0], deviceRun['Results']['id_data'][0], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'], I_OFF_min=deviceRun['Computed']['offCurrent']/2, I_OFF_max=deviceRun['Computed']['offCurrent']*2)
			else:
				fwd_id_fitted, fwd_model_parameters, fwd_model_parameters_kw = fet_model.NMOSFET_Fit(deviceRun['Results']['vgs_data'][0], deviceRun['Results']['id_data'][0], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'], I_OFF_min=deviceRun['Computed']['offCurrent']/2, I_OFF_max=deviceRun['Computed']['offCurrent']*2)
			all_fitted_values['fwd_id_fitted'].append(fwd_id_fitted)
		if(mode_parameters['sweepDirection'] in ['both', 'reverse']):
			if(abs(deviceRun['Results']['id_data'][1][0]) < abs(deviceRun['Results']['id_data'][1][-1]) and (deviceRun['Results']['vgs_data'][1][0] > deviceRun['Results']['vgs_data'][1][-1])):
				rev_id_fitted, rev_model_parameters, rev_model_parameters_kw = fet_model.PMOSFET_Fit(deviceRun['Results']['vgs_data'][1], deviceRun['Results']['id_data'][1], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'], I_OFF_min=deviceRun['Computed']['offCurrent']/2, I_OFF_max=deviceRun['Computed']['offCurrent']*2)
			else:
				rev_id_fitted, rev_model_parameters, rev_model_parameters_kw = fet_model.NMOSFET_Fit(deviceRun['Results']['vgs_data'][1], deviceRun['Results']['id_data'][1], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'], I_OFF_min=deviceRun['Computed']['offCurrent']/2, I_OFF_max=deviceRun['Computed']['offCurrent']*2)
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

	# Label axes
	axisLabels(ax, x_label=plotDescrip_current['plotDefaults']['xlabel'], y_label=plotDescrip_current['plotDefaults']['ylabel'])

	# Save figure	
	adjustAndSaveFigure(fig, 'ModelledFET', mode_parameters)

	return (fig, ax)

