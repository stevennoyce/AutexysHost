from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu



plotDescription = {
	'plotCategory': 'device',
	'priority': 2010,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'automaticAxisLabels':True,
		
		'xlabel':'Trial',
		'ylabel':'$g_{{m}}^{{max}}$ ($\\mu$A/V)',
		'legend_label':'$g_{{m}}^{{avg}} = {:.3g}$ $\\mu$A/V',
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
	line = ax.boxplot(np.array(gm_list) * 10**6, meanline=True, showmeans=True, showfliers=False, medianprops={'color':'#000000'}, meanprops={'color':'#000000'})
	
	# Legend
	if(mode_parameters['enableLegend']):
		ax.legend(title=plotDescription['plotDefaults']['legend_label'].format(gm_avg * 10**6))
	
	return (fig, (ax,))
