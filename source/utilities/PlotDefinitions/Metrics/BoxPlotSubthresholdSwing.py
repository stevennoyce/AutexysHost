from utilities.MatplotlibUtility import *
from utilities import FET_Modeling as fet_model



plotDescription = {
	'name': 'SS',
	'plotCategory': 'device',
	'priority': 3020,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.3),
		'includeOriginOnYaxis':True,
		'colorMap':'white_purple_black',
		'colorDefault': ['#7363af'],
		
		'spacing':1,
		'x_padding':0.8,
		'width':0.5,
		
		'xlabel':'',
		'V_ylabel': 'SS (V/dec)',
		'mV_ylabel':'SS (mV/dec)',
		'V_legend_label':'Trials: {:.5g} \n$SS^{{avg}} = {:.3g}$ V/dec \n$SS^{{std}} = {:.3g}$ V/dec',
		'mV_legend_label':'Trials: {:.5g} \n$SS^{{avg}} = {:.3g}$ mV/dec \n$SS^{{std}} = {:.3g}$ mV/dec',
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
			
	# Split data into categories (default is just a single category)
	category_list = mode_parameters['boxPlotCategories']
	categories = [elem[0] for elem in category_list]
	category_sizes = [int(min(elem[1],len(SS_list))) for elem in category_list]
	category_segments = [sum(category_sizes[0:i]) for i in range(len(category_sizes)+1)]
	SS_list_categorized = [SS_list[category_segments[i]:category_segments[i+1]] for i in range(len(category_segments)-1)]
	total_points_plotted = sum([len(cat) for cat in SS_list_categorized])			
	
	# Colors
	colors = setupColors(fig, len(SS_list_categorized), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=['', '', ''], colorBarAxisLabel='')			
	
	# Adjust y-scale and y-axis labels 
	max_value = np.max(SS_list_categorized)
	min_value = np.min(SS_list_categorized)
	abs_min_value = min(abs(max_value), abs(min_value)) if(mode_parameters['yscale'] is None) else float(mode_parameters['yscale'])
	yscale, ylabel, legendlabel = (1e-3, plotDescription['plotDefaults']['V_ylabel'], plotDescription['plotDefaults']['V_legend_label']) if(abs_min_value >= 1e3) else (1, plotDescription['plotDefaults']['mV_ylabel'], plotDescription['plotDefaults']['mV_legend_label']) 
				
	# Plot	
	for i in range(len(SS_list_categorized)):
		position = i*plotDescription['plotDefaults']['spacing']
		if(mode_parameters['boxPlotBarChart']):
			line = ax.bar(position, np.mean(SS_list_categorized[i]) * yscale, yerr=np.std(SS_list_categorized[i]) * yscale, color=colors[i], width=plotDescription['plotDefaults']['width'], capsize=3, ecolor='#333333', error_kw={'capthick':1})	
		else:
			line = ax.boxplot((np.array(SS_list_categorized) * yscale).tolist()[i], positions=[position], widths=[plotDescription['plotDefaults']['width']], meanline=False, showmeans=False, showfliers=False, boxprops={'color':colors[i]}, capprops={'color':colors[i]}, whiskerprops={'color':colors[i]}, medianprops={'color':colors[i]}, meanprops={'color':colors[i]})
		if(mode_parameters['boxPlotShowPoints']):
			for value in SS_list_categorized[i]:
				ax.plot([position], [value * yscale], color='black', marker='o', markersize=4)
		
	# Tick Labels
	ax.set_xticks(range(len(SS_list_categorized)))
	ax.set_xticklabels(categories)
	
	# Legend
	if(mode_parameters['enableLegend']):
		ax.legend(loc='upper right', title=legendlabel.format(total_points_plotted, SS_avg * yscale, SS_std * yscale))
	
	# X-axis limits
	ax.set_xlim(left= -plotDescription['plotDefaults']['x_padding'], right=(len(SS_list_categorized)-1)*plotDescription['plotDefaults']['spacing']+(plotDescription['plotDefaults']['x_padding']))
	
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOriginOnYaxis'], stretchfactor=1.1)
	
	return (fig, (ax,))