from utilities.MatplotlibUtility import *
import copy


plotDescription = {
	'name': 'Drain Voltage',
	'plotCategory': 'device',
	'priority': 330,
	'dataFileDependencies': ['StaticCurrent.json'],
	'plotDefaults': {
		'figsize':(3,2.5),#(2*2.2,2*1.6),#(5,4),
		'mainIncludeOrigin':True,
		'dualIncludeOrigin':False,
		'colorMap':'white_magenta_black',
		'colorDefault': ['#9F3285'],
		
		'xlabel':'Time ({:})',
		'ylabel':          '$V_{{DS}}$ (V)',
		'milli_ylabel':    '$V_{{DS}}$ (mV)',
		
		'id_label': 	 '$I_{{D}}^{{Hold}}$ (A)',
		'milli_id_label':'$I_{{D}}^{{Hold}}$ (mA)',
		'micro_id_label':'$I_{{D}}^{{Hold}}$ ($\\mathregular{\\mu}$A)',
		'nano_id_label': '$I_{{D}}^{{Hold}}$ (nA)',
		'pico_id_label': '$I_{{D}}^{{Hold}}$ (pA)',
		'ig_label': 	 '$I_{{G}}^{{Hold}}$ (A)',
		'milli_ig_label':'$I_{{G}}^{{Hold}}$ (mA)',
		'micro_ig_label':'$I_{{G}}^{{Hold}}$ ($\\mathregular{\\mu}$A)',
		'nano_ig_label': '$I_{{G}}^{{Hold}}$ (nA)',
		'pico_ig_label': '$I_{{G}}^{{Hold}}$ (pA)',
		
		'id_legend':      '$I_{{D}}^{{Hold}}$ = {:.2f} A',
		'milli_id_legend':'$I_{{D}}^{{Hold}}$ = {:.2f} mA',
		'micro_id_legend':'$I_{{D}}^{{Hold}}$ = {:.2f} $\\mathregular{\\mu}$A',
		'nano_id_legend': '$I_{{D}}^{{Hold}}$ = {:.2f} nA',
		'pico_id_legend': '$I_{{D}}^{{Hold}}$ = {:.2f} pA',
		'ig_legend':      '$I_{{G}}^{{Hold}}$ = {:.2f} A',
		'milli_ig_legend':'$I_{{G}}^{{Hold}}$ = {:.2f} mA',
		'micro_ig_legend':'$I_{{G}}^{{Hold}}$ = {:.2f} $\\mathregular{\\mu}$A',
		'nano_ig_legend': '$I_{{G}}^{{Hold}}$ = {:.2f} nA',
		'pico_ig_legend': '$I_{{G}}^{{Hold}}$ = {:.2f} pA',
		
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
	
	# Modify data structure to include expected parameters...
	for jsonData in deviceHistory:
		jsonData['runConfigs']['StaticBias']['drainCurrentSetPoint'] = 0
		jsonData['runConfigs']['StaticBias']['gateCurrentSetPoint'] = 0
	
	# Check if V_DS or V_GS are changing during this experiment
	id_setpoint_values = [jsonData['runConfigs']['StaticBias']['drainCurrentSetPoint'] for jsonData in deviceHistory]
	ig_setpoint_values = [jsonData['runConfigs']['StaticBias']['gateCurrentSetPoint'] for jsonData in deviceHistory]
	biasTime_values = [jsonData['runConfigs']['StaticBias']['totalBiasTime'] for jsonData in deviceHistory]
	id_setpoint_changes = min(id_setpoint_values) != max(id_setpoint_values)
	ig_setpoint_changes = min(ig_setpoint_values) != max(ig_setpoint_values)
	biasTime_changes = min(biasTime_values) != max(biasTime_values)
	if(not (id_setpoint_changes or ig_setpoint_changes)):
		includeDualAxis = False
	
	# Init Figure
	if(includeDualAxis):
		fig, (ax1, ax2) = initFigure(2, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'], shareX=True, subplotWidthRatio=plotDescription['plotDefaults']['subplot_width_ratio'], subplotHeightRatio=plotDescription['plotDefaults']['subplot_height_ratio'])
		ax3 = ax2.twinx() if(id_setpoint_changes and ig_setpoint_changes) else None
		
		id_ax = ax2
		ig_ax = ax3 if(id_setpoint_changes) else ax2
	else:
		fig, ax1 = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
		ax2, ax3 = None, None
	
	# Build Color Map
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False)		
	
	# If timescale is unspecified, choose an appropriate one based on the data range
	if(timescale == ''):
		timescale = bestTimeScaleFor(deviceHistory[-1]['Results']['timestamps'][-1] - deviceHistory[0]['Results']['timestamps'][0])
	
	# Rescale timestamp data by factor related to the time scale
	deviceHistory = scaledData(deviceHistory, 'Results', 'timestamps', 1/secondsPer(timescale))
	
	# Adjust y-scale and y-axis labels 
	max_voltage = np.max([np.max(deviceRun['Results']['vds_data']) for deviceRun in deviceHistory])
	min_voltage = np.min([np.min(deviceRun['Results']['vds_data']) for deviceRun in deviceHistory])
	abs_max_voltage = max(max_voltage, abs(min_voltage)) if(mode_parameters['yscale'] is None) else float(mode_parameters['yscale'])
	voltage_scale, ylabel = (1, plotDescription['plotDefaults']['ylabel']) if(abs_max_voltage >= 1) else (1e3, plotDescription['plotDefaults']['milli_ylabel'])
	
	# Find best scale for current axis
	abs_max_drain_current = np.max([abs(deviceRun['runConfigs']['StaticBias']['drainCurrentSetPoint']) for deviceRun in deviceHistory])
	abs_max_gate_current = np.max([abs(deviceRun['runConfigs']['StaticBias']['gateCurrentSetPoint']) for deviceRun in deviceHistory])
	abs_max_current = max(abs_max_drain_current, abs_max_gate_current)
	current_scale, id_axis_label, ig_axis_label, id_legend_label, ig_legend_label = (1, plotDescription['plotDefaults']['id_label'], plotDescription['plotDefaults']['ig_label'], plotDescription['plotDefaults']['id_legend'], plotDescription['plotDefaults']['ig_legend']) if((abs_max_current >= 1) or (abs_max_current == 0)) else ((1e3, plotDescription['plotDefaults']['milli_id_label'], plotDescription['plotDefaults']['milli_ig_label'], plotDescription['plotDefaults']['milli_id_legend'], plotDescription['plotDefaults']['milli_ig_legend']) if(abs_max_current >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_id_label'], plotDescription['plotDefaults']['micro_ig_label'], plotDescription['plotDefaults']['micro_id_legend'], plotDescription['plotDefaults']['micro_ig_legend']) if(abs_max_current >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_id_label'], plotDescription['plotDefaults']['nano_ig_label'], plotDescription['plotDefaults']['nano_id_legend'], plotDescription['plotDefaults']['nano_ig_legend']) if(abs_max_current >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_id_label'], plotDescription['plotDefaults']['pico_ig_label'], plotDescription['plotDefaults']['pico_id_legend'], plotDescription['plotDefaults']['pico_ig_legend']))))
	
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
		line = plotStaticBias(ax1, deviceHistory[i], colors[i], time_offset, y_data='vds_data', scaleYaxisBy=voltage_scale, timescale=timescale, lineStyle=None, gradient=mode_parameters['enableGradient'], gradientColors=colorsFromMap(plotDescription['plotDefaults']['colorMap'], 0, 0.95, len(deviceHistory[i]['Results']['timestamps']))['colors'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
			
		# Plot Dual Axis (if desired)
		if(includeDualAxis):
			if(id_setpoint_changes):
				id_line = plotOverTime(id_ax, deviceHistory[i]['Results']['timestamps'], [deviceHistory[i]['runConfigs']['StaticBias']['drainCurrentSetPoint'] * current_scale]*len(deviceHistory[i]['Results']['timestamps']), plt.rcParams['axes.prop_cycle'].by_key()['color'][0], offset=time_offset)
			if(ig_setpoint_changes):
				ig_line = plotOverTime(ig_ax, deviceHistory[i]['Results']['timestamps'], [deviceHistory[i]['runConfigs']['StaticBias']['gateCurrentSetPoint'] * current_scale]*len(deviceHistory[i]['Results']['timestamps']), plt.rcParams['axes.prop_cycle'].by_key()['color'][3], offset=time_offset)
				
	# === End Plotting Data ===
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax1, include=plotDescription['plotDefaults']['mainIncludeOrigin'])
	
	# Add Legend
	legend_plot_description = dict(plotDescription['plotDefaults'])
	legend_plot_description['id_legend'] = id_legend_label
	legend_plot_description['ig_legend'] = ig_legend_label
	legend_title = getLegendTitle(deviceHistory, identifiers, legend_plot_description, 'runConfigs', 'StaticBias', mode_parameters, current_scale=current_scale, includeIdHold=(not id_setpoint_changes), includeIgHold=(not ig_setpoint_changes), includeTimeHold=(not biasTime_changes))
	if(len(legend_title) > 0):
		addLegend(ax1, loc=mode_parameters['legendLoc'], title=legend_title, mode_parameters=mode_parameters)
	
	# Dual Axis Legend, Axis Labels, and save figure
	if(includeDualAxis):
		# Axis labels
		axisLabels(ax1, y_label=ylabel)
		axisLabels(ax2, x_label=plotDescription['plotDefaults']['xlabel'].format(timescale))
		
		if(id_setpoint_changes):
			includeOriginOnYaxis(id_ax, include=plotDescription['plotDefaults']['dualIncludeOrigin'])
			id_ax.set_ylim(bottom=id_ax.get_ylim()[0] - (id_ax.get_ylim()[1] - id_ax.get_ylim()[0])*0.08, top=id_ax.get_ylim()[1] + (id_ax.get_ylim()[1] - id_ax.get_ylim()[0])*0.08)
			axisLabels(id_ax, y_label=id_axis_label)
			
		if(ig_setpoint_changes):
			includeOriginOnYaxis(ig_ax, include=plotDescription['plotDefaults']['dualIncludeOrigin'])
			axisLabels(ig_ax, y_label=ig_axis_label)
			
		if(id_setpoint_changes and ig_setpoint_changes):
			setLabel(id_line, '$I_{{D}}^{{Hold}}$')
			setLabel(ig_line, '$I_{{G}}^{{Hold}}$')
			id_ax.legend(loc=mode_parameters['legendLoc'], borderpad=0.15, labelspacing=0.3, handlelength=0.2, handletextpad=0.2)
			ig_ax.legend(loc=mode_parameters['legendLoc'], borderpad=0.15, labelspacing=0.3, handlelength=0.2, handletextpad=0.2)
		
		# Adjust main tick alignment so that y-axis tick labels are not so close to the dual axis
		[tick.set_verticalalignment('top') for tick in ax2.yaxis.get_majorticklabels()]
	else:
		axisLabels(ax1, x_label=plotDescription['plotDefaults']['xlabel'].format(timescale), y_label=ylabel)

	return (fig, (ax1, ax2, ax3))
