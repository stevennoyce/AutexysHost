from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu
from utilities import FET_Modeling as fet_model



plotDescription = {
	'plotCategory': 'device',
	'priority': 2040,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.3),
		'includeOriginOnYaxis':True,
		'colorMap':'white_maroon_black',
		'colorDefault': ['#800000'],
		
		'spacing':1,
		'x_padding':0.8,
		'width':0.5,
		
		'xlabel':'',
		'unity_ylabel':'Hysteresis (V)',
		'milli_ylabel':'Hysteresis (mV)',
		'unity_legend_label':'Trials: {:.5g} \n$V_{{H}}^{{avg}} = {:.3g}$ V \n$V_{{H}}^{{std}} = {:.3g}$ V',
		'milli_legend_label':'Trials: {:.5g} \n$V_{{H}}^{{avg}} = {:.3g}$ mV \n$V_{{H}}^{{std}} = {:.3g}$ mV',
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
	
	# Compute Hysteresis from VT for every pair of transfer curves
	H_list = [abs(VT_list[i] - VT_list[i+1]) for i in np.array(range(int(len(VT_list)/2))) * 2] if(len(VT_list) >= 2) else []
	H_avg, H_std = np.mean(H_list), np.std(H_list)
	print('Extracted H: ' + str(H_list))
	
	# Split data into categories (default is just a single category)
	category_list = mode_parameters['boxPlotCategories']
	categories = [elem[0] for elem in category_list]
	category_sizes = [int(min(elem[1],len(H_list))) for elem in category_list]
	category_segments = [sum(category_sizes[0:i]) for i in range(len(category_sizes)+1)]
	H_list_categorized = [H_list[category_segments[i]:category_segments[i+1]] for i in range(len(category_segments)-1)]
	total_points_plotted = sum([len(cat) for cat in H_list_categorized])			
	
	# Colors
	colors = setupColors(fig, len(H_list_categorized), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=['', '', ''], colorBarAxisLabel='')			
		
	# Adjust y-scale and y-axis labels 
	max_value = np.max(H_list_categorized)
	min_value = np.min(H_list_categorized)
	abs_max_value = max(max_value, abs(min_value))
	voltage_scale, ylabel, legendlabel = (1, plotDescription['plotDefaults']['unity_ylabel'], plotDescription['plotDefaults']['unity_legend_label']) if(abs_max_value >= 1) else (1e3, plotDescription['plotDefaults']['milli_ylabel'], plotDescription['plotDefaults']['milli_legend_label'])	
				
	# Plot
	for i in range(len(H_list_categorized)):
		position = i*plotDescription['plotDefaults']['spacing']
		if(mode_parameters['boxPlotBarChart']):
			line = ax.bar(position, np.mean(H_list_categorized[i]) * voltage_scale, yerr=np.std(H_list_categorized[i]) * voltage_scale, color=colors[i], width=plotDescription['plotDefaults']['width'], capsize=3, ecolor='#333333', error_kw={'capthick':1})	
		else:
			line = ax.boxplot((np.array(H_list_categorized) * voltage_scale).tolist()[i], positions=[position], widths=[plotDescription['plotDefaults']['width']], meanline=False, showmeans=False, showfliers=False, boxprops={'color':colors[i]}, capprops={'color':colors[i]}, whiskerprops={'color':colors[i]}, medianprops={'color':colors[i]}, meanprops={'color':colors[i]})
		
	# Tick Labels
	ax.set_xticks(range(len(H_list_categorized)))
	ax.set_xticklabels(categories)
	
	# Legend
	if(mode_parameters['enableLegend']):
		ax.legend(loc='upper right', title=legendlabel.format(total_points_plotted, H_avg * voltage_scale, H_std * voltage_scale))
	
	# X-axis limits
	ax.set_xlim(left= -plotDescription['plotDefaults']['x_padding'], right=(len(H_list_categorized)-1)*plotDescription['plotDefaults']['spacing']+(plotDescription['plotDefaults']['x_padding']))
	
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)	
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOriginOnYaxis'], stretchfactor=1.1)
	
	return (fig, (ax,))