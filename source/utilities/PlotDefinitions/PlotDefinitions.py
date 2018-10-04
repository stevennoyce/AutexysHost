from ..MatplotlibUtility import *

plot_parameters = {
	
}




plot_parameters['SubthresholdCurve'] = {
	'figsize':(2.8,3.2),
	'colorMap':'hot',
	'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][0],
	'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
	'ylabel':'$I_{{D}}$ [A]',
	'leg_vds_label':'$V_{{DS}}^{{Sweep}}$\n  = {:}V',
	'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V'
}

def plotFullSubthresholdCurveHistory(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['SubthresholdCurve']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
	# Build Color Map and Color Bar
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plot_parameters['SubthresholdCurve']['colorDefault'], colorMapName=plot_parameters['SubthresholdCurve']['colorMap'], colorMapStart=0.7, colorMapEnd=0, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')		

	# Plot
	for i in range(len(deviceHistory)):
		line = plotSubthresholdCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], fitSubthresholdSwing=False, includeLabel=False, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])			
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	axisLabels(ax, x_label=plot_parameters['SubthresholdCurve']['xlabel'], y_label=plot_parameters['SubthresholdCurve']['ylabel'])
	ax.yaxis.set_major_locator(matplotlib.ticker.LogLocator(numticks=10))
	
	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plot_parameters['SubthresholdCurve'], 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True, includeSubthresholdSwing=False))
	adjustAndSaveFigure(fig, 'FullSubthresholdCurves', mode_parameters)

	return (fig, ax)



plot_parameters['TransferCurve'] = {
	'figsize':(2.8,3.2),
	'includeOrigin':True,
	'colorMap':'hot',
	'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][1],
	'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
	'ylabel':'$I_{{D}}$ [$\\mu$A]',
	'neg_label':'$-I_{{D}}$ [$\\mu$A]',
	'ii_label':'$I_{{D}}$, $I_{{G}}$ [$\\mu$A]',
	'neg_ii_label':'$-I_{{D}}$, $I_{{G}}$ [$\\mu$A]',
	'leg_vds_label':'$V_{{DS}}^{{Sweep}}$\n  = {:}V',
	'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V',
}

def plotFullTransferCurveHistory(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['TransferCurve']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
	# Build Color Map and Color Bar
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plot_parameters['TransferCurve']['colorDefault'], colorMapName=plot_parameters['TransferCurve']['colorMap'], colorMapStart=0.7, colorMapEnd=0, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')		
	
	# If first segment of device history is mostly negative current, flip data
	if((len(deviceHistory) > 0) and (np.percentile(deviceHistory[0]['Results']['id_data'], 75) < 0)):
		deviceHistory = scaledData(deviceHistory, 'Results', 'id_data', -1)
		plot_parameters['TransferCurve']['ylabel'] = plot_parameters['TransferCurve']['neg_label']
	
	# Plot
	for i in range(len(deviceHistory)):
		line = plotTransferCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	axisLabels(ax, x_label=plot_parameters['TransferCurve']['xlabel'], y_label=plot_parameters['TransferCurve']['ylabel'])

	# Add gate current to axis
	if(mode_parameters['includeGateCurrent']):
		if(len(deviceHistory) == 1):
			gate_colors = [plt.rcParams['axes.prop_cycle'].by_key()['color'][2]]
			gate_linestyle = None
		else:	
			gate_colors = colors
			gate_linestyle = '--'
		for i in range(len(deviceHistory)):
			plotGateCurrent(ax, deviceHistory[i], gate_colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=gate_linestyle, errorBars=mode_parameters['enableErrorBars'])
		if(plot_parameters['TransferCurve']['ylabel'] == plot_parameters['TransferCurve']['neg_label']):
			plot_parameters['TransferCurve']['ylabel'] = plot_parameters['TransferCurve']['neg_ii_label']
		else:
			plot_parameters['TransferCurve']['ylabel'] = plot_parameters['TransferCurve']['ii_label']
		axisLabels(ax, x_label=plot_parameters['TransferCurve']['xlabel'], y_label=plot_parameters['TransferCurve']['ylabel'])

	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plot_parameters['TransferCurve']['includeOrigin'])

	# Add Legend and save figure	
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plot_parameters['TransferCurve'], 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True))
	adjustAndSaveFigure(fig, 'FullTransferCurves', mode_parameters)

	return (fig, ax)



plot_parameters['GateCurrent'] = {
	'figsize':(2.8,3.2),
	'includeOrigin':False,
	'colorMap':'hot',
	'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][2],
	'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
	'ylabel':'$I_{{G}}$ [A]',
	'leg_vds_label':'$V_{{DS}}^{{Sweep}} = ${:}V',
	'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V'
}

def plotFullGateCurrentHistory(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['GateCurrent']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))

	# Build Color Map and Color Bar
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plot_parameters['GateCurrent']['colorDefault'], colorMapName=plot_parameters['GateCurrent']['colorMap'], colorMapStart=0.7, colorMapEnd=0, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')		

	# Plot
	for i in range(len(deviceHistory)):
		line = plotGateCurrent(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	axisLabels(ax, x_label=plot_parameters['GateCurrent']['xlabel'], y_label=plot_parameters['GateCurrent']['ylabel'])

	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plot_parameters['GateCurrent']['includeOrigin'])

	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plot_parameters['GateCurrent'], 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True))
	adjustAndSaveFigure(fig, 'FullGateCurrents', mode_parameters)

	return (fig, ax)



plot_parameters['OutputCurve'] = {
	'figsize':(2.8,3.2),
	'colorMap':'plasma',
	'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][0],
	'xlabel':'$V_{{DS}}^{{Sweep}}$ [V]',
	'ylabel':'$I_{{D}}$ [$\\mu$A]',
	'neg_label':'$-I_{{D}}$ [$\\mu$A]',
	'leg_vgs_label':'$V_{{GS}}^{{Sweep}}$\n  = {:}V',
	'leg_vgs_range_label':'$V_{{GS}}^{{min}} = $ {:}V\n'+'$V_{{GS}}^{{max}} = $ {:}V'
}

def plotFullOutputCurveHistory(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['OutputCurve']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))

	# Build Color Map and Color Bar
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plot_parameters['OutputCurve']['colorDefault'], colorMapName=plot_parameters['OutputCurve']['colorMap'], colorMapStart=0, colorMapEnd=0.87, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')		
	
	# If first segment of device history is mostly negative current, flip data
	if((len(deviceHistory) > 0) and (np.percentile(deviceHistory[0]['Results']['id_data'], 75) < 0)):
		deviceHistory = scaledData(deviceHistory, 'Results', 'id_data', -1)
		plot_parameters['OutputCurve']['ylabel'] = plot_parameters['OutputCurve']['neg_label']
	
	# Plot
	for i in range(len(deviceHistory)):
		line = plotOutputCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	axisLabels(ax, x_label=plot_parameters['OutputCurve']['xlabel'], y_label=plot_parameters['OutputCurve']['ylabel'])

	# Add Legend and save figure	
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plot_parameters['OutputCurve'], 'runConfigs', 'DrainSweep', mode_parameters, includeVgsSweep=True))
	adjustAndSaveFigure(fig, 'FullOutputCurves', mode_parameters)

	return (fig, ax)



plot_parameters['BurnOut'] = {
	'figsize':(8,4.5),
	'subplot_height_ratio':[1],
	'subplot_width_ratio':[1,1],
	'colorMap':'hot',
	'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][0],
	'vds_label':'$V_{{DS}}$ [V]',
	'id_micro_label':'$I_{{D}}$ [$\\mu$A]',
	'time_label':'Time [sec]',
	'id_annotation':'burn current',
	'legend_title':'$V_{{GS}}$ = {:}V'
}

def plotFullBurnOutHistory(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure	
	fig, (ax1, ax2) = initFigure(1, 2, plot_parameters['BurnOut']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'], shareX=False, subplotWidthRatio=plot_parameters['BurnOut']['subplot_width_ratio'], subplotHeightRatio=plot_parameters['BurnOut']['subplot_height_ratio'])
	ax2 = plt.subplot(222)
	ax3 = plt.subplot(224)
	if(not mode_parameters['publication_mode']):
		ax1.set_title(getTestLabel(deviceHistory, identifiers))

	# Build Color Map and Color Bar
	plt.sca(ax1)
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plot_parameters['BurnOut']['colorDefault'], colorMapName=plot_parameters['BurnOut']['colorMap'], colorMapStart=0.7, colorMapEnd=0, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,1], colorBarTickLabels=['Final', 'Initial'], colorBarAxisLabel='Burnouts')		

	# Plot
	for i in range(len(deviceHistory)):
		plotBurnOut(ax1, ax2, ax3, deviceHistory[i], colors[i], lineStyle=None, annotate=False, annotation=plot_parameters['BurnOut']['id_annotation'])

	axisLabels(ax1, x_label=plot_parameters['BurnOut']['vds_label'], y_label=plot_parameters['BurnOut']['id_micro_label'])
	axisLabels(ax2, x_label=plot_parameters['BurnOut']['time_label'], y_label=plot_parameters['BurnOut']['id_micro_label'])
	axisLabels(ax3, x_label=plot_parameters['BurnOut']['time_label'], y_label=plot_parameters['BurnOut']['vds_label'])

	# Add Legend and save figure
	addLegend(ax1, loc=mode_parameters['legendLoc'], title=plot_parameters['BurnOut']['legend_title'].format(np.mean([deviceRun['runConfigs']['BurnOut']['gateVoltageSetPoint'] for deviceRun in deviceHistory])))
	addLegend(ax2, loc=mode_parameters['legendLoc'], title=plot_parameters['BurnOut']['legend_title'].format(np.mean([deviceRun['runConfigs']['BurnOut']['gateVoltageSetPoint'] for deviceRun in deviceHistory])))
	addLegend(ax3, loc=mode_parameters['legendLoc'], title=plot_parameters['BurnOut']['legend_title'].format(np.mean([deviceRun['runConfigs']['BurnOut']['gateVoltageSetPoint'] for deviceRun in deviceHistory])))
	adjustAndSaveFigure(fig, 'FullBurnOut', mode_parameters, subplotWidthPad=0.25, subplotHeightPad=0.8)

	return (fig, (ax1, ax2, ax3))



plot_parameters['StaticBias'] = {
	'figsize':(4.4,3.2),#(2*2.2,2*1.6),#(5,4),
	'mainIncludeOrigin':True,
	'dualIncludeOrigin':False,
	'colorMap':'plasma',
	'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][4],
	'xlabel':'Time [{:}]',
	'ylabel':'$I_{{D}}$ [$\\mu$A]',
	'neg_label':'$-I_{{D}}$ [$\\mu$A]',
	'vds_label': '$V_{{DS}}^{{Hold}}$ [V]',
	'vgs_label': '$V_{{GS}}^{{Hold}}$ [V]',
	'vds_legend': '$V_{{DS}}^{{Hold}}$ = {:.2f}V',
	'vgs_legend': '$V_{{GS}}^{{Hold}}$ = {:.1f}V',
	't_legend': '$t_{{Hold}}$ = {:}',
	'subplot_height_ratio':[3,1],
	'subplot_width_ratio': [1],
	'subplot_spacing': 0.03
}

def plotFullStaticBiasHistory(deviceHistory, identifiers, mode_parameters=None):
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
		fig, (ax1, ax2) = initFigure(2, 1, plot_parameters['StaticBias']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'], shareX=True, subplotWidthRatio=plot_parameters['StaticBias']['subplot_width_ratio'], subplotHeightRatio=plot_parameters['StaticBias']['subplot_height_ratio'])
		ax3 = ax2.twinx() if(vds_setpoint_changes and vgs_setpoint_changes) else None
		
		vds_ax = ax2
		vgs_ax = ax3 if(vds_setpoint_changes) else ax2
	else:
		fig, ax1 = initFigure(1, 1, plot_parameters['StaticBias']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
		ax2, ax3 = None, None
	if(not mode_parameters['publication_mode']):
		ax1.set_title(getTestLabel(deviceHistory, identifiers))
	
	# Build Color Map
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plot_parameters['StaticBias']['colorDefault'], colorMapName=plot_parameters['StaticBias']['colorMap'], colorMapStart=0, colorMapEnd=0.87, enableColorBar=False)		
	
	# If timescale is unspecified, choose an appropriate one based on the data range
	if(timescale == ''):
		timescale = bestTimeScaleFor(deviceHistory[-1]['Results']['timestamps'][-1] - deviceHistory[0]['Results']['timestamps'][0])
	
	# Rescale timestamp data by factor related to the time scale
	deviceHistory = scaledData(deviceHistory, 'Results', 'timestamps', 1/secondsPer(timescale))
	
	# If first segment of device history is mostly negative current, flip data
	if((np.percentile(deviceHistory[0]['Results']['id_data'], 75) < 0)):
		deviceHistory = scaledData(deviceHistory, 'Results', 'id_data', -1)
		plot_parameters['StaticBias']['ylabel'] = plot_parameters['StaticBias']['neg_label']
	
	# === Begin Plotting Data ===
	time_offset = 0
	dotted_lines = []
	parameter_labels = {'drainVoltageSetPoint':[],'gateVoltageSetPoint':[]}
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
		line = plotStaticBias(ax1, deviceHistory[i], colors[i], time_offset, timescale=timescale, lineStyle=None, gradient=mode_parameters['enableGradient'], gradientColors=colorsFromMap(plot_parameters['StaticBias']['colorMap'], 0, 0.95, len(deviceHistory[i]['Results']['timestamps']))['colors'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
		
		# Plot Gate Current (if desired)	
		if(mode_parameters['includeGateCurrent']):
			line = plotStaticBias(ax1, deviceHistory[i], plot_parameters['GateCurrent']['colorDefault'], time_offset, currentData='ig_data', timescale=timescale, lineStyle=None, gradient=False)
			
		# Plot Dual Axis (if desired)
		if(includeDualAxis):
			if(vds_setpoint_changes):
				vds_line = plotOverTime(vds_ax, deviceHistory[i]['Results']['timestamps'], [deviceHistory[i]['runConfigs']['StaticBias']['drainVoltageSetPoint']]*len(deviceHistory[i]['Results']['timestamps']), plt.rcParams['axes.prop_cycle'].by_key()['color'][0], offset=time_offset)
			if(vgs_setpoint_changes):
				vgs_line = plotOverTime(vgs_ax, deviceHistory[i]['Results']['timestamps'], [deviceHistory[i]['runConfigs']['StaticBias']['gateVoltageSetPoint']]*len(deviceHistory[i]['Results']['timestamps']), plt.rcParams['axes.prop_cycle'].by_key()['color'][3], offset=time_offset)
				
		# Compare current plot's parameters to the next ones, and save any differences
		if((i == 0) or (deviceHistory[i]['runConfigs']['StaticBias'] != deviceHistory[i-1]['runConfigs']['StaticBias']) or mode_parameters['staticBiasSegmentDividers']):
			dotted_lines.append({'x':time_offset})
			for key in set(deviceHistory[i]['runConfigs']['StaticBias'].keys()).intersection(deviceHistory[i-1]['runConfigs']['StaticBias'].keys()):
				if((i == 0) or deviceHistory[i]['runConfigs']['StaticBias'][key] != deviceHistory[i-1]['runConfigs']['StaticBias'][key]):
					if(key not in parameter_labels):
						parameter_labels[key] = []
					parameter_labels[key].append({'x':time_offset, key:deviceHistory[i]['runConfigs']['StaticBias'][key]})
	
	# === End Plotting Data ===
	
	# Draw annotations on the main plot
	if(len(dotted_lines) > 1):
		# Draw dotted lines
		if(mode_parameters['staticBiasChangeDividers'] or mode_parameters['staticBiasSegmentDividers']):
			for i in range(len(dotted_lines)):
				ax1.annotate('', xy=(dotted_lines[i]['x'], ax1.get_ylim()[0]), xytext=(dotted_lines[i]['x'], ax1.get_ylim()[1]), xycoords='data', arrowprops=dict(arrowstyle='-', color=(0,0,0,0.3), ls=':', lw=0.5))
		
		# If no dual axis included, then annotate the plot	
		if(not includeDualAxis):
			if(len(parameter_labels['drainVoltageSetPoint']) > 1) or (len(parameter_labels['gateVoltageSetPoint']) > 1):
				# Make the data take up less of the vertical space to make room for the labels
				ax1.set_ylim(top=1.2*ax1.get_ylim()[1])
				
				# Add V_DS annotation
				for i in range(len(parameter_labels['drainVoltageSetPoint'])):
					ax1.annotate(' $V_{DS} = $'+'{:.1f}V'.format(parameter_labels['drainVoltageSetPoint'][i]['drainVoltageSetPoint']), xy=(parameter_labels['drainVoltageSetPoint'][i]['x'], ax1.get_ylim()[1]*(0.99 - 0*0.03*i)), xycoords='data', ha='left', va='top', rotation=-90)

				# Add V_GS annotation
				for i in range(len(parameter_labels['gateVoltageSetPoint'])):
					ax1.annotate(' $V_{GS} = $'+'{:.0f}V'.format(parameter_labels['gateVoltageSetPoint'][i]['gateVoltageSetPoint']), xy=(parameter_labels['gateVoltageSetPoint'][i]['x'], ax1.get_ylim()[1]*(0.90 - 0*0.03*i)), xycoords='data', ha='left', va='bottom', rotation=-90)
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax1, include=plot_parameters['StaticBias']['mainIncludeOrigin'])
	
	# Main Axis Legend
	legend_title = getLegendTitle(deviceHistory, identifiers, plot_parameters['StaticBias'], 'runConfigs', 'StaticBias', mode_parameters, includeVdsHold=(not vds_setpoint_changes), includeVgsHold=(not vgs_setpoint_changes), includeTimeHold=(not biasTime_changes))
	if(len(legend_title) > 0):
		addLegend(ax1, loc=mode_parameters['legendLoc'], title=legend_title)
	
	# Dual Axis Legend, Axis Labels, and save figure
	if(includeDualAxis):
		# Axis labels
		axisLabels(ax1, y_label=plot_parameters['StaticBias']['ylabel'])
		axisLabels(ax2, x_label=plot_parameters['StaticBias']['xlabel'].format(timescale))
		
		if(vds_setpoint_changes):
			includeOriginOnYaxis(vds_ax, include=plot_parameters['StaticBias']['dualIncludeOrigin'])
			vds_ax.set_ylim(bottom=vds_ax.get_ylim()[0] - (vds_ax.get_ylim()[1] - vds_ax.get_ylim()[0])*0.08, top=vds_ax.get_ylim()[1] + (vds_ax.get_ylim()[1] - vds_ax.get_ylim()[0])*0.08)
			axisLabels(vds_ax, y_label=plot_parameters['StaticBias']['vds_label'])
			
		if(vgs_setpoint_changes):
			includeOriginOnYaxis(vgs_ax, include=plot_parameters['StaticBias']['dualIncludeOrigin'])
			axisLabels(vgs_ax, y_label=plot_parameters['StaticBias']['vgs_label'])
			
		if(vds_setpoint_changes and vgs_setpoint_changes):
			setLabel(vds_line, '$V_{DS}^{{Hold}}$')
			setLabel(vgs_line, '$V_{GS}^{{Hold}}$')
			vds_ax.legend(loc=mode_parameters['legendLoc'], borderpad=0.15, labelspacing=0.3, handlelength=0.2, handletextpad=0.2)
			vgs_ax.legend(loc=mode_parameters['legendLoc'], borderpad=0.15, labelspacing=0.3, handlelength=0.2, handletextpad=0.2)
		
		# Adjust tick alignment
		[tick.set_verticalalignment('top') for tick in ax2.yaxis.get_majorticklabels()]
		adjustAndSaveFigure(fig, 'FullStaticBias', mode_parameters, subplotHeightPad=plot_parameters['StaticBias']['subplot_spacing'])
	else:
		axisLabels(ax1, x_label=plot_parameters['StaticBias']['xlabel'].format(timescale), y_label=plot_parameters['StaticBias']['ylabel'])
		adjustAndSaveFigure(fig, 'FullStaticBias', mode_parameters)

	return (fig, (ax1, ax2, ax3))



plot_parameters['OnOffCurrent'] = {
	'figsize':(4.4,3.4),#(2*2.2,2*1.7),#(5,4),
	'time_label':'Time [{:}]',
	'index_label':'Time Index of Gate Sweep [#]',
	'ylabel':'$I_{{ON}}$ [$\\mu$A]',
	'ylabel_dual_axis':'$I_{{OFF}}$ [nA]',
	'vds_label': '$V_{{DS}}^{{Hold}}$ [V]',
	'vgs_label': '$V_{{GS}}^{{Hold}}$ [V]',
	'subplot_height_ratio':[3,1],
	'subplot_width_ratio': [1],
	'subplot_spacing': 0.03
}

def plotOnAndOffCurrentHistory(deviceHistory, identifiers, mode_parameters=None):
	timescale = mode_parameters['timescale']
	plotInRealTime = mode_parameters['plotInRealTime']
	includeDualAxis = mode_parameters['includeDualAxis']
	
	# Check if V_DS or V_GS are changing during this experiment
	vds_setpoint_values = [jsonData['runConfigs']['StaticBias']['drainVoltageSetPoint'] for jsonData in deviceHistory]
	vgs_setpoint_values = [jsonData['runConfigs']['StaticBias']['gateVoltageSetPoint'] for jsonData in deviceHistory]
	vds_setpoint_changes = min(vds_setpoint_values) != max(vds_setpoint_values)
	vgs_setpoint_changes = min(vgs_setpoint_values) != max(vgs_setpoint_values)
	if(not (vds_setpoint_changes or vgs_setpoint_changes)):
		includeDualAxis = False
	
	# Init Figure
	if(includeDualAxis):
		fig, (ax1, ax3) = initFigure(2, 1, plot_parameters['OnOffCurrent']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'], shareX=True, subplotWidthRatio=plot_parameters['OnOffCurrent']['subplot_width_ratio'], subplotHeightRatio=plot_parameters['OnOffCurrent']['subplot_height_ratio'])
		ax4 = ax3.twinx() if(vds_setpoint_changes and vgs_setpoint_changes) else None

		vds_ax = ax3
		vgs_ax = ax4 if(vds_setpoint_changes) else ax3
	else:
		fig, ax1 = initFigure(1, 1, plot_parameters['OnOffCurrent']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
		ax3, ax4 = None, None
	ax2 = ax1.twinx() if(mode_parameters['includeOffCurrent']) else None
	if(not mode_parameters['publication_mode']):
		ax1.set_title(getTestLabel(deviceHistory, identifiers))
	
	# If timescale is unspecified, choose an appropriate one based on the data range
	if(timescale == ''):
		timescale = bestTimeScaleFor(flatten(deviceHistory[-1]['Results']['timestamps'])[-1] - flatten(deviceHistory[0]['Results']['timestamps'])[0])
	
	# Rescale timestamp data by factor related to the time scale
	deviceHistory = scaledData(deviceHistory, 'Results', 'timestamps', 1/secondsPer(timescale))
	
	# Build On/Off Current lists
	onCurrents = []
	offCurrents = []
	timestamps = []
	blacklisted = []
	for i, deviceRun in enumerate(deviceHistory):
		if(abs(deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint']) > 0):
			onCurrents.append(deviceRun['Computed']['onCurrent'] * 10**6)
			offCurrents.append(deviceRun['Computed']['offCurrent'] * 10**9)
			timestamps.append(flatten(deviceRun['Results']['timestamps'])[0])
		else:
			blacklisted.append(i)
	# Get rid of V_DS = 0 sweeps (not meaningful)
	for i in blacklisted:
		del deviceHistory[i]
	
	# Plot On Current
	if(plotInRealTime):
		line = plotOverTime(ax1, timestamps, onCurrents, plt.rcParams['axes.prop_cycle'].by_key()['color'][3], offset=0, markerSize=3, lineWidth=0)
	else:
		line = ax1.plot(range(len(onCurrents)), onCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][3], marker='o', markersize=3, linewidth=0, linestyle=None)[0]
	setLabel(line, 'On-Currents')
	ax1.set_ylim(bottom=0)
	axisLabels(ax1, y_label=plot_parameters['OnOffCurrent']['ylabel'])
	
	# Plot Off Current
	if(mode_parameters['includeOffCurrent']):
		if(plotInRealTime):
			line = plotOverTime(ax2, timestamps, offCurrents, plt.rcParams['axes.prop_cycle'].by_key()['color'][1], offset=0, markerSize=2, lineWidth=0)
		else:
			line = ax2.plot(range(len(offCurrents)), offCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], marker='o', markersize=2, linewidth=0, linestyle=None)
		setLabel(line, 'Off-Currents')
		ax2.set_ylim(top=max(10, max(offCurrents)))
		axisLabels(ax2, y_label=plot_parameters['OnOffCurrent']['ylabel_dual_axis'])
	
	# Plot in Dual Axis
	if(includeDualAxis):
		time_offset = 0
		for i in range(len(deviceHistory)):
			t_0 = timestamps[0]
			t_i = timestamps[i]
			time_offset = (t_i - t_0)
			t_i_next = timestamps[i] + deviceHistory[i]['runConfigs']['StaticBias']['totalBiasTime']/secondsPer(timescale)

			if(vds_setpoint_changes):
				vds_line = plotOverTime(vds_ax, [timestamps[i], t_i_next], [deviceHistory[i]['runConfigs']['StaticBias']['drainVoltageSetPoint']]*2, plt.rcParams['axes.prop_cycle'].by_key()['color'][0], offset=time_offset)
			if(vgs_setpoint_changes):
				vgs_line = plotOverTime(vgs_ax, [timestamps[i], t_i_next], [deviceHistory[i]['runConfigs']['StaticBias']['gateVoltageSetPoint']]*2, plt.rcParams['axes.prop_cycle'].by_key()['color'][3], offset=time_offset)
	
	# Add Legend
	lines1, labels1 = ax1.get_legend_handles_labels()
	lines2, labels2 = [],[]
	legendax = ax1
	if(mode_parameters['includeOffCurrent']):
		lines2, labels2 = ax2.get_legend_handles_labels()
		legendax = ax2
	legendax.legend(lines1 + lines2, labels1 + labels2, loc=mode_parameters['legendLoc'])

	if(includeDualAxis):
		if(plotInRealTime):
			ax3.set_xlabel(plot_parameters['OnOffCurrent']['time_label'].format(timescale))
		else:
			ax3.set_xlabel(plot_parameters['OnOffCurrent']['index_label'])
		if(vds_setpoint_changes):
			vds_ax.set_ylabel(plot_parameters['StaticBias']['vds_label'])
		if(vgs_setpoint_changes):
			vgs_ax.set_ylabel(plot_parameters['StaticBias']['vgs_label'])
		adjustAndSaveFigure(fig, 'OnAndOffCurrents', mode_parameters, subplotHeightPad=plot_parameters['StaticBias']['subplot_spacing'])
	else:
		if(plotInRealTime):
			ax1.set_xlabel(plot_parameters['OnOffCurrent']['time_label'].format(timescale))
		else:
			ax1.set_xlabel(plot_parameters['OnOffCurrent']['index_label'])
		adjustAndSaveFigure(fig, 'OnAndOffCurrents', mode_parameters)
	
	return (fig, (ax1, ax2, ax3, ax4))
	
	
	
plot_parameters['AFMSignalsOverTime'] = {
	'figsize':(5,4),
	'xlabel':'Time',
	'ylabel':'Current'
}

def plotAFMSignalsOverTime(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['AFMSignalsOverTime']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
	ax2 = ax.twinx()
	startTime = min(deviceHistory[0]['Results']['timestamps_device'])
	
	# Plot
	for i in range(len(deviceHistory)):
		ax.set_prop_cycle(None)
		ax2.set_prop_cycle(None)
		line = ax.plot(np.array(deviceHistory[i]['Results']['timestamps_device']) - startTime, np.array(deviceHistory[i]['Results']['id_data'])*1e9)
		ax2.plot([])
		line = ax2.plot(np.array(deviceHistory[i]['Results']['timestamps_smu2']) - startTime, deviceHistory[i]['Results']['smu2_v1_data'], alpha=0.8)
		line = ax2.plot(np.array(deviceHistory[i]['Results']['timestamps_smu2']) - startTime, deviceHistory[i]['Results']['smu2_v2_data'], alpha=0.8)
		
		# if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			# setLabel(line, mode_parameters['legendLabels'][i])
	
	ax.set_ylabel('$I_D$ [nA]')
	ax.set_xlabel('Time [s]')
	ax2.set_ylabel('AFM Voltages [V]', rotation=-90, va='bottom', labelpad=5)
	
	# Add Legend and save figure
	adjustAndSaveFigure(fig, 'FullSubthresholdCurves', mode_parameters)
	
	return (fig, ax)



plot_parameters['AFMdeviationsVsX'] = {
	'figsize':(5,4),
	'colorMap':'plasma'
}

def plotAFMdeviationsVsX(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['AFMdeviationsVsX']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
	# Build Color Map
	colors = colorsFromMap(plot_parameters['AFMdeviationsVsX']['colorMap'], 0, 0.87, len(deviceHistory))['colors']
	# E07N is a sister device, E22N_10000 is another with 40nm device, 5 fin devices E33N E64N, Bigger cavity E27N and E27P 5 fin
	# Bonded devices E07N_10000 (pins 7-8), E08N_10000 (pins 9-10), E22N_10000 (pins 11-12), E27N_10000 (pins 13-14), E33N_10000 (pins 15-16)
	# CNT devices that could be used for AFM: C127V2-3 C127X15-16
	# Plot
	for i in range(len(deviceHistory)):
		current = np.array(deviceHistory[i]['Results']['id_data'])
		currentLinearFit = np.polyval(np.polyfit(range(len(current)), current, 1), range(len(current)))
		currentLinearized = current - currentLinearFit
		currentLinearized = currentLinearized - np.median(currentLinearized)
		
		Vxs = np.array(deviceHistory[i]['Results']['smu2_v2_data'])
		Xs = -Vxs/0.157
		Xs = Xs - np.min(Xs)
		
		line = ax.plot(Xs, currentLinearized*1e9, color=colors[i], alpha=0.01+(1.0/(len(deviceHistory)+1))**0.2)
		
		# if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			# setLabel(line, mode_parameters['legendLabels'][i])
	
	ax.set_ylabel('$I_D$ [nA]')
	ax.set_xlabel('X Position [$\mu$m]')
	
	# Add Legend and save figure
	adjustAndSaveFigure(fig, 'AFMdeviationsVsX', mode_parameters)
	
	return (fig, ax)



plot_parameters['AFMdeviationsVsXY'] = {
	'figsize':(5,4),
	'colorMap':'plasma'
}

def plotAFMdeviationsVsXY(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['AFMdeviationsVsXY']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
	# Build Color Map and Color Bar	
	colors = colorsFromMap(plot_parameters['AFMdeviationsVsXY']['colorMap'], 0, 0.87, len(deviceHistory))['colors']
	
	Vxs = []
	Vys = []
	currents = []
	
	# Plot
	for i in range(len(deviceHistory)):
		current = np.array(deviceHistory[i]['Results']['id_data'])
		currentLinearFit = np.polyval(np.polyfit(range(len(current)), current, 1), range(len(current)))
		currentLinearized = current - currentLinearFit
		currentLinearized = currentLinearized - np.median(currentLinearized)
		
		# currentLinearized[np.where(np.array(deviceHistory[i]['Results']['smu2_v1_data']) - max(deviceHistory[i]['Results']['smu2_v1_data']) < -2.2*0.157)[0]] = 0
		
		Vxs.extend(deviceHistory[i]['Results']['smu2_v2_data'])
		Vys.extend(deviceHistory[i]['Results']['smu2_v1_data'])
		currents.extend(currentLinearized)
	
	Xs = -np.array(Vxs)/0.157
	Ys = np.array(Vys)/0.138
	
	Xs = Xs - np.min(Xs)
	Ys = Ys - np.min(Ys)
	
	# currents[np.where(Xs < 0.5)[0]] = 0
	
	c, a, b = zip(*sorted(zip(np.array(currents)*1e9, Xs, Ys), reverse=True))
	line = ax.scatter(a, b, c=c, cmap=plot_parameters['AFMdeviationsVsXY']['colorMap'], alpha=0.6)
	# line = ax.scatter(Xs, Ys, c=np.array(currents)*1e9, cmap=plot_parameters['AFMdeviationsVsXY']['colorMap'], alpha=0.6)
	cbar = fig.colorbar(line, pad=0.015, aspect=50)
	cbar.set_label('Drain Current [nA]', rotation=270, labelpad=11)
	cbar.solids.set(alpha=1)
	
	# if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
		# setLabel(line, mode_parameters['legendLabels'][i])
	
	ax.set_ylabel('Y Position [$\mu$m]')
	ax.set_xlabel('X Position [$\mu$m]')
	
	# Add Legend and save figure
	adjustAndSaveFigure(fig, 'AFMdeviationsVsXY', mode_parameters)
	
	return (fig, ax)



plot_parameters['ChipHistogram'] = {
	'figsize':(5,4),
	'xlabel':'Device',
	'ylabel':'Experiments'
}

def plotChipHistogram(chipIndexes, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['ChipHistogram']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build index, experiment lists
	devices = list(chipIndexes.keys())
	deviceExperiments = len(devices)*[0]
	for device, indexData in chipIndexes.items():
		deviceExperiments[devices.index(device)] = indexData['experimentNumber']
	
	deviceExperiments, devices = zip(*(reversed(sorted(zip(deviceExperiments, devices)))))

	# Plot
	ax.bar(devices, deviceExperiments)

	# Label axes
	axisLabels(ax, x_label=plot_parameters['ChipHistogram']['xlabel'], y_label=plot_parameters['ChipHistogram']['ylabel'])
	tickLabels(ax, devices, rotation=90)

	# Save figure
	adjustAndSaveFigure(fig, 'ChipHistogram', mode_parameters)
	return (fig, ax)



plot_parameters['ChipOnOffRatios'] = {
	'figsize':(5,4),
	'xlabel':'Device',
	'ylabel':'On/Off Ratio, (Order of Mag)'
}

def plotChipOnOffRatios(firstRunChipHistory, recentRunChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['ChipOnOffRatios']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build On/Off Ratio lists
	devices = []
	firstOnOffRatios = []
	for deviceRun in firstRunChipHistory:
		devices.append(deviceRun['Identifiers']['device']) 
		firstOnOffRatios.append(np.log10(deviceRun['Computed']['onOffRatio']))
	lastOnOffRatios = len(devices)*[0]
	for deviceRun in recentRunChipHistory:
		lastOnOffRatios[devices.index(deviceRun['Identifiers']['device'])] = np.log10(deviceRun['Computed']['onOffRatio'])

	lastOnOffRatios, devices, firstOnOffRatios = zip(*(reversed(sorted(zip(lastOnOffRatios, devices, firstOnOffRatios)))))

	# Plot
	line = ax.plot(range(len(devices)), firstOnOffRatios, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], marker='o', markersize=6, linewidth=0, linestyle=None)[0]
	setLabel(line, 'First Run')
	line = ax.plot(range(len(devices)), lastOnOffRatios, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)[0]
	setLabel(line, 'Most Recent Run')

	# Label axes
	axisLabels(ax, x_label=plot_parameters['ChipOnOffRatios']['xlabel'], y_label=plot_parameters['ChipOnOffRatios']['ylabel'])
	tickLabels(ax, devices, rotation=90)
	
	# Add Legend and save figure
	ax.legend(loc=mode_parameters['legendLoc'])
	adjustAndSaveFigure(fig, 'ChipOnOffRatios', mode_parameters)
	return (fig, ax)
	


plot_parameters['ChipOnOffCurrents'] = {
	'figsize':(5,4),
	'xlabel':'Device',
	'ylabel':'$I_{{ON}}$ [$\\mu$A]',
	'ylabel_dual_axis':'$I_{{OFF}}$ [$\\mu$A]'
}	
	
def plotChipOnOffCurrents(recentRunChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['ChipOnOffCurrents']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	# Build On Current lists
	devices = []
	recentOnCurrents = []
	recentOffCurrents = []
	for deviceRun in recentRunChipHistory:
		devices.append(deviceRun['Identifiers']['device']) 
		recentOnCurrents.append(deviceRun['Computed']['onCurrent'] * 10**6)
		recentOffCurrents.append(deviceRun['Computed']['offCurrent'] * 10**6)

	recentOnCurrents, devices, recentOffCurrents = zip(*(reversed(sorted(zip(recentOnCurrents, devices, recentOffCurrents)))))

	# Plot
	if(mode_parameters['inlcudeOffCurrent']):
		line = ax.plot(range(len(devices)), recentOffCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], marker='o', markersize=8, linewidth=0, linestyle=None)[0]
		setLabel(line, 'Off Currents')
	line = ax.plot(range(len(devices)), recentOnCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)[0]
	setLabel(line, 'On Currents')

	# Label axes
	axisLabels(ax, x_label=plot_parameters['ChipOnOffCurrents']['xlabel'], y_label=plot_parameters['ChipOnOffCurrents']['ylabel'])
	tickLabels(ax, devices, rotation=90)
	
	# Add Legend
	ax.legend(loc=mode_parameters['legendLoc'])
	
	# Save Figure
	adjustAndSaveFigure(fig, 'ChipOnOffCurrents', mode_parameters)
	return (fig, ax)



plot_parameters['plotChipTransferCurves'] = {
	'figsize':(2.8,3.2),
	'colorMap':'plasma',
	'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
	'ylabel':'$I_{{D}}$ [$\\mu$A]',
	'neg_label':'$-I_{{D}}$ [$\\mu$A]',
}

def plotChipTransferCurves(recentRunChipHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['ChipTransferCurves']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title('Chip ' + str(identifiers['wafer']) + str(identifiers['chip']))
	
	# Colors
	colorMap = colorsFromMap(plot_parameters['ChipTransferCurves']['colorMap'], 0, 0.87, len(recentRunChipHistory))
	colors = colorMap['colors']
	if(len(recentRunChipHistory) == 1):
		colors = [plt.rcParams['axes.prop_cycle'].by_key()['color'][1]]
	elif(len(recentRunChipHistory) == 2):
		colors = [plt.rcParams['axes.prop_cycle'].by_key()['color'][1], plt.rcParams['axes.prop_cycle'].by_key()['color'][0]]
	
	# If first segment of device history is mostly negative current, flip data
	if((len(recentRunChipHistory) > 0) and (np.percentile(recentRunChipHistory[0]['Results']['id_data'], 75) < 0)):
		recentRunChipHistory = scaledData(recentRunChipHistory, 'Results', 'id_data', -1)
		plot_parameters['ChipTransferCurves']['ylabel'] = plot_parameters['ChipTransferCurves']['neg_label']
	
	# Plot
	for i in range(len(recentRunChipHistory)):
		line = plotTransferCurve(ax, recentRunChipHistory[i], colors[i], direction=mode_parameters['sweepDirection'], scaleCurrentBy=1e6, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])
		if(len(recentRunChipHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
		
	# Label axes
	axisLabels(ax, x_label=plot_parameters['ChipTransferCurves']['xlabel'], y_label=plot_parameters['ChipTransferCurves']['ylabel'])
	
	# Save Figure
	adjustAndSaveFigure(fig, 'ChipTransferCurves', mode_parameters)
	return (fig, ax)
	
