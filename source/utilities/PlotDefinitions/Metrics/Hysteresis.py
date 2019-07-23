from utilities.MatplotlibUtility import *
from utilities import FET_Modeling as fet_model

import numpy as np


plotDescription = {
	'plotCategory': 'device',
	'priority': 1040,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'colorMap':'white_maroon_black',
		'colorDefault': ['#800000'],
		
		'xlabel':'Trial',
		'unity_ylabel':'Hysteresis (V)',
		'milli_ylabel':'Hysteresis (mV)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
		
	# Compute device metrics
	directions = [0,1]
	vgs_data_list = [deviceRun['Results']['vgs_data'][i]  for deviceRun in deviceHistory for i in directions]
	id_data_list  = [deviceRun['Results']['id_data'][i]   for deviceRun in deviceHistory for i in directions]
	metrics = fet_model.FET_Metrics_Multiple(vgs_data_list, id_data_list)
	VT_list = metrics['V_T']
	gm_list = metrics['g_m_max']
	SS_list = metrics['SS_mV_dec']
	VT_avg, VT_std = np.mean(VT_list), np.std(VT_list)
	gm_avg, gm_std = np.mean(gm_list), np.std(gm_list)
	SS_avg, SS_std = np.mean(SS_list), np.std(SS_list)
	
	# Compute Hysteresis from VT for every pair of transfer curves
	H_list = [abs(VT_list[i] - VT_list[i+1]) for i in np.array(range(int(len(VT_list)/2))) * 2] if(len(VT_list) >= 2) else []
	print('Extracted H: ' + str(H_list))
	
	# Build Color Map and Color Bar	
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(H_list), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')			
	
	# Adjust y-scale and y-axis labels 
	max_value = np.max(H_list)
	min_value = np.min(H_list)
	abs_max_value = max(max_value, abs(min_value))
	voltage_scale, ylabel = (1, plotDescription['plotDefaults']['unity_ylabel']) if(abs_max_value >= 1) else (1e3, plotDescription['plotDefaults']['milli_ylabel'])
	
	# Plot
	for i in range(len(H_list)):
		line = ax.plot([i+1], [H_list[i] * voltage_scale], color=colors[i], marker='o', markersize=4, linewidth=0, linestyle=None)

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)	

	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOriginOnYaxis'], stretchfactor=1.1)

	return (fig, (ax,))

