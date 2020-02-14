from utilities.MatplotlibUtility import *
import copy


plotDescription = {
	'plotCategory': 'device',
	'priority': 310,
	'dataFileDependencies': ['StaticBias.json'],
	'plotDefaults': {
		'figsize':(3,2.5),#(2*2.2,2*1.6),#(5,4),
		'mainIncludeOrigin':True,
		'dualIncludeOrigin':False,
		'colorMap':'plasma',
		'colorDefault': ['#56638A'],
		
		'xlabel':'Time ({:})',
		'ylabel':          '$I_{{D}}$ (A)',
		'milli_ylabel':    '$I_{{D}}$ (mA)',
		'micro_ylabel':    '$I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'nano_ylabel':     '$I_{{D}}$ (nA)',
		'pico_ylabel':     '$I_{{D}}$ (pA)',
		'neg_ylabel':      '$-I_{{D}}$ (A)',
		'neg_milli_ylabel':'$-I_{{D}}$ (mA)',
		'neg_micro_ylabel':'$-I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'neg_nano_ylabel': '$-I_{{D}}$ (nA)',
		'neg_pico_ylabel': '$-I_{{D}}$ (pA)',
		
		'vds_label': '$V_{{DS}}^{{Hold}}$ (V)',
		'vgs_label': '$V_{{GS}}^{{Hold}}$ (V)',
		'vds_legend': '$V_{{DS}}^{{Hold}}$ = {:.2f} V',
		'vgs_legend': '$V_{{GS}}^{{Hold}}$ = {:.1f} V',
		't_legend': '$t_{{Hold}}$ = {:}',
		'subplot_height_ratio':[3,1],
		'subplot_width_ratio': [1],
		'subplotHeightPad': 0.03
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	timescale = mode_parameters['timescale']
	plotInRealTime = mode_parameters['plotInRealTime']
	includeDualAxis = mode_parameters['includeDualAxis']
	
	# Check if V_DS or V_GS are changing during this experiment
	vds_setpoint_values = [jsonData['runConfigs']['StaticBias']['drainVoltageSetPoint'] for jsonData in deviceHistory]
	vgs_setpoint_values = [jsonData['runConfigs']['StaticBias']['gateVoltageSetPoint'] for jsonData in deviceHistory]
	biasTime_values = [jsonData['runConfigs']['StaticBias']['totalBiasTime'] for jsonData in deviceHistory]
	vds_setpoint_changes = min(vds_setpoint_values) != max(vds_setpoint_values)
	vgs_setpoint_changes = min(vgs_setpoint_values) != max(vgs_setpoint_values)
	biasTime_changes = min(biasTime_values) != max(biasTime_values)
	if(not (vds_setpoint_changes or vgs_setpoint_changes)):
		includeDualAxis = False
	
	# Init Figure
	if(includeDualAxis):
		fig, (ax1, ax2) = initFigure(2, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'], shareX=True, subplotWidthRatio=plotDescription['plotDefaults']['subplot_width_ratio'], subplotHeightRatio=plotDescription['plotDefaults']['subplot_height_ratio'])
		ax3 = ax2.twinx() if(vds_setpoint_changes and vgs_setpoint_changes) else None
		
		vds_ax = ax2
		vgs_ax = ax3 if(vds_setpoint_changes) else ax2
	else:
		fig, ax1 = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
		ax2, ax3 = None, None
	
	# Build Color Map
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0, colorMapEnd=0.87, enableColorBar=False)		
	
	# If timescale is unspecified, choose an appropriate one based on the data range
	if(timescale == ''):
		timescale = bestTimeScaleFor(deviceHistory[-1]['Results']['timestamps'][-1] - deviceHistory[0]['Results']['timestamps'][0])
	
	# Rescale timestamp data by factor related to the time scale
	deviceHistory = scaledData(deviceHistory, 'Results', 'timestamps', 1/secondsPer(timescale))
	
	# Adjust y-scale and y-axis labels 
	max_current = np.max([np.max(deviceRun['Results']['id_data']) for deviceRun in deviceHistory])
	min_current = np.min([np.min(deviceRun['Results']['id_data']) for deviceRun in deviceHistory])
	abs_max_current = max(max_current, abs(min_current)) if(mode_parameters['yscale'] is None) else float(mode_parameters['yscale'])
	current_scale, ylabel = (1, plotDescription['plotDefaults']['ylabel']) if(abs_max_current >= 1) else ((1e3, plotDescription['plotDefaults']['milli_ylabel']) if(abs_max_current >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_ylabel']) if(abs_max_current >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_ylabel']) if(abs_max_current >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_ylabel']))))
	
	# If negative current maximum greater than positive current maximum, flip data
	if(abs(min_current) > max_current):
		current_scale = -current_scale
		ylabel = plotDescription['plotDefaults']['neg_ylabel'] if(abs_max_current >= 1) else (plotDescription['plotDefaults']['neg_milli_ylabel'] if(abs_max_current >= 1e-3) else (plotDescription['plotDefaults']['neg_micro_ylabel'] if(abs_max_current >= 1e-6) else (plotDescription['plotDefaults']['neg_nano_ylabel'] if(abs_max_current >= 1e-9) else (plotDescription['plotDefaults']['neg_pico_ylabel']))))

	# === Begin Plotting Data ===
	time_offset = 0
	for i in range(len(deviceHistory)):
		# Compute time_offset as the real point in time relative to t_0 or just by picking up where the prev data left off
		if(plotInRealTime):
			t_0 = deviceHistory[0]['Results']['timestamps'][0]
			t_i_start = deviceHistory[i]['Results']['timestamps'][0]
			time_offset = (t_i_start - t_0)
		else:
			t_prev_end = deviceHistory[i-1]['Results']['timestamps'][-1]
			t_prev_start = deviceHistory[i-1]['Results']['timestamps'][0]
			time_offset = (0) if(i == 0) else (time_offset + (t_prev_end - t_prev_start))
		
		# Plot
		line = plotStaticBias(ax1, deviceHistory[i], colors[i], time_offset, y_data='id_data', scaleYaxisBy=current_scale, timescale=timescale, lineStyle=None, gradient=mode_parameters['enableGradient'], gradientColors=colorsFromMap(plotDescription['plotDefaults']['colorMap'], 0, 0.95, len(deviceHistory[i]['Results']['timestamps']))['colors'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
			
		# Plot Dual Axis (if desired)
		if(includeDualAxis):
			if(vds_setpoint_changes):
				vds_line = plotOverTime(vds_ax, deviceHistory[i]['Results']['timestamps'], [deviceHistory[i]['runConfigs']['StaticBias']['drainVoltageSetPoint']]*len(deviceHistory[i]['Results']['timestamps']), plt.rcParams['axes.prop_cycle'].by_key()['color'][0], offset=time_offset)
			if(vgs_setpoint_changes):
				vgs_line = plotOverTime(vgs_ax, deviceHistory[i]['Results']['timestamps'], [deviceHistory[i]['runConfigs']['StaticBias']['gateVoltageSetPoint']]*len(deviceHistory[i]['Results']['timestamps']), plt.rcParams['axes.prop_cycle'].by_key()['color'][3], offset=time_offset)
				
		## Compare current plot's parameters to the next ones, and save any differences
		# if((i == 0) or (deviceHistory[i]['runConfigs']['StaticBias'] != deviceHistory[i-1]['runConfigs']['StaticBias']) or mode_parameters['staticBiasSegmentDividers']):
		# 	dotted_lines.append({'x':time_offset})
		# 	for key in set(deviceHistory[i]['runConfigs']['StaticBias'].keys()).intersection(deviceHistory[i-1]['runConfigs']['StaticBias'].keys()):
		# 		if((i == 0) or deviceHistory[i]['runConfigs']['StaticBias'][key] != deviceHistory[i-1]['runConfigs']['StaticBias'][key]):
		# 			if(key not in parameter_labels):
		# 				parameter_labels[key] = []
		# 			parameter_labels[key].append({'x':time_offset, key:deviceHistory[i]['runConfigs']['StaticBias'][key]})
	
	# === End Plotting Data ===
	
	# Draw annotations on the main plot
	# if(len(dotted_lines) > 1):
	# 	# Draw dotted lines
	# 	if(mode_parameters['staticBiasChangeDividers'] or mode_parameters['staticBiasSegmentDividers']):
	# 		for i in range(len(dotted_lines)):
	# 			ax1.annotate('', xy=(dotted_lines[i]['x'], ax1.get_ylim()[0]), xytext=(dotted_lines[i]['x'], ax1.get_ylim()[1]), xycoords='data', arrowprops=dict(arrowstyle='-', color=(0,0,0,0.3), ls=':', lw=0.5))
		
	# 		# If no dual axis included, then annotate the plot	
	# 		if(not includeDualAxis):
	# 			if(len(parameter_labels['drainVoltageSetPoint']) > 1) or (len(parameter_labels['gateVoltageSetPoint']) > 1):
	# 				# Make the data take up less of the vertical space to make room for the labels
	# 				ax1.set_ylim(top=1.2*ax1.get_ylim()[1])
					
	# 				# Add V_DS annotation
	# 				for i in range(len(parameter_labels['drainVoltageSetPoint'])):
	# 					ax1.annotate(' $V_{DS} = $'+'{:.1f}V'.format(parameter_labels['drainVoltageSetPoint'][i]['drainVoltageSetPoint']), xy=(parameter_labels['drainVoltageSetPoint'][i]['x'], ax1.get_ylim()[1]*(0.99 - 0*0.03*i)), xycoords='data', ha='left', va='top', rotation=-90)

	# 				# Add V_GS annotation
	# 				for i in range(len(parameter_labels['gateVoltageSetPoint'])):
	# 					ax1.annotate(' $V_{GS} = $'+'{:.0f}V'.format(parameter_labels['gateVoltageSetPoint'][i]['gateVoltageSetPoint']), xy=(parameter_labels['gateVoltageSetPoint'][i]['x'], ax1.get_ylim()[1]*(0.90 - 0*0.03*i)), xycoords='data', ha='left', va='bottom', rotation=-90)
		
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax1, include=plotDescription['plotDefaults']['mainIncludeOrigin'])
	
	# Add Legend
	legend_title = getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'StaticBias', mode_parameters, includeVdsHold=(not vds_setpoint_changes), includeVgsHold=(not vgs_setpoint_changes), includeTimeHold=(not biasTime_changes))
	if(len(legend_title) > 0):
		addLegend(ax1, loc=mode_parameters['legendLoc'], title=legend_title, mode_parameters=mode_parameters)
	
	# Dual Axis Legend, Axis Labels, and save figure
	if(includeDualAxis):
		# Axis labels
		axisLabels(ax1, y_label=ylabel)
		axisLabels(ax2, x_label=plotDescription['plotDefaults']['xlabel'].format(timescale))
		
		if(vds_setpoint_changes):
			includeOriginOnYaxis(vds_ax, include=plotDescription['plotDefaults']['dualIncludeOrigin'])
			vds_ax.set_ylim(bottom=vds_ax.get_ylim()[0] - (vds_ax.get_ylim()[1] - vds_ax.get_ylim()[0])*0.08, top=vds_ax.get_ylim()[1] + (vds_ax.get_ylim()[1] - vds_ax.get_ylim()[0])*0.08)
			axisLabels(vds_ax, y_label=plotDescription['plotDefaults']['vds_label'])
			
		if(vgs_setpoint_changes):
			includeOriginOnYaxis(vgs_ax, include=plotDescription['plotDefaults']['dualIncludeOrigin'])
			axisLabels(vgs_ax, y_label=plotDescription['plotDefaults']['vgs_label'])
			
		if(vds_setpoint_changes and vgs_setpoint_changes):
			setLabel(vds_line, '$V_{DS}^{{Hold}}$')
			setLabel(vgs_line, '$V_{GS}^{{Hold}}$')
			vds_ax.legend(loc=mode_parameters['legendLoc'], borderpad=0.15, labelspacing=0.3, handlelength=0.2, handletextpad=0.2)
			vgs_ax.legend(loc=mode_parameters['legendLoc'], borderpad=0.15, labelspacing=0.3, handlelength=0.2, handletextpad=0.2)
		
		# Adjust main tick alignment so that y-axis tick labels are not so close to the dual axis
		[tick.set_verticalalignment('top') for tick in ax2.yaxis.get_majorticklabels()]
	else:
		axisLabels(ax1, x_label=plotDescription['plotDefaults']['xlabel'].format(timescale), y_label=ylabel)

	return (fig, (ax1, ax2, ax3))
