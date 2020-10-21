from utilities.MatplotlibUtility import *
from utilities import FET_Modeling as fet_model



plotDescription = {
	'name': 'Transconductance',
	'plotCategory': 'device',
	'priority': 2010,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'colorMap':'white_orange_black',
		'colorDefault': ['#ee7539'],
		
		'xlabel':'Trial',
		'ylabel':      '$g_{{m}}^{{max}}$ (S)',
		'milli_ylabel':'$g_{{m}}^{{max}}$ (mS)',
		'micro_ylabel':'$g_{{m}}^{{max}}$ ($\\mathregular{\\mu}$S)',
		'nano_ylabel': '$g_{{m}}^{{max}}$ (nS)',
		'pico_ylabel': '$g_{{m}}^{{max}}$ (pS)',
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
	print('Extracted gm: ' + str(gm_list))
	
	# Build Color Map and Color Bar	
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(gm_list), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')			
	
	# Adjust y-scale and y-axis labels 
	max_value = np.max(gm_list)
	min_value = np.min(gm_list)
	abs_max_value = max(max_value, abs(min_value)) if(mode_parameters['yscale'] is None) else float(mode_parameters['yscale'])
	yscale, ylabel = (1, plotDescription['plotDefaults']['ylabel']) if(abs_max_value >= 1) else ((1e3, plotDescription['plotDefaults']['milli_ylabel']) if(abs_max_value >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_ylabel']) if(abs_max_value >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_ylabel']) if(abs_max_value >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_ylabel']))))
	
	# Plot
	for i in range(len(gm_list)):
		line = ax.plot([i+1], np.array([gm_list[i]]) * yscale, color=colors[i], marker='o', markersize=4, linewidth=0, linestyle=None)

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)

	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOriginOnYaxis'], stretchfactor=1.1)

	return (fig, (ax,))

