from utilities.MatplotlibUtility import *
import copy


plotDescription = {
	'plotCategory': 'device',
	'priority': 110,
	'dataFileDependencies': ['StaticCurrent.json'],
	'plotDefaults': {
		'figsize':(3,2.5),#(2*2.2,2*1.6),#(5,4),
		'mainIncludeOrigin':True,
		'dualIncludeOrigin':False,
		'colorMap':'plasma',
		'colorDefault': ['#56638A'],
		
		'xlabel':'Time ({:})',
		'ylabel':          '$V_{{DS}}$ (V)',
		'milli_ylabel':    '$I_{{D}}$ (mV)',
		
		'id_label': '$I_{{D}}^{{Hold}}$ (A)',
		'ig_label': '$I_{{G}}^{{Hold}}$ (A)',
		'id_legend':'$I_{{D}}^{{Hold}}$ = {:.2f} A',
		'ig_legend':'$I_{{G}}^{{Hold}}$ = {:.1f} A',
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
	id_setpoint_values = [jsonData['runConfigs']['StaticCurrent']['drainCurrentSetPoint'] for jsonData in deviceHistory]
	ig_setpoint_values = [jsonData['runConfigs']['StaticCurrent']['gateCurrentSetPoint'] for jsonData in deviceHistory]
	biasTime_values = [jsonData['runConfigs']['StaticCurrent']['totalBiasTime'] for jsonData in deviceHistory]
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
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0, colorMapEnd=0.87, enableColorBar=False)		
	
	# If timescale is unspecified, choose an appropriate one based on the data range
	if(timescale == ''):
		timescale = bestTimeScaleFor(deviceHistory[-1]['Results']['timestamps'][-1] - deviceHistory[0]['Results']['timestamps'][0])
	
	# Rescale timestamp data by factor related to the time scale
	deviceHistory = scaledData(deviceHistory, 'Results', 'timestamps', 1/secondsPer(timescale))
	
	# Adjust y-scale and y-axis labels 
	max_voltage = np.max([np.max(deviceRun['Results']['vds_data']) for deviceRun in deviceHistory])
	min_voltage = np.min([np.min(deviceRun['Results']['vds_data']) for deviceRun in deviceHistory])
	abs_max_voltage = max(max_voltage, abs(min_voltage)) if(mode_parameters['yscale'] is None) else mode_parameters['yscale']
	voltage_scale, ylabel = (1, plotDescription['plotDefaults']['ylabel']) if(abs_max_voltage >= 1) else (1e3, plotDescription['plotDefaults']['milli_ylabel'])
	
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
				id_line = plotOverTime(id_ax, deviceHistory[i]['Results']['timestamps'], [deviceHistory[i]['runConfigs']['StaticCurrent']['drainCurrentSetPoint']]*len(deviceHistory[i]['Results']['timestamps']), plt.rcParams['axes.prop_cycle'].by_key()['color'][0], offset=time_offset)
			if(ig_setpoint_changes):
				ig_line = plotOverTime(ig_ax, deviceHistory[i]['Results']['timestamps'], [deviceHistory[i]['runConfigs']['StaticCurrent']['gateCurrentSetPoint']]*len(deviceHistory[i]['Results']['timestamps']), plt.rcParams['axes.prop_cycle'].by_key()['color'][3], offset=time_offset)
				
	# === End Plotting Data ===
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax1, include=plotDescription['plotDefaults']['mainIncludeOrigin'])
	
	# Add Legend
	legend_title = getLegendTitle(deviceHistory, identifiers, plotDescription['plotDefaults'], 'runConfigs', 'StaticCurrent', mode_parameters, includeIdHold=(not id_setpoint_changes), includeIgHold=(not ig_setpoint_changes), includeTimeHold=(not biasTime_changes))
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
			axisLabels(id_ax, y_label=plotDescription['plotDefaults']['id_label'])
			
		if(ig_setpoint_changes):
			includeOriginOnYaxis(ig_ax, include=plotDescription['plotDefaults']['dualIncludeOrigin'])
			axisLabels(ig_ax, y_label=plotDescription['plotDefaults']['ig_label'])
			
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
