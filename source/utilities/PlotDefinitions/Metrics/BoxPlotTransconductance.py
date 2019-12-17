from utilities.MatplotlibUtility import *
from utilities import FET_Modeling as fet_model



plotDescription = {
	'plotCategory': 'device',
	'priority': 3010,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.3),
		'includeOriginOnYaxis':True,
		'colorMap':'white_orange_black',
		'colorDefault': ['#ee7539'],
		
		'spacing':1,
		'x_padding':0.8,
		'width':0.5,
		
		'xlabel':'',
		'ylabel':      '$g_{{m}}^{{max}}$ (S)',
		'milli_ylabel':'$g_{{m}}^{{max}}$ (mS)',
		'micro_ylabel':'$g_{{m}}^{{max}}$ ($\\mathregular{\\mu}$S)',
		'nano_ylabel': '$g_{{m}}^{{max}}$ (nS)',
		'pico_ylabel': '$g_{{m}}^{{max}}$ (pS)',
		'legend_label':      'Trials: {:.5g} \n$g_{{m}}^{{avg}} = {:.3g}$ S \n$g_{{m}}^{{std}} = {:.3g}$ S',
		'milli_legend_label':'Trials: {:.5g} \n$g_{{m}}^{{avg}} = {:.3g}$ mS \n$g_{{m}}^{{std}} = {:.3g}$ mS',
		'micro_legend_label':'Trials: {:.5g} \n$g_{{m}}^{{avg}} = {:.3g}$ $\\mathregular{{\\mu}}$S \n$g_{{m}}^{{std}} = {:.3g}$ $\\mathregular{{\\mu}}$S',
		'nano_legend_label': 'Trials: {:.5g} \n$g_{{m}}^{{avg}} = {:.3g}$ nS \n$g_{{m}}^{{std}} = {:.3g}$ nS',
		'pico_legend_label': 'Trials: {:.5g} \n$g_{{m}}^{{avg}} = {:.3g}$ pS \n$g_{{m}}^{{std}} = {:.3g}$ pS',
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
		
	# Adjust y-scale and y-axis labels 
	max_value = np.max(gm_list_categorized)
	min_value = np.min(gm_list_categorized)
	abs_max_value = max(max_value, abs(min_value)) if(mode_parameters['yscale'] is None) else mode_parameters['yscale']
	yscale, ylabel, legendlabel = (1, plotDescription['plotDefaults']['ylabel'], plotDescription['plotDefaults']['legend_label']) if(abs_max_value >= 1) else ((1e3, plotDescription['plotDefaults']['milli_ylabel'], plotDescription['plotDefaults']['milli_legend_label']) if(abs_max_value >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_ylabel'], plotDescription['plotDefaults']['micro_legend_label']) if(abs_max_value >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_ylabel'], plotDescription['plotDefaults']['nano_legend_label']) if(abs_max_value >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_ylabel'], plotDescription['plotDefaults']['pico_legend_label']))))	
		
	# Plot
	for i in range(len(gm_list_categorized)):
		position = i*plotDescription['plotDefaults']['spacing']
		if(mode_parameters['boxPlotBarChart']):
			line = ax.bar(position, np.mean(gm_list_categorized[i]) * yscale, yerr=np.std(gm_list_categorized[i]) * yscale, color=colors[i], width=plotDescription['plotDefaults']['width'], capsize=3, ecolor='#333333', error_kw={'capthick':1})	
		else:
			line = ax.boxplot((np.array(gm_list_categorized) * yscale).tolist()[i], positions=[position], widths=[plotDescription['plotDefaults']['width']], meanline=False, showmeans=False, showfliers=False, boxprops={'color':colors[i]}, capprops={'color':colors[i]}, whiskerprops={'color':colors[i]}, medianprops={'color':colors[i]}, meanprops={'color':colors[i]})
		if(mode_parameters['boxPlotShowPoints']):
			for value in gm_list_categorized[i]:
				ax.plot([position], [value * yscale], color='black', marker='o', markersize=4)
	
	# Tick Labels
	ax.set_xticks(range(len(gm_list_categorized)))
	ax.set_xticklabels(categories)
	
	# Legend
	if(mode_parameters['enableLegend']):
		ax.legend(loc='upper right', title=legendlabel.format(total_points_plotted, gm_avg * yscale, gm_std * yscale))
	
	# X-axis limits
	ax.set_xlim(left= -plotDescription['plotDefaults']['x_padding'], right=(len(gm_list_categorized)-1)*plotDescription['plotDefaults']['spacing']+(plotDescription['plotDefaults']['x_padding']))
	
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOriginOnYaxis'], stretchfactor=1.1)

	return (fig, (ax,))
