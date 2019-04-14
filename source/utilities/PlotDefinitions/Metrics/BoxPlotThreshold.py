from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu



plotDescription = {
	'plotCategory': 'device',
	'priority': 2030,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'automaticAxisLabels':True,
		
		'xlabel':'Trial',
		'ylabel':'Threshold Voltage (V)',
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
	VT_avg = np.mean(VT_list)
	gm_avg = np.mean(gm_list)	
	SS_avg = np.mean(SS_list)	
				
	# Plot
	if mode_parameters['useBoxWhiskerPlot']: 
		line = ax.boxplot(VT_list, meanline=True, showmeans=True, showfliers=False, medianprops={'color':'#000000'}, meanprops={'color':'#000000'})
	else: 
		line = ax.plot(range(len(VT_list)), VT_list, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)

	return (fig, (ax,))