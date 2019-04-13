from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu
from utilities import FET_Modeling as fet_model



plotDescription = {
	'plotCategory': 'device',
	'priority': 1020,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'includeOriginOnYaxis':True,
		'automaticAxisLabels':True,
		'colorMap':'white_orange_black',
		'colorDefault': ['#1f77b4'],
		'xlabel':'Trial',
		'ylabel':'$g_{{m}}^{{max}}$ ($\\mu$A/V)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
		
	# Compute device metrics
	directions = ([0]) if(mode_parameters['sweepDirection'] == 'forward') else (([1]) if(mode_parameters['sweepDirection'] == 'reverse') else([0,1]))
	vgs_data_list = [deviceRun['Results']['vgs_data'][i]  for deviceRun in deviceHistory for i in directions]
	id_data_list  = [deviceRun['Results']['id_data'][i]   for deviceRun in deviceHistory for i in directions]
	
	print(len(vgs_data_list))
	print(len(id_data_list))
	metrics = fet_model.FET_Metrics_Multiple(vgs_data_list, id_data_list)
	
	VT_list = metrics['V_T']
	gm_list = metrics['g_m_max']
	SS_list = metrics['SS_mV_dec']
	VT_avg = np.mean(VT_list)
	gm_avg = np.mean(gm_list)	
	SS_avg = np.mean(SS_list)
	
	# Build Color Map and Color Bar	
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(gm_list), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')			
	
	# Plot
	for i in range(len(gm_list)):
		line = ax.plot([i+1], np.array([gm_list[i]]) * 10**6, color=colors[i], marker='o', markersize=4, linewidth=0, linestyle=None)

	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOriginOnYaxis'])
	ax.set_ylim(bottom=ax.get_ylim()[0]*1.1, top=ax.get_ylim()[1]*1.1)

	return (fig, (ax,))

