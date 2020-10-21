from utilities.MatplotlibUtility import *
from utilities import FET_Modeling as fet_model



plotDescription = {
	'name': 'SS',
	'plotCategory': 'device',
	'priority': 2020,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'include60mV':True,
		'colorMap':'white_purple_black',
		'colorDefault': ['#7363af'],
		
		'xlabel':'Trial',
		'V_ylabel': 'SS (V/dec)',
		'mV_ylabel':'SS (mV/dec)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
		
	# Compute device metrics
	directions = ([0]) if(mode_parameters['sweepDirection'] == 'forward') else (([1]) if(mode_parameters['sweepDirection'] == 'reverse') else([0,1]))
	vgs_data_list = [deviceRun['Results']['vgs_data'][i]  for deviceRun in deviceHistory for i in directions]
	id_data_list  = [deviceRun['Results']['id_data'][i]   for deviceRun in deviceHistory for i in directions]
	metrics = fet_model.FET_Metrics_Multiple(vgs_data_list, id_data_list)
	VT_list = metrics['V_T']
	gm_list = metrics['g_m_max']
	SS_list = metrics['SS_mV_dec']
	VT_avg, VT_std = np.mean(VT_list), np.std(VT_list)
	gm_avg, gm_std = np.mean(gm_list), np.std(gm_list)
	SS_avg, SS_std = np.mean(SS_list), np.std(SS_list)
	print('Extracted SS_mV_dec: ' + str(SS_list))
	
	# Build Color Map and Color Bar	
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(SS_list), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')			
	
	# Adjust y-scale and y-axis labels 
	max_value = np.max(SS_list)
	min_value = np.min(SS_list)
	abs_min_value = min(abs(max_value), abs(min_value)) if(mode_parameters['yscale'] is None) else float(mode_parameters['yscale'])
	yscale, ylabel = (1e-3, plotDescription['plotDefaults']['V_ylabel']) if(abs_min_value >= 1e3) else (1, plotDescription['plotDefaults']['mV_ylabel']) 
	
	# Plot
	for i in range(len(SS_list)):
		line = ax.plot([i+1], np.array([SS_list[i]]) * yscale, color=colors[i], marker='o', markersize=4, linewidth=0, linestyle=None)

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Show the 60 mV/dec thermal limit to SS (if desired)
	if(plotDescription['plotDefaults']['include60mV'] and (yscale == 1)):
		ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [60, 60], color='black', lw=1, ls='--')
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOriginOnYaxis'], stretchfactor=1.1)

	return (fig, (ax,))

