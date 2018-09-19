import matplotlib
from matplotlib import pyplot as plt
from matplotlib import colors as pltc
from matplotlib import cm
import numpy as np

import io
import os

# ********** Matplotlib Parameters **********

plt.style.use('seaborn-paper')

# plt.rcParams['mathtext.fontset'] = 'custom'
# plt.rcParams['mathtext.rm'] = 'Arial'
# plt.rcParams['mathtext.it'] = 'Arial'
# plt.rcParams['mathtext.bf'] = 'Arial:bold'

# plt.rcParams["font.family"] = 'Times New Roman'
# plt.rcParams['mathtext.rm'] = 'Times New Roman'
# plt.rcParams['mathtext.it'] = 'Times New Roman'
# plt.rcParams['mathtext.bf'] = 'Times New Roman'

# Used for the DRC Abstract
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 8
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['font.size'] = 8

# Minimum Sizes based on Dr. Franklin's Publications (Body text is 10 pt)
plt.rcParams['axes.labelsize'] = 6
plt.rcParams['axes.titlesize'] = 6
plt.rcParams['legend.fontsize'] = 4.5
plt.rcParams['xtick.labelsize'] = 4.5
plt.rcParams['ytick.labelsize'] = 4.5
plt.rcParams['font.size'] = 4.5

# Sizes based on Nature Nanotechnology (Body text is 9 pt)
plt.rcParams['axes.labelsize'] = 7
plt.rcParams['axes.titlesize'] = 7
plt.rcParams['legend.fontsize'] = 7
plt.rcParams['xtick.labelsize'] = 7
plt.rcParams['ytick.labelsize'] = 7
plt.rcParams['font.size'] = 7

# Steven's preferences loosely based on Nature Nanotechnology (Body text is 9 pt)
plt.rcParams['axes.labelsize'] = 7
plt.rcParams['axes.titlesize'] = 7
plt.rcParams['legend.fontsize'] = 6
plt.rcParams['xtick.labelsize'] = 6
plt.rcParams['ytick.labelsize'] = 6
plt.rcParams['font.size'] = 6

plt.rcParams['axes.labelpad'] = 0
plt.rcParams['axes.titlepad'] = 6
plt.rcParams['ytick.major.pad'] = 2
plt.rcParams['xtick.major.pad'] = 2

plt.rcParams['figure.figsize'] = [8,6]
plt.rcParams['figure.titlesize'] = 8
plt.rcParams['axes.formatter.use_mathtext'] = True
plt.rcParams['axes.formatter.useoffset'] = False
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['axes.axisbelow'] = False
# plt.rcParams['figure.autolayout'] = True

plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['xtick.major.width'] = 0.5
plt.rcParams['ytick.major.width'] = 0.5
plt.rcParams['xtick.major.size'] = 3
plt.rcParams['ytick.major.size'] = 3

plt.rcParams['xtick.minor.width'] = 0.5
plt.rcParams['ytick.minor.width'] = 0.5
plt.rcParams['xtick.minor.size'] = 1
plt.rcParams['ytick.minor.size'] = 1

plt.rcParams['axes.formatter.limits'] = [-2, 3]

# Change to Type 2/TrueType fonts (editable text)
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42



# === Plot Parameters ===
default_mode_parameters = {
	'showFigures': True,
	'saveFigures': True,
	'plotSaveFolder': 'CurrentPlots/',
	'plotSaveName': '',
	'plotSaveExtension': '.png',
	
	'publication_mode': False,
	'default_png_dpi': 300,
	
	'figureSizeOverride': None,
	'colorsOverride': [],
	'legendLoc': 'best',
	'legendTitleSuffix':'',
	'legendLabels': [],
	
	'enableErrorBars': True,
	'enableColorBar': True,
	'enableGradient': False,
	
	'sweepDirection': ['both','forward','reverse'][0],
	'timescale': ['','seconds','minutes','hours','days','weeks'][0],
	'plotInRealTime': True,
	
	'includeDualAxis': True,
	'includeOffCurrent': True,
	'includeGateCurrent': False,
	
	'staticBiasSegmentDividers': False,
	'staticBiasChangeDividers': True,
	
	'generalInfo': None
}

plot_parameters = {
	'SubthresholdCurve': {
		'figsize':(2.8,3.2),#(2*1.4,2*1.6),#(4.2,4.9),
		'colorMap':'hot',
		'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][0],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
		'ylabel':'$I_{{D}}$ [A]',
		'leg_vds_label':'$V_{{DS}}^{{Sweep}}$\n  = {:}V',
		'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V'
	},
	'TransferCurve':{
		'figsize':(2.8,3.2),#(2*1.4,2*1.6),#(4.2,4.9),
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
	},
	'GateCurrent':{
		'figsize':(2.8,3.2),#(2*1.4,2*1.6),#(4.2,4.9),
		'includeOrigin':False,
		'colorMap':'hot',
		'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][2],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
		'ylabel':'$I_{{G}}$ [A]',
		'leg_vds_label':'$V_{{DS}}^{{Sweep}} = ${:}V',
		'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V'
	},
	'OutputCurve':{
		'figsize':(2.8,3.2),
		'colorMap':'plasma',
		'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][0],
		'xlabel':'$V_{{DS}}^{{Sweep}}$ [V]',
		'ylabel':'$I_{{D}}$ [$\\mu$A]',
		'neg_label':'$-I_{{D}}$ [$\\mu$A]',
		'leg_vgs_label':'$V_{{GS}}^{{Sweep}}$\n  = {:}V',
		'leg_vgs_range_label':'$V_{{GS}}^{{min}} = $ {:}V\n'+'$V_{{GS}}^{{max}} = $ {:}V'
	},
	'BurnOut':{
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
	},
	'StaticBias':{
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
	},
	'OnCurrent':{
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
	},
	'ChipHistogram':{
		'figsize':(5,4),
		'xlabel':'Device',
		'ylabel':'Experiments'
	},
	'ChipOnOffRatios':{
		'figsize':(5,4),
		'xlabel':'Device',
		'ylabel':'On/Off Ratio, (Order of Mag)'
	},
	'ChipOnOffCurrents':{
		'figsize':(5,4),
		'xlabel':'Device',
		'ylabel':'$I_{{ON}}$ [$\\mu$A]',
		'ylabel_dual_axis':'$I_{{OFF}}$ [$\\mu$A]'
	},
	'ChipTransferCurves':{
		'figsize':(2.8,3.2),
		'colorMap':'plasma',
		'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
		'ylabel':'$I_{{D}}$ [$\\mu$A]',
		'neg_label':'$-I_{{D}}$ [$\\mu$A]',
	},
	'AFMSignalsOverTime':{
		'figsize':(5,4),
		'xlabel':'Time',
		'ylabel':'Current'
	},
	'AFMdeviationsVsX':{
		'figsize':(5,4),
		'colorMap':'plasma'
	},
	'AFMdeviationsVsXY':{
		'figsize':(5,4),
		'colorMap':'plasma'
	}
}



# === External API ===
def makeDevicePlot(plotType, deviceHistory, identifiers, mode_parameters=None):
	if(len(deviceHistory) <= 0):
		print('No ' + str(plotType) + ' device history to plot.')
		return
	
	updated_mode_parameters = default_mode_parameters.copy()
	if(mode_parameters is not None):
		updated_mode_parameters.update(mode_parameters)
	
	if(plotType == 'SubthresholdCurve'):
		fig, axes = plotFullSubthresholdCurveHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'TransferCurve'):
		fig, axes = plotFullTransferCurveHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'GateCurrent'):
		fig, axes = plotFullGateCurrentHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'OutputCurve'):
		fig, axes = plotFullOutputCurveHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'BurnOut'):
		fig, axes = plotFullBurnOutHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'StaticBias'):
		fig, axes = plotFullStaticBiasHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'OnCurrent'):
		fig, axes = plotOnAndOffCurrentHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'AFMSignalsOverTime'):
		fig, axes = plotAFMSignalsOverTime(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'AFMdeviationsVsX'):
		fig, axes = plotAFMdeviationsVsX(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'AFMdeviationsVsXY'):
		fig, axes = plotAFMdeviationsVsXY(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	else:
		raise NotImplementedError('Unrecognized "plotType": ' + str(plotType))
	
	return fig, axes

def makeChipPlot(plotType, identifiers=None, chipIndexes=None, firstRunChipHistory=None, recentRunChipHistory=None, mode_parameters=None):	
	if(plotType is 'ChipHistogram' and ((chipIndexes is None) or len(chipIndexes) <= 0)):
		print('No chip histogram to plot.')
		return
	elif((recentRunChipHistory is None) or len(recentRunChipHistory) <= 0):
		print('No ' + str(plotType) + ' chip history to plot.')
	
	if((recentRunChipHistory is None) or len(recentRunChipHistory) <= 0):
			print('No  ratios to plot.')
			return
	
	updated_mode_parameters = default_mode_parameters.copy()
	if(mode_parameters is not None):
		updated_mode_parameters.update(mode_parameters)

	if(plotType == 'ChipHistogram'):			
		return plotChipHistogram(chipIndexes, mode_parameters=updated_mode_parameters)
	elif(plotType == 'ChipOnOffRatios'):
		return plotChipOnOffRatios(firstRunChipHistory, recentRunChipHistory, mode_parameters=updated_mode_parameters)
	elif(plotType == 'ChipOnOffCurrents'):
		return plotChipOnOffCurrents(recentRunChipHistory, mode_parameters=updated_mode_parameters)
	elif(plotType == 'ChipTransferCurves'):
		return plotChipTransferCurves(recentRunChipHistory, identifiers, mode_parameters=updated_mode_parameters)
	else:
		raise NotImplementedError('Unrecognized "plotType": ' + str(plotType))



# === Internal API ===
def plotFullSubthresholdCurveHistory(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, 'SubthresholdCurve', figsizeOverride=mode_parameters['figureSizeOverride'])
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

	ax.yaxis.set_major_locator(matplotlib.ticker.LogLocator(numticks=10))
	
	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, 'SubthresholdCurve', 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True, includeSubthresholdSwing=False))
	adjustAndSaveFigure(fig, 'FullSubthresholdCurves', mode_parameters)

	return (fig, ax)

def plotFullTransferCurveHistory(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, 'TransferCurve', figsizeOverride=mode_parameters['figureSizeOverride'])
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
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, 'TransferCurve', 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True))
	adjustAndSaveFigure(fig, 'FullTransferCurves', mode_parameters)

	return (fig, ax)

def plotFullGateCurrentHistory(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, 'GateCurrent', figsizeOverride=mode_parameters['figureSizeOverride'])
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

	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plot_parameters['GateCurrent']['includeOrigin'])

	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, 'GateCurrent', 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True))
	adjustAndSaveFigure(fig, 'FullGateCurrents', mode_parameters)

	return (fig, ax)

def plotFullOutputCurveHistory(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, 'OutputCurve', figsizeOverride=mode_parameters['figureSizeOverride'])
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

	# Add Legend and save figure	
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, 'OutputCurve', 'runConfigs', 'DrainSweep', mode_parameters, includeVgsSweep=True))
	adjustAndSaveFigure(fig, 'FullOutputCurves', mode_parameters)

	return (fig, ax)

def plotFullBurnOutHistory(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure	
	fig, (ax1, ax2) = initFigure(1, 2, 'BurnOut', figsizeOverride=mode_parameters['figureSizeOverride'])
	ax2 = plt.subplot(222)
	ax3 = plt.subplot(224)
	if(not mode_parameters['publication_mode']):
		ax1.set_title(getTestLabel(deviceHistory, identifiers))

	# Build Color Map and Color Bar
	plt.sca(ax1)
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plot_parameters['BurnOut']['colorDefault'], colorMapName=plot_parameters['BurnOut']['colorMap'], colorMapStart=0.7, colorMapEnd=0, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,1], colorBarTickLabels=['Final', 'Initial'], colorBarAxisLabel='Burnouts')		

	# Plot
	for i in range(len(deviceHistory)):
		plotBurnOut(ax1, ax2, ax3, deviceHistory[i], colors[i], lineStyle=None)

	# Add Legend and save figure
	addLegend(ax1, loc=mode_parameters['legendLoc'], title=plot_parameters['BurnOut']['legend_title'].format(np.mean([deviceRun['runConfigs']['BurnOut']['gateVoltageSetPoint'] for deviceRun in deviceHistory])))
	addLegend(ax2, loc=mode_parameters['legendLoc'], title=plot_parameters['BurnOut']['legend_title'].format(np.mean([deviceRun['runConfigs']['BurnOut']['gateVoltageSetPoint'] for deviceRun in deviceHistory])))
	addLegend(ax3, loc=mode_parameters['legendLoc'], title=plot_parameters['BurnOut']['legend_title'].format(np.mean([deviceRun['runConfigs']['BurnOut']['gateVoltageSetPoint'] for deviceRun in deviceHistory])))
	adjustAndSaveFigure(fig, 'FullBurnOut', mode_parameters, subplotWidthPad=0.25, subplotHeightPad=0.8)

	return (fig, (ax1, ax2, ax3))

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
		fig, (ax1, ax2) = initFigure(2, 1, 'StaticBias', shareX=True, figsizeOverride=mode_parameters['figureSizeOverride'])
		ax3 = ax2.twinx() if(vds_setpoint_changes and vgs_setpoint_changes) else None
		
		vds_ax = ax2
		vgs_ax = ax3 if(vds_setpoint_changes) else ax2
	else:
		fig, ax1 = initFigure(1, 1, 'StaticBias', figsizeOverride=mode_parameters['figureSizeOverride'])
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
		line = plotStaticBias(ax1, deviceHistory[i], colors[i], time_offset, timescale=timescale, includeLabel=False, lineStyle=None, gradient=mode_parameters['enableGradient'])
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])
		
		# Plot Gate Current (if desired)	
		if(mode_parameters['includeGateCurrent']):
			line = plotStaticBias(ax1, deviceHistory[i], plot_parameters['GateCurrent']['colorDefault'], time_offset, currentData='ig_data', timescale=timescale, includeLabel=False, lineStyle=None, gradient=False)
			
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
	legend_title = getLegendTitle(deviceHistory, identifiers, 'StaticBias', 'runConfigs', 'StaticBias', mode_parameters, includeVdsHold=(not vds_setpoint_changes), includeVgsHold=(not vgs_setpoint_changes), includeTimeHold=(not biasTime_changes))
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
		fig, (ax1, ax3) = initFigure(2, 1, 'OnCurrent', shareX=True, figsizeOverride=mode_parameters['figureSizeOverride'])
		ax4 = ax3.twinx() if(vds_setpoint_changes and vgs_setpoint_changes) else None

		vds_ax = ax3
		vgs_ax = ax4 if(vds_setpoint_changes) else ax3
	else:
		fig, ax1 = initFigure(1, 1, 'OnCurrent', figsizeOverride=mode_parameters['figureSizeOverride'])
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
	axisLabels(ax1, y_label=plot_parameters['OnCurrent']['ylabel'])
	
	# Plot Off Current
	if(mode_parameters['includeOffCurrent']):
		if(plotInRealTime):
			line = plotOverTime(ax2, timestamps, offCurrents, plt.rcParams['axes.prop_cycle'].by_key()['color'][1], offset=0, markerSize=2, lineWidth=0)
		else:
			line = ax2.plot(range(len(offCurrents)), offCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], marker='o', markersize=2, linewidth=0, linestyle=None)
		setLabel(line, 'Off-Currents')
		ax2.set_ylim(top=max(10, max(offCurrents)))
		axisLabels(ax2, y_label=plot_parameters['OnCurrent']['ylabel_dual_axis'])
	
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
			ax3.set_xlabel(plot_parameters['OnCurrent']['time_label'].format(timescale))
		else:
			ax3.set_xlabel(plot_parameters['OnCurrent']['index_label'])
		if(vds_setpoint_changes):
			vds_ax.set_ylabel(plot_parameters['StaticBias']['vds_label'])
		if(vgs_setpoint_changes):
			vgs_ax.set_ylabel(plot_parameters['StaticBias']['vgs_label'])
		adjustAndSaveFigure(fig, 'OnAndOffCurrents', mode_parameters, subplotHeightPad=plot_parameters['StaticBias']['subplot_spacing'])
	else:
		if(plotInRealTime):
			ax1.set_xlabel(plot_parameters['OnCurrent']['time_label'].format(timescale))
		else:
			ax1.set_xlabel(plot_parameters['OnCurrent']['index_label'])
		adjustAndSaveFigure(fig, 'OnAndOffCurrents', mode_parameters)
	
	return (fig, (ax1, ax2, ax3, ax4))

def plotAFMSignalsOverTime(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, 'AFMSignalsOverTime', figsizeOverride=mode_parameters['figureSizeOverride'])
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
	# addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, 'SubthresholdCurve', 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True, includeSubthresholdSwing=False))
	adjustAndSaveFigure(fig, 'FullSubthresholdCurves', mode_parameters)
	
	return (fig, ax)

def plotAFMdeviationsVsX(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, 'AFMdeviationsVsX', figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
	# Build Color Map
	colors = colorsFromMap(plot_parameters['AFMdeviationsVsX']['colorMap'], 0, 0.87, len(deviceHistory))['colors']
	# E07_N is a sister device, E22N_10000 is another with 40nm device, 5 fin devices E33N E64N, Bigger cavity E27N and E27P 5 fin
	# Plot
	for i in range(len(deviceHistory)):
		current = np.array(deviceHistory[i]['Results']['id_data'])
		currentLinearFit = np.polyval(np.polyfit(range(len(current)), current, 1), range(len(current)))
		currentLinearized = current - currentLinearFit
		currentLinearized = currentLinearized - max(currentLinearized)
		
		Vxs = np.array(deviceHistory[i]['Results']['smu2_v2_data'])
		Xs = -Vxs/0.157
		Xs = Xs - np.min(Xs)
		
		line = ax.plot(Xs, currentLinearized*1e9, color=colors[i], alpha=0.01+(1.0/(len(deviceHistory)+1))**0.2)
		
		# if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			# setLabel(line, mode_parameters['legendLabels'][i])
	
	ax.set_ylabel('$I_D$ [nA]')
	ax.set_xlabel('X Position [$\mu$m]')
	
	# Add Legend and save figure
	# addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, 'SubthresholdCurve', 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True, includeSubthresholdSwing=False))
	adjustAndSaveFigure(fig, 'AFMdeviationsVsX', mode_parameters)
	
	return (fig, ax)

def plotAFMdeviationsVsXY(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, 'AFMdeviationsVsXY', figsizeOverride=mode_parameters['figureSizeOverride'])
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
		currentLinearized = currentLinearized - max(currentLinearized)
		
		Vxs.extend(deviceHistory[i]['Results']['smu2_v2_data'])
		Vys.extend(deviceHistory[i]['Results']['smu2_v1_data'])
		currents.extend(currentLinearized)
	
	Xs = -np.array(Vxs)/0.157
	Ys = np.array(Vys)/0.138
	
	Xs = Xs - np.min(Xs)
	Ys = Ys - np.min(Ys)
	
	c, a, b = zip(*sorted(zip(np.array(currents)*1e9, Xs, Ys), reverse=True))
	line = ax.scatter(a, b, c=c, cmap=plot_parameters['AFMdeviationsVsXY']['colorMap'], alpha=0.6)
	# line = ax.scatter(Xs, Ys, c=np.array(currents)*1e9, cmap=plot_parameters['AFMdeviationsVsXY']['colorMap'], alpha=0.6)
	cbar = fig.colorbar(line, pad=0.015, aspect=50)
	cbar.set_label('Drain Current [nA]', rotation=270, labelpad=11)
	cbar.solids.set(alpha=1)
	
	# if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
		# setLabel(line, mode_parameters['legendLabels'][i])
	
	ax.set_ylabel('Y Voltage [V]')
	ax.set_xlabel('X Voltage [V]')
	
	# Add Legend and save figure
	# addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, 'SubthresholdCurve', 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True, includeSubthresholdSwing=False))
	adjustAndSaveFigure(fig, 'AFMdeviationsVsXY', mode_parameters)
	
	return (fig, ax)

def plotChipHistogram(chipIndexes, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, 'ChipHistogram', figsizeOverride=mode_parameters['figureSizeOverride'])

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

def plotChipOnOffRatios(firstRunChipHistory, recentRunChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, 'ChipOnOffRatios', figsizeOverride=mode_parameters['figureSizeOverride'])

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
	
def plotChipOnOffCurrents(recentRunChipHistory, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, 'ChipOnOffCurrents', figsizeOverride=mode_parameters['figureSizeOverride'])

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

def plotChipTransferCurves(recentRunChipHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, 'ChipTransferCurves', figsizeOverride=mode_parameters['figureSizeOverride'])
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

def show():
	plt.show()



# === Device Plots ===
def plotSweep(axis, jsonData, lineColor, direction='both', voltageData='gate', currentData='drain', logScale=True, scaleCurrentBy=1, lineStyle=None, errorBars=True, alphaForwardSweep=1):
	if(currentData == 'gate'):
		currentData = 'ig_data'
	elif(currentData == 'drain'):
		currentData = 'id_data'
	
	if(voltageData == 'gate'):
		voltageData = 'vgs_data'
	elif(voltageData == 'drain'):
		voltageData = 'vds_data'
	
	x = jsonData['Results'][voltageData]
	y = jsonData['Results'][currentData]

	# Sort data if it was collected in an unordered fashion
	try:
		if(jsonData['runConfigs']['GateSweep']['isAlternatingSweep']):
			forward_x, forward_y = zip(*sorted(zip(x[0], y[0])))
			reverse_x, reverse_y = zip(*reversed(sorted(zip(x[1], y[1]))))
			x = [list(forward_x), list(reverse_x)]
			y = [list(forward_y), list(reverse_y)]
	except:
		pass

	# Plot only forward or reverse sweeps of the data (also backwards compatible to old format)
	if(direction == 'forward'):
		x = x[0]
		y = y[0]
	elif(direction == 'reverse'):
		x = x[1]
		y = y[1]
	else:
		if(alphaForwardSweep < 1):
			x = x
			y = y
		else:
			x = flatten(x)
			y = flatten(y)

	# Make y-axis a logarithmic scale
	if(logScale):
		y = abs(np.array(y))
		semiLogScale(axis)

	# Scale the data by a given factor
	y = np.array(y)*scaleCurrentBy

	if(alphaForwardSweep < 1):
		forward_x = x[0]
		forward_y = y[0]
		reverse_x = x[1]
		reverse_y = y[1]
		if(forward_x[0] == forward_x[1]):
			plotWithErrorBars(axis, forward_x, forward_y, lineColor, errorBars=errorBars, alpha=alphaForwardSweep)
			line = plotWithErrorBars(axis, reverse_x, reverse_y, lineColor, errorBars=errorBars)
		else:
			axis.plot(forward_x, forward_y, color=lineColor, marker='o', markersize=2, linewidth=1, linestyle=lineStyle, alpha=alphaForwardSweep)[0]
			line = axis.plot(reverse_x, reverse_y, color=lineColor, marker='o', markersize=2, linewidth=1, linestyle=lineStyle)[0]
	else:
		# data contains multiple y-values per x-value
		if(x[0] == x[1]):
			line = plotWithErrorBars(axis, x, y, lineColor, errorBars=errorBars)
		else:
			line = axis.plot(x, y, color=lineColor, marker='o', markersize=2, linewidth=1, linestyle=lineStyle)[0]

	return line

def plotSubthresholdCurve(axis, jsonData, lineColor, direction='both', fitSubthresholdSwing=False, includeLabel=False, lineStyle=None, errorBars=True):
	line = plotSweep(axis, jsonData, lineColor, direction, voltageData='gate', currentData='drain', logScale=True, scaleCurrentBy=1, lineStyle=lineStyle, errorBars=errorBars)
	axisLabels(axis, x_label=plot_parameters['SubthresholdCurve']['xlabel'], y_label=plot_parameters['SubthresholdCurve']['ylabel'])
	if(includeLabel): 
		#setLabel(line, '$log_{10}(I_{on}/I_{off})$'+': {:.1f}'.format(np.log10(jsonData['Computed']['onOffRatio'])))
		setLabel(line, 'max $|I_{g}|$'+': {:.2e}'.format(jsonData['Computed']['ig_max']))
	if(fitSubthresholdSwing):
		startIndex, endIndex = steepestRegion(np.log10(np.abs(jsonData['Results']['id_data'][0])), 10)
		vgs_region = jsonData['Results']['vgs_data'][0][startIndex:endIndex]
		id_region = jsonData['Results']['id_data'][0][startIndex:endIndex]
		fitted_region = semilogFit(vgs_region, id_region)['fitted_data']
		print(avgSubthresholdSwing(vgs_region, fitted_region))
		axis.plot(vgs_region, fitted_region, color='b', linestyle='--')
	return line

def plotTransferCurve(axis, jsonData, lineColor, direction='both', scaleCurrentBy=1, lineStyle=None, errorBars=True):
	line = plotSweep(axis, jsonData, lineColor, direction, voltageData='gate', currentData='drain', logScale=False, scaleCurrentBy=scaleCurrentBy, lineStyle=lineStyle, errorBars=errorBars)
	axisLabels(axis, x_label=plot_parameters['TransferCurve']['xlabel'], y_label=plot_parameters['TransferCurve']['ylabel'])
	return line

def plotGateCurrent(axis, jsonData, lineColor, direction='both', scaleCurrentBy=1, lineStyle=None, errorBars=True):
	line = plotSweep(axis, jsonData, lineColor, direction, voltageData='gate', currentData='gate', logScale=False, scaleCurrentBy=scaleCurrentBy, lineStyle=lineStyle, errorBars=errorBars)
	axisLabels(axis, x_label=plot_parameters['GateCurrent']['xlabel'], y_label=plot_parameters['GateCurrent']['ylabel'])
	return line

def plotOutputCurve(axis, jsonData, lineColor, direction='both', scaleCurrentBy=1, lineStyle=None, errorBars=True):
	line = plotSweep(axis, jsonData, lineColor, direction, voltageData='drain', currentData='drain', logScale=False, scaleCurrentBy=scaleCurrentBy, lineStyle=lineStyle, errorBars=errorBars)
	axisLabels(axis, x_label=plot_parameters['OutputCurve']['xlabel'], y_label=plot_parameters['OutputCurve']['ylabel'])
	return line

def plotBurnOut(axis1, axis2, axis3, jsonData, lineColor, lineStyle=None, annotate=False, plotLine1=True, plotLine2=True, plotLine3=True):
	line1, line2, line3 = None, None, None
	if(plotLine1):
		line1 = axis1.plot(jsonData['Results']['vds_data'], (np.array(jsonData['Results']['id_data'])*10**6), color=lineColor, linestyle=lineStyle)[0]
		axisLabels(axis1, x_label=plot_parameters['BurnOut']['vds_label'], y_label=plot_parameters['BurnOut']['id_micro_label'])

	# Add burn threshold annotation
	if(annotate):
		currentThreshold = np.percentile(np.array(jsonData['Results']['id_data']), 90) * jsonData['runConfigs']['BurnOut']['thresholdProportion'] * 10**6
		axis1.plot([0, jsonData['Results']['vds_data'][-1]], [currentThreshold, currentThreshold], color=lineColor, linestyle='--', linewidth=1)
		axis1.annotate(plot_parameters['BurnOut']['id_annotation'], xy=(0, currentThreshold), xycoords='data', horizontalalignment='left', verticalalignment='bottom', color=lineColor)
	
	if(plotLine2):
		line2 = plotOverTime(axis2, jsonData['Results']['timestamps'], (np.array(jsonData['Results']['id_data'])*10**6), lineColor)	
		axisLabels(axis2, x_label=plot_parameters['BurnOut']['time_label'], y_label=plot_parameters['BurnOut']['id_micro_label'])

	if(plotLine3):
		line3 = plotOverTime(axis3, jsonData['Results']['timestamps'], jsonData['Results']['vds_data'], lineColor)
		axisLabels(axis3, x_label=plot_parameters['BurnOut']['time_label'], y_label=plot_parameters['BurnOut']['vds_label'])
	return (line1, line2, line3)

def plotStaticBias(axis, jsonData, lineColor, timeOffset, currentData='id_data', timescale='seconds', includeLabel=True, lineStyle=None, gradient=False):
	line = plotOverTime(axis, jsonData['Results']['timestamps'], (np.array(jsonData['Results'][currentData])*(10**6)), lineColor, offset=timeOffset, plotInnerGradient=gradient)	
	if(includeLabel):
		axisLabels(axis, x_label=plot_parameters['StaticBias']['xlabel'].format(timescale), y_label=plot_parameters['StaticBias']['ylabel'])
	return line



# === Figures ===
def initFigure(rows, columns, plotType, shareX=False, figsizeOverride=None):
	if(figsizeOverride != None):
		plot_parameters[plotType]['figsize'] = figsizeOverride
	if(rows > 1 or columns > 1):
		fig, axes = plt.subplots(rows, columns, figsize=plot_parameters[plotType]['figsize'], sharex=shareX, gridspec_kw={'width_ratios':plot_parameters[plotType]['subplot_width_ratio'], 'height_ratios':plot_parameters[plotType]['subplot_height_ratio']})
	else:
		fig, axes = plt.subplots(rows, columns, figsize=plot_parameters[plotType]['figsize'])
	return fig, axes

def adjustAndSaveFigure(figure, plotType, mode_parameters, subplotWidthPad=0, subplotHeightPad=0):
	# figure.set_size_inches(2.2,1.6) # Static Bias
	# figure.set_size_inches(1.4,1.6) # Subthreshold Curve
	# figure.set_size_inches(2.2,1.7) # On/Off-Current	
	# figure.align_labels()
	figure.tight_layout()
	plt.subplots_adjust(wspace=subplotWidthPad, hspace=subplotHeightPad)
	pngDPI = (300) if(mode_parameters['publication_mode']) else (mode_parameters['default_png_dpi'])
	if(mode_parameters['saveFigures']):
		if isinstance(mode_parameters['plotSaveName'], io.BytesIO):
			plt.savefig(mode_parameters['plotSaveName'], transparent=True, dpi=pngDPI, format='png')
		else:
			plt.savefig(os.path.join(mode_parameters['plotSaveFolder'], mode_parameters['plotSaveName'] + plotType + mode_parameters['plotSaveExtension']), transparent=True, dpi=pngDPI)
			# plt.savefig(os.path.join(mode_parameters['plotSaveFolder'], mode_parameters['plotSaveName'] + plotType + '.pdf'), transparent=True, dpi=pngDPI)
			# plt.savefig(os.path.join(mode_parameters['plotSaveFolder'], mode_parameters['plotSaveName'] + plotType + '.eps'), transparent=True, dpi=pngDPI)
	if(not mode_parameters['showFigures']):
		plt.close(figure)



# === Plots === 
def plotWithErrorBars(axis, x, y, lineColor, errorBars=True, alpha=1):
	x_unique, avg, std = avgAndStdAtEveryPoint(x, y)
	if(not errorBars):
		std = None
	return axis.errorbar(x_unique, avg, yerr=std, color=lineColor, capsize=2, capthick=0.5, elinewidth=0.5, alpha=alpha)[0]

def plotOverTime(axis, timestamps, y, lineColor, offset=0, markerSize=1, lineWidth=1, lineStyle=None, plotInnerGradient=False):
	zeroed_timestamps = list( np.array(timestamps) - timestamps[0] + offset )
	if(not plotInnerGradient):
		return axis.plot(zeroed_timestamps, y, color=lineColor, marker='o', markersize=markerSize, linewidth=lineWidth, linestyle=lineStyle)[0]
	else:
		colors = colorsFromMap(plot_parameters['StaticBias']['colorMap'], 0, 0.95, len(y))['colors']
		N = len(y)//20
		if N < 1:
			N = 1
		for i in range(0, len(y)-1, N):
			p = axis.plot(zeroed_timestamps[i:i+1+N], y[i:i+1+N], color=colors[i])
		return p[0]


# === Colors ===
def setupColors(fig, numberOfColors, colorOverride=[], colorDefault=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], colorMapName='plasma', colorMapStart=0, colorMapEnd=0.87, enableColorBar=False, colorBarTicks=[0,1], colorBarTickLabels=['End','Start'], colorBarAxisLabel=''):
	if(numberOfColors == len(colorOverride)):
		return colorOverride
	
	colors = None
	if(numberOfColors == 1):
		colors = [colorDefault]
	elif(numberOfColors == 2):
		colors = [plt.rcParams['axes.prop_cycle'].by_key()['color'][1], plt.rcParams['axes.prop_cycle'].by_key()['color'][0]]
	else:
		colorMap = colorsFromMap(colorMapName, colorMapStart, colorMapEnd, numberOfColors)
		colors = colorMap['colors']
		if(enableColorBar):
			colorBar(fig, colorMap['smap'], ticks=colorBarTicks, tick_labels=colorBarTickLabels, axisLabel=colorBarAxisLabel)
		
	return colors

def colorsFromMap(mapName, colorStartPoint, colorEndPoint, numberOfColors):
	scalarColorMap = cm.ScalarMappable(norm=pltc.Normalize(vmin=0, vmax=1.0), cmap=mapName)
	return {'colors':[scalarColorMap.to_rgba(i) for i in np.linspace(colorStartPoint, colorEndPoint, numberOfColors)], 'smap':scalarColorMap}

def colorBar(fig, scalarMappableColorMap, ticks=[0,1], tick_labels=['End','Start'], axisLabel='Time'):
	scalarMappableColorMap._A = []
	cbar = fig.colorbar(scalarMappableColorMap, pad=0.02, aspect=50)
	cbar.set_ticks(ticks)
	cbar.ax.set_yticklabels(tick_labels, rotation=270)
	cbar.ax.yaxis.get_majorticklabels()[0].set_verticalalignment('bottom')
	cbar.ax.yaxis.get_majorticklabels()[-1].set_verticalalignment('top')
	if len(ticks) > 2:
		for i in range(len(ticks) - 2):
			cbar.ax.yaxis.get_majorticklabels()[i+1].set_verticalalignment('center')
	cbar.set_label(axisLabel, rotation=270, labelpad=0.9)



# === Labels ===
def setLabel(line, label):
	line.set_label(label)

def semiLogScale(axis):
	axis.set_yscale('log')

def axisLabels(axis, x_label=None, y_label=None):
	if(x_label is not None):
		axis.set_xlabel(x_label)
	if(y_label is not None):
		axis.set_ylabel(y_label)

def tickLabels(axis, labelList, rotation=0):
	axis.set_xticklabels(labelList)
	axis.set_xticks(range(len(labelList)))
	axis.xaxis.set_tick_params(rotation=rotation)

def includeOriginOnYaxis(axis, include=True):
	if(include):
		if(axis.get_ylim()[1] < 0):
			axis.set_ylim(top=0)
		elif(axis.get_ylim()[0] > 0):
			axis.set_ylim(bottom=0)	
		
def getTestLabel(deviceHistory, identifiers):
	if(identifiers is None):
		return ''
	
	label = str(identifiers['wafer']) + str(identifiers['chip']) + ':' + identifiers['device']
	if len(deviceHistory) > 0:
		test1Num = deviceHistory[0]['experimentNumber']
		test2Num = deviceHistory[-1]['experimentNumber']
		if test1Num == test2Num:
			label += ', Test {:}'.format(test1Num)
		else:
			label += ', Tests {:}-{:}'.format(test1Num, test2Num)
	return label



# === Legend ===
def addLegend(axis, loc, title):
	lines, labels = axis.get_legend_handles_labels()
	axis.legend(lines, labels, loc=loc, title=title, labelspacing=(0) if(len(labels) == 0) else (0.3))

def getLegendTitle(deviceHistory, identifiers, plotType, parameterSuperType, parameterType, mode_parameters=None, includeVdsSweep=False, includeVgsSweep=False, includeSubthresholdSwing=False, includeVdsHold=False, includeVgsHold=False, includeHoldTime=False, includeTimeHold=False, includeChannelLength=True):
	legend_title = ''
	legend_entries = []
	if(includeVdsSweep):
		vds_list = getParameterArray(deviceHistory, parameterSuperType, parameterType, 'drainVoltageSetPoint')
		vds_min = min(vds_list)
		vds_max = max(vds_list)
		legend_entries.append(plot_parameters[plotType]['leg_vds_label'].format(vds_min) if(vds_min == vds_max) else (plot_parameters[plotType]['leg_vds_range_label'].format(vds_min, vds_max)))
	if(includeVgsSweep):
		vgs_list = getParameterArray(deviceHistory, parameterSuperType, parameterType, 'gateVoltageSetPoint')
		vgs_min = min(vgs_list)
		vgs_max = max(vgs_list)
		legend_entries.append(plot_parameters[plotType]['leg_vgs_label'].format(vgs_min) if(vgs_min == vgs_max) else (plot_parameters[plotType]['leg_vds_range_label'].format(vgs_min, vgs_max)))
	if(includeSubthresholdSwing):
		SS_list = []
		for deviceRun in deviceHistory:
			startIndex, endIndex = steepestRegion(np.log10(np.abs(deviceRun['Results']['id_data'][0])), 10)
			vgs_region = deviceRun['Results']['vgs_data'][0][startIndex:endIndex]
			id_region = deviceRun['Results']['id_data'][0][startIndex:endIndex]
			fitted_region = semilogFit(vgs_region, id_region)['fitted_data']
			SS_list.append(avgSubthresholdSwing(vgs_region, fitted_region))
			#axis.plot(vgs_region, fitted_region, color='b', linestyle='--')
		SS_avg = np.mean(SS_list)
		legend_entries.append('$SS_{{avg}} = $ {:.0f}mV/dec'.format(SS_avg))
	if(includeVdsHold):	
		legend_entries.append(plot_parameters[plotType]['vds_legend'].format(deviceHistory[0][parameterSuperType][parameterType]['drainVoltageSetPoint']))
	if(includeVgsHold):
		legend_entries.append(plot_parameters[plotType]['vgs_legend'].format(deviceHistory[0][parameterSuperType][parameterType]['gateVoltageSetPoint']))
	if(includeTimeHold):
		legend_entries.append(plot_parameters[plotType]['t_legend'].format(timeWithUnits(np.mean([jsonData[parameterSuperType][parameterType]['totalBiasTime'] for jsonData in deviceHistory]))))
	if(includeChannelLength):
		if((mode_parameters is not None) and (mode_parameters['generalInfo'] is not None)):
			wafer_info = mode_parameters['generalInfo']
			L_ch = wafer_info['channel_length_nm'][identifiers['device']]
			if(L_ch < 1000):
				legend_entries.append('$L_{{ch}} = $ {:} nm'.format(L_ch))
			else:
				legend_entries.append('$L_{{ch}} = $ {:.1f} $\\mu$m'.format(L_ch/1000))
				
	if((mode_parameters is not None) and (mode_parameters['legendTitleSuffix'] != '')):
		legend_entries.append(mode_parameters['legendTitleSuffix'])
	
	# Concatentate legend entries with new lines
	for i in range(len(legend_entries)):
		if(i != 0):
			legend_title += '\n'
		legend_title += legend_entries[i]

	return legend_title
	


# === Curve Fitting ===
def linearFit(x, y):
	slope, intercept = np.polyfit(x, y, 1)
	fitted_data = [slope*x[i] + intercept for i in range(len(x))]
	return {'fitted_data': fitted_data,'slope':slope, 'intercept':intercept}

def quadraticFit(x, y):
	a, b, c = np.polyfit(x, y, 2)
	fitted_data = [(a*(x[i]**2) + b*x[i] + c) for i in range(len(x))]
	return {'fitted_data': fitted_data, 'a':a, 'b':b, 'c':c}

def semilogFit(x, y):
	fit_results = linearFit(x, np.log10(np.abs(y)))
	fitted_data = [10**(fit_results['fitted_data'][i]) for i in range(len(fit_results['fitted_data']))]
	return {'fitted_data': fitted_data}

def steepestRegion(data, numberOfPoints):
	maxSlope = 0
	index = 0
	for i in range(len(data) - 1):
		diff = abs(data[i] - data[i+1])
		if(diff > maxSlope):
			maxSlope = diff
			index = i
	regionStart = max(0, index - numberOfPoints/2)
	regionEnd = min(len(data)-1, index + numberOfPoints/2)
	return (int(regionStart), int(regionEnd))



# === Metrics ===
def avgSubthresholdSwing(vgs_data, id_data):
	return (abs( vgs_data[0] - vgs_data[-1] / (np.log10(np.abs(id_data[0])) - np.log10(np.abs(id_data[-1]))) ) * 1000)



# === Statistics ===
def avgAndStdAtEveryPoint(x, y):
	x_uniques = []
	y_averages = []
	y_standardDeviations = []
	i = 0
	while (i < len(y)):
		j = nextIndexToBeDifferent(x, i)
		x_uniques.append(x[i])
		y_averages.append(np.mean(y[i:j]))
		y_standardDeviations.append(np.std(y[i:j]))
		i = j

	return (x_uniques, y_averages, y_standardDeviations)

def nextIndexToBeDifferent(data, i):
	value = data[i]
	while((i < len(data)) and (data[i] == value)):
		i += 1
	return i

def secondsPer(amountOfTime):
	if(amountOfTime == 'seconds'):
		return 1
	elif(amountOfTime == 'minutes'):
		return 60
	elif(amountOfTime == 'hours'):
		return 3600
	elif(amountOfTime == 'days'):
		return 3600*24
	elif(amountOfTime == 'weeks'):
		return 3600*24*7
	elif(amountOfTime == 'months'):
		return 3600*24*30
	else: 
		return 0

def timeWithUnits(seconds):
	time = seconds
	unit = 's'
	threshold = 2
	
	if seconds >= 60*60*24*30:
		time = seconds/(60*60*24*30)
		unit = 'month'
	elif seconds >= 60*60*24*7:
		time = seconds/(60*60*24*7)
		unit = 'wk'
	elif seconds >= 60*60*24:
		time = seconds/(60*60*24)
		unit = 'day' if int(time) == 1 else 'days'
	elif seconds >= 60*60:
		time = seconds/(60*60)
		unit = 'hr'
	elif seconds >= 60:
		time = seconds/(60)
		unit = 'min'
	elif seconds >= 60:
		time = seconds/(1)
		unit = 's'
	
	return '{} {}'.format(int(time), unit)

def bestTimeScaleFor(seconds):
	if(seconds < 2*60):
		return 'seconds'
	elif(seconds < 2*60*60):
		return 'minutes'
	elif(seconds < 2*60*60*24):
		return 'hours'
	elif(seconds < 2*60*60*24*7):
		return 'days'
	elif(seconds < 2*60*60*24*30):
		return 'weeks'
	else:
		return 'months'



# === Data Manipulation ===
def flatten(dataList):
	data = list([dataList])
	while(isinstance(data[0], list)):
		data = [(item) for sublist in data for item in sublist]
	return data

def scaledData(deviceHistory, dataSubdirectory, dataToScale, scalefactor):
	data = list(deviceHistory)
	for i in range(len(data)):
		data_entry = data[i][dataSubdirectory][dataToScale]
		if(isinstance(data_entry[0], list)):
			for j in range(len(data_entry)):
				data_entry[j] = list(np.array(data_entry[j])*scalefactor)
		else:
			data_entry = list(np.array(data_entry)*scalefactor)
		data[i][dataSubdirectory][dataToScale] = data_entry
	return data

def getParameterArray(deviceHistory, parameterSuperType, parameterSubType, parameterName):
	result = []
	for i in range(len(deviceHistory)):
		element = deviceHistory[i]
		if(parameterSuperType != ''):
			element = element[parameterSuperType]
		if(parameterSubType != ''):
			element = element[parameterSubType]
		result.append(element[parameterName])
	return result



