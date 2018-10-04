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



# === Matplotlib Access ===
def getPlt():
	return plt

def show():
	plt.show()



# *********** Plot Helper Functions ***********

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
	return line

def plotGateCurrent(axis, jsonData, lineColor, direction='both', scaleCurrentBy=1, lineStyle=None, errorBars=True):
	line = plotSweep(axis, jsonData, lineColor, direction, voltageData='gate', currentData='gate', logScale=False, scaleCurrentBy=scaleCurrentBy, lineStyle=lineStyle, errorBars=errorBars)
	return line

def plotOutputCurve(axis, jsonData, lineColor, direction='both', scaleCurrentBy=1, lineStyle=None, errorBars=True):
	line = plotSweep(axis, jsonData, lineColor, direction, voltageData='drain', currentData='drain', logScale=False, scaleCurrentBy=scaleCurrentBy, lineStyle=lineStyle, errorBars=errorBars)
	return line

def plotBurnOut(axis1, axis2, axis3, jsonData, lineColor, lineStyle=None, annotate=False, annotation='', plotLine1=True, plotLine2=True, plotLine3=True):
	line1, line2, line3 = None, None, None
	if(plotLine1):
		line1 = axis1.plot(jsonData['Results']['vds_data'], (np.array(jsonData['Results']['id_data'])*10**6), color=lineColor, linestyle=lineStyle)[0]

	# Add burn threshold annotation
	if(annotate):
		currentThreshold = np.percentile(np.array(jsonData['Results']['id_data']), 90) * jsonData['runConfigs']['BurnOut']['thresholdProportion'] * 10**6
		axis1.plot([0, jsonData['Results']['vds_data'][-1]], [currentThreshold, currentThreshold], color=lineColor, linestyle='--', linewidth=1)
		axis1.annotate(annotation, xy=(0, currentThreshold), xycoords='data', horizontalalignment='left', verticalalignment='bottom', color=lineColor)
	
	if(plotLine2):
		line2 = plotOverTime(axis2, jsonData['Results']['timestamps'], (np.array(jsonData['Results']['id_data'])*10**6), lineColor)	
	if(plotLine3):
		line3 = plotOverTime(axis3, jsonData['Results']['timestamps'], jsonData['Results']['vds_data'], lineColor)
	return (line1, line2, line3)

def plotStaticBias(axis, jsonData, lineColor, timeOffset, currentData='id_data', timescale='seconds', lineStyle=None, gradient=False, gradientColors=None):
	line = plotOverTime(axis, jsonData['Results']['timestamps'], (np.array(jsonData['Results'][currentData])*(10**6)), lineColor, offset=timeOffset, plotInnerGradient=gradient, innerGradientColors=gradientColors)	
	return line



# === Figures ===
def initFigure(rows, columns, figsizeDefault, figsizeOverride=None, shareX=False, subplotWidthRatio=None, subplotHeightRatio=None):
	figsize = figsizeDefault
	if(figsizeOverride != None):
		figsize = figsizeOverride
		
	if(rows > 1 or columns > 1):
		fig, axes = plt.subplots(rows, columns, figsize=figsize, sharex=shareX, gridspec_kw={'width_ratios':subplotWidthRatio, 'height_ratios':subplotHeightRatio})
	else:
		fig, axes = plt.subplots(rows, columns, figsize=figsize)
		
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

def plotOverTime(axis, timestamps, y, lineColor, offset=0, markerSize=1, lineWidth=1, lineStyle=None, plotInnerGradient=False, innerGradientColors=None):
	zeroed_timestamps = list( np.array(timestamps) - timestamps[0] + offset )
	if(not plotInnerGradient):
		return axis.plot(zeroed_timestamps, y, color=lineColor, marker='o', markersize=markerSize, linewidth=lineWidth, linestyle=lineStyle)[0]
	else:
		N = len(y)//20
		if N < 1:
			N = 1
		for i in range(0, len(y)-1, N):
			p = axis.plot(zeroed_timestamps[i:i+1+N], y[i:i+1+N], color=innerGradientColors[i])
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

def getLegendTitle(deviceHistory, identifiers, plottype_parameters, parameterSuperType, parameterType, mode_parameters=None, includeVdsSweep=False, includeVgsSweep=False, includeSubthresholdSwing=False, includeVdsHold=False, includeVgsHold=False, includeHoldTime=False, includeTimeHold=False, includeChannelLength=True):
	legend_title = ''
	legend_entries = []
	if(includeVdsSweep):
		vds_list = getParameterArray(deviceHistory, parameterSuperType, parameterType, 'drainVoltageSetPoint')
		vds_min = min(vds_list)
		vds_max = max(vds_list)
		legend_entries.append(plottype_parameters['leg_vds_label'].format(vds_min) if(vds_min == vds_max) else (plottype_parameters['leg_vds_range_label'].format(vds_min, vds_max)))
	if(includeVgsSweep):
		vgs_list = getParameterArray(deviceHistory, parameterSuperType, parameterType, 'gateVoltageSetPoint')
		vgs_min = min(vgs_list)
		vgs_max = max(vgs_list)
		legend_entries.append(plottype_parameters['leg_vgs_label'].format(vgs_min) if(vgs_min == vgs_max) else (plottype_parameters['leg_vds_range_label'].format(vgs_min, vgs_max)))
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
		legend_entries.append(plottype_parameters['vds_legend'].format(deviceHistory[0][parameterSuperType][parameterType]['drainVoltageSetPoint']))
	if(includeVgsHold):
		legend_entries.append(plottype_parameters['vgs_legend'].format(deviceHistory[0][parameterSuperType][parameterType]['gateVoltageSetPoint']))
	if(includeTimeHold):
		legend_entries.append(plottype_parameters['t_legend'].format(timeWithUnits(np.mean([jsonData[parameterSuperType][parameterType]['totalBiasTime'] for jsonData in deviceHistory]))))
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



