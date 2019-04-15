from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu



plotDescription = {
	'plotCategory': 'device',
	'priority': 2010,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.3),
		'automaticAxisLabels':True,
		'colorMap':'white_orange_black',
		'colorDefault': ['#ee7539'],
		
		'xlabel':'',
		'ylabel':'$g_{{m}}^{{max}}$ ($\\mu$A/V)',
		'legend_label':'Trials: {:.5g} \n$g_{{m}}^{{avg}} = {:.3g}$ $\\mu$A/V \n$g_{{m}}^{{std}} = {:.3g}$ $\\mu$A/V',
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
	
	# Split data into categories (default is just a single category)
	category_list = mode_parameters['boxPlotCategories']
	categories = [elem[0] for elem in category_list]
	category_sizes = [int(min(elem[1],len(gm_list))) for elem in category_list]
	category_segments = [sum(category_sizes[0:i]) for i in range(len(category_sizes)+1)]
	gm_list_categorized = [gm_list[category_segments[i]:category_segments[i+1]] for i in range(len(category_segments)-1)]
	total_points_plotted = sum([len(cat) for cat in gm_list_categorized])			
	
	# Colors
	colors = setupColors(fig, len(gm_list_categorized), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=['', '', ''], colorBarAxisLabel='')			
		
	# Plot
	for i in range(len(gm_list_categorized)):
		line = ax.boxplot((np.array(gm_list_categorized) * 10**6).tolist()[i], positions=[i], meanline=True, showmeans=True, showfliers=False, boxprops={'color':colors[i]}, capprops={'color':colors[i]}, whiskerprops={'color':colors[i]}, medianprops={'color':colors[i]}, meanprops={'color':colors[i]})
	
	# Tick Labels
	ax.set_xticks(range(len(gm_list_categorized)))
	ax.set_xticklabels(categories)
	
	# X-axis limits
	x_padding = 0.25
	ax.set_xlim(left=(0-(x_padding)), right=(len(gm_list_categorized)-1)+(x_padding))
	
	# Legend
	if(mode_parameters['enableLegend']):
		ax.legend(loc='upper right', title=plotDescription['plotDefaults']['legend_label'].format(total_points_plotted, gm_avg * 10**6, gm_std * 10**6))
	
	return (fig, (ax,))
