"""A utility designed to help with the creation a plots with matplotlib that all use a consistent style."""

import matplotlib
from matplotlib import pyplot as plt
from matplotlib import colors as pltc
from matplotlib import cm
import numpy as np
import io
import os

from utilities import FET_Modeling as fet_model

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

try:
	plt.rcParams["legend.title_fontsize"] = 6
except:
	# this is new in Matplotlib version 3.0
	pass

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

# Add custom color-maps
light_to_dark_map = lambda R, G, B: dict({'red':((0.0, 0/255, 0/255), (0.5, R/255, R/255), (1.0, 255/255, 255/255)), 'green':((0.0, 0/255, 0/255), (0.5, G/255, G/255), (1.0, 255/255, 255/255)), 'blue':((0.0, 0/255, 0/255), (0.5, B/255, B/255), (1.0, 255/255, 255/255))})
color_to_color_map = lambda R1, G1, B1, R2, G2, B2: dict({'red':((0.0, R1/255, R1/255), (0.5, 0.5*(R1+R2)/255, 0.5*(R1+R2)/255), (1.0, R2/255, R2/255)), 'green':((0.0, G1/255, G1/255), (0.5, 0.5*(G1+G2)/255, 0.5*(G1+G2)/255), (1.0, G2/255, G2/255)), 'blue':((0.0, B1/255, B1/255), (0.5, 0.5*(B1+B2)/255, 0.5*(B1+B2)/255), (1.0, B2/255, B2/255))})
color_to_color_to_color_map = lambda R1, G1, B1, R2, G2, B2, R3, G3, B3: dict({'red':((0.0, R1/255, R1/255), (0.5, R2/255, R2/255), (1.0, R3/255, R3/255)), 'green':((0.0, G1/255, G1/255), (0.5, G2/255, G2/255), (1.0, G3/255, G3/255)), 'blue':((0.0, B1/255, B1/255), (0.5, B2/255, B2/255), (1.0, B3/255, B3/255))})
rgba_to_rgba_map = lambda R1, G1, B1, A1, R2, G2, B2, A2: dict({'red':((0.0, R1/255, R1/255), (0.5, 0.5*(R1+R2)/255, 0.5*(R1+R2)/255), (1.0, R2/255, R2/255)), 'green':((0.0, G1/255, G1/255), (0.5, 0.5*(G1+G2)/255, 0.5*(G1+G2)/255), (1.0, G2/255, G2/255)), 'blue':((0.0, B1/255, B1/255), (0.5, 0.5*(B1+B2)/255, 0.5*(B1+B2)/255), (1.0, B2/255, B2/255)), 'alpha':((0.0, A1/255, A1/255), (0.5, 0.5*(A1+A2)/255, 0.5*(A1+A2)/255), (1.0, A2/255, A2/255))})


plt.register_cmap(cmap=pltc.LinearSegmentedColormap('white_red_black', light_to_dark_map(237, 85, 59) ))
plt.register_cmap(cmap=pltc.LinearSegmentedColormap('white_green_black', light_to_dark_map(79, 185, 159) ))
plt.register_cmap(cmap=pltc.LinearSegmentedColormap('white_blue_black', light_to_dark_map(31, 119, 180) ))

plt.register_cmap(cmap=pltc.LinearSegmentedColormap('white_yellow_black', light_to_dark_map(242, 177, 52) ))
plt.register_cmap(cmap=pltc.LinearSegmentedColormap('white_purple_black', light_to_dark_map(86, 99, 175) ))
plt.register_cmap(cmap=pltc.LinearSegmentedColormap('white_orange_black', light_to_dark_map(238, 117, 57) ))

plt.register_cmap(cmap=pltc.LinearSegmentedColormap('white_teal_black', light_to_dark_map(28, 206, 167) ))
plt.register_cmap(cmap=pltc.LinearSegmentedColormap('white_lime_black', light_to_dark_map(58, 226, 75) ))
plt.register_cmap(cmap=pltc.LinearSegmentedColormap('white_violet_black', light_to_dark_map(53, 25, 150) ))
plt.register_cmap(cmap=pltc.LinearSegmentedColormap('white_magenta_black', light_to_dark_map(159, 50, 133) ))
plt.register_cmap(cmap=pltc.LinearSegmentedColormap('white_peach_black', light_to_dark_map(255, 142, 101) ))

plt.register_cmap(cmap=pltc.LinearSegmentedColormap('blue_teal_orange', color_to_color_to_color_map(10, 30, 150, 100, 175, 170, 250, 200, 100) ))



# === Matplotlib Access ===
def getPlt():
	return plt

def show():
	print('Showing plots from matplotlib.')
	plt.show()



# *********** Plot Helper Functions ***********
"""Every method in this utility is intended to assist the creation of new plotDefintions in the plotDefinitions folder."""

# === Device Plots ===
def plotSweep(axis, jsonData, lineColor, direction='both', x_data='gate voltage', y_data='drain current', logScale=True, scaleCurrentBy=1, lineStyle=None, errorBars=True):
	data_save_names = {
		'gate voltage': 'vgs_data',
		'drain voltage': 'vds_data',
		'gate current': 'ig_data',
		'drain current': 'id_data',
		
		'input voltage': 'vin_data',
		'output voltage': 'vout_data',
		'input current': 'iin_data',
		'output current': 'iout_data',
	}
	
	y_data = data_save_names[y_data]
	x_data = data_save_names[x_data]
	
	x = jsonData['Results'][x_data]
	y = jsonData['Results'][y_data]

	# Sort data if it was collected in an unordered fashion
	try:
		if(jsonData['runConfigs']['GateSweep']['isAlternatingSweep']):
			forward_x, forward_y = zip(*sorted(zip(x[0], y[0])))
			reverse_x, reverse_y = zip(*reversed(sorted(zip(x[1], y[1]))))
			x = [list(forward_x), list(reverse_x)]
			y = [list(forward_y), list(reverse_y)]
	except:
		pass
	
	# Figure out if data was collected with multiple points per x-value
	pointsPerX = 1
	try:
		if(x_data == 'vgs_data'):
			pointsPerX = jsonData['runConfigs']['GateSweep']['pointsPerVGS']
		elif(x_data == 'vds_data'):
			pointsPerX = jsonData['runConfigs']['DrainSweep']['pointsPerVDS']
		elif(x_data == 'vin_data'):
			pointsPerX = jsonData['runConfigs']['InverterSweep']['pointsPerVIN']
	except:
		pointsPerX = 1

	# Plot only forward or reverse sweeps of the data (also backwards compatible to old format)
	if(direction == 'forward'):
		forward_x = []
		forward_y = []
		for i in [j for j in range(len(x)) if(j % 2 == 0)]:
			forward_x.append(x[i])
			forward_y.append(y[i])
		x = forward_x
		y = forward_y
	elif(direction == 'reverse'):
		reverse_x = []
		reverse_y = []
		for i in [j for j in range(len(x)) if(j % 2 == 1)]:
			reverse_x.append(x[i])
			reverse_y.append(y[i])
		x = reverse_x
		y = reverse_y
	else:
		x = flatten(x)
		y = flatten(y)

	# x and y are flattened and plotted as a single array at this point to be backwards compatible with old data and to simplify data scaling

	# Make y-axis a logarithmic scale
	if(logScale):
		y = abs(np.array(y))
		semiLogScale(axis)

	# Scale the data by a given factor
	y = np.array(y)*scaleCurrentBy

	# Convert x and y to list-of-list form for consistency across all possible data formats
	if(not isinstance(x[0], list)):
		x = [x]
		y = [y]
	
	# Iterate through segments of x and y
	for i in range(len(x)):
		# data contains multiple y-values per x-value
		if(pointsPerX > 1):
			line = plotWithErrorBars(axis, x[i], y[i], lineColor, errorBars=errorBars)
		else:
			if(lineStyle == ''):
				line = axis.plot(x[i], y[i], color=lineColor, marker='o', markersize=2, linewidth=0)[0]
			else:
				line = axis.plot(x[i], y[i], color=lineColor, marker='o', markersize=2, linewidth=1, linestyle=lineStyle)[0]

	return line

def plotSubthresholdCurve(axis, jsonData, lineColor, direction='both', fitSubthresholdSwing=False, includeLabel=False, lineStyle=None, errorBars=True):
	line = plotSweep(axis, jsonData, lineColor, direction, x_data='gate voltage', y_data='drain current', logScale=True, scaleCurrentBy=1, lineStyle=lineStyle, errorBars=errorBars)
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
	line = plotSweep(axis, jsonData, lineColor, direction, x_data='gate voltage', y_data='drain current', logScale=False, scaleCurrentBy=scaleCurrentBy, lineStyle=lineStyle, errorBars=errorBars)
	return line

def plotGateCurrent(axis, jsonData, lineColor, direction='both', scaleCurrentBy=1, lineStyle=None, errorBars=True):
	line = plotSweep(axis, jsonData, lineColor, direction, x_data='gate voltage', y_data='gate current', logScale=False, scaleCurrentBy=scaleCurrentBy, lineStyle=lineStyle, errorBars=errorBars)
	return line

def plotOutputCurve(axis, jsonData, lineColor, direction='both', scaleCurrentBy=1, lineStyle=None, errorBars=True):
	line = plotSweep(axis, jsonData, lineColor, direction, x_data='drain voltage', y_data='drain current', logScale=False, scaleCurrentBy=scaleCurrentBy, lineStyle=lineStyle, errorBars=errorBars)
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

def plotInverterVTC(axis, jsonData, lineColor, direction='both', lineStyle=None, errorBars=True):
	line = plotSweep(axis, jsonData, lineColor, direction, x_data='input voltage', y_data='output voltage', logScale=False, scaleCurrentBy=1, lineStyle=lineStyle, errorBars=errorBars)
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
		print('Saving figures.')
		if isinstance(mode_parameters['plotSaveName'], io.BytesIO):
			plt.savefig(mode_parameters['plotSaveName'], transparent=True, dpi=pngDPI, format='png')
		else:
			plt.savefig(os.path.join(mode_parameters['plotSaveFolder'], mode_parameters['plotSaveName'] + plotType + mode_parameters['plotSaveExtension']), transparent=True, dpi=pngDPI)
			# plt.savefig(os.path.join(mode_parameters['plotSaveFolder'], mode_parameters['plotSaveName'] + plotType + '.pdf'), transparent=True, dpi=pngDPI)
			# plt.savefig(os.path.join(mode_parameters['plotSaveFolder'], mode_parameters['plotSaveName'] + plotType + '.eps'), transparent=True, dpi=pngDPI)
		print('Figures saved.')
	if(not mode_parameters['showFigures']):
		print('Closing figures.')
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

def boxplot(axis, data):
	return axis.boxplot(data, meanline=True, showmeans=True, showfliers=False, medianprops={'color':'#000000'}, meanprops={'color':'#000000'})
	


# === Colors ===
def setupColors(fig, numberOfColors, colorOverride=[], colorDefault=['#1f77b4', '#f2b134', '#4fb99f', '#ed553b', '#56638A'], colorMapName='plasma', colorMapStart=0, colorMapEnd=0.87, enableColorBar=False, colorBarTicks=[0,1], colorBarTickLabels=['End','Start'], colorBarAxisLabel=''):
	if(numberOfColors == len(colorOverride)):
		return colorOverride
	
	colors = None
	if(numberOfColors <= len(colorDefault)):
		colors = colorDefault.copy()
	else:
		colorMap = colorsFromMap(colorMapName, colorMapStart, colorMapEnd, numberOfColors)
		colors = colorMap['colors']
		if(enableColorBar and numberOfColors >= 5):
			colorBar(fig, colorMap['smap'], ticks=colorBarTicks, tick_labels=colorBarTickLabels, axisLabel=colorBarAxisLabel)
	
	#for color in colors:
	#	print(pltc.to_hex(color))
		
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
def addLegend(axis, loc, title, mode_parameters=None):
	if((mode_parameters is not None) and (mode_parameters['enableLegend'] == False)):
		return
	lines, labels = axis.get_legend_handles_labels()
	axis.legend(lines, labels, loc=loc, title=title, labelspacing=(0) if(len(labels) == 0) else (0.3))

def getLegendTitle(deviceHistory, identifiers, plottype_parameters, parameterSuperType, parameterType, mode_parameters=None, includeVdsSweep=False, includeVgsSweep=False, includeIdVgsFit=False, includeVdsHold=False, includeVgsHold=False, includeHoldTime=False, includeTimeHold=False, includeChannelLength=True):
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
		legend_entries.append(plottype_parameters['leg_vgs_label'].format(vgs_min) if(vgs_min == vgs_max) else (plottype_parameters['leg_vgs_range_label'].format(vgs_min, vgs_max)))
	if(includeIdVgsFit and mode_parameters['enableModelFitting']):
		all_fitted_parameters = {'V_T':[], 'mu_Cox_W_L':[], 'SS_mV_dec':[], 'I_OFF':[], 'g_m_max':[]}
		for deviceRun in deviceHistory:
			if(mode_parameters['sweepDirection'] in ['both', 'forward']):
				if(abs(deviceRun['Results']['id_data'][0][0]) > abs(deviceRun['Results']['id_data'][0][-1]) and (deviceRun['Results']['vgs_data'][0][0] < deviceRun['Results']['vgs_data'][0][-1])):
					fwd_id_fitted, fwd_model_parameters, fwd_model_parameters_kw = fet_model.PMOSFET_Fit(deviceRun['Results']['vgs_data'][0], deviceRun['Results']['id_data'][0], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'], I_OFF_min=deviceRun['Computed']['offCurrent']/2, I_OFF_max=deviceRun['Computed']['offCurrent']*2)
				else:
					fwd_id_fitted, fwd_model_parameters, fwd_model_parameters_kw = fet_model.NMOSFET_Fit(deviceRun['Results']['vgs_data'][0], deviceRun['Results']['id_data'][0], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'], I_OFF_min=deviceRun['Computed']['offCurrent']/2, I_OFF_max=deviceRun['Computed']['offCurrent']*2)
				for parameter in all_fitted_parameters.keys():
					all_fitted_parameters[parameter].append(fwd_model_parameters_kw[parameter])
			if(mode_parameters['sweepDirection'] in ['both', 'reverse']):
				if(abs(deviceRun['Results']['id_data'][1][0]) < abs(deviceRun['Results']['id_data'][1][-1]) and (deviceRun['Results']['vgs_data'][1][0] > deviceRun['Results']['vgs_data'][1][-1])):
					rev_id_fitted, rev_model_parameters, rev_model_parameters_kw = fet_model.PMOSFET_Fit(deviceRun['Results']['vgs_data'][1], deviceRun['Results']['id_data'][1], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'], I_OFF_min=deviceRun['Computed']['offCurrent']/2, I_OFF_max=deviceRun['Computed']['offCurrent']*2)
				else:
					rev_id_fitted, rev_model_parameters, rev_model_parameters_kw = fet_model.NMOSFET_Fit(deviceRun['Results']['vgs_data'][1], deviceRun['Results']['id_data'][1], deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint'], I_OFF_guess=deviceRun['Computed']['offCurrent'], I_OFF_min=deviceRun['Computed']['offCurrent']/2, I_OFF_max=deviceRun['Computed']['offCurrent']*2)
				for parameter in all_fitted_parameters.keys():
					all_fitted_parameters[parameter].append(rev_model_parameters_kw[parameter])
		#plt.gca().plot(deviceRun['Results']['vgs_data'][0], 10**6 * np.array(fwd_id_fitted), color='#f2b134')
		VT_avg = np.mean(all_fitted_parameters['V_T'])
		gm_avg = np.mean(all_fitted_parameters['g_m_max'])	
		SS_avg = np.mean(all_fitted_parameters['SS_mV_dec'])
		legend_entries.append('$V_{{T}}^{{avg}} = $ {:.2f}V'.format(VT_avg))
		legend_entries.append('$g_{{m \\cdot max}}^{{avg}} = $ {:.1f}$\\mu$A/V'.format(gm_avg * 10**6))
		legend_entries.append('$SS^{{avg}} = $ {:.0f}mV/dec'.format(SS_avg))
	if(includeVdsHold):	
		legend_entries.append(plottype_parameters['vds_legend'].format(deviceHistory[0][parameterSuperType][parameterType]['drainVoltageSetPoint']))
	if(includeVgsHold):
		legend_entries.append(plottype_parameters['vgs_legend'].format(deviceHistory[0][parameterSuperType][parameterType]['gateVoltageSetPoint']))
	if(includeTimeHold):
		legend_entries.append(plottype_parameters['t_legend'].format(timeWithUnits(np.mean([jsonData[parameterSuperType][parameterType]['totalBiasTime'] for jsonData in deviceHistory]))))
	if(includeChannelLength):
		if((mode_parameters is not None) and (mode_parameters['generalInfo'] is not None)):
			try:
				wafer_info = mode_parameters['generalInfo']
				L_ch = wafer_info['channel_length_nm'][identifiers['chip']][identifiers['device']] if(identifiers['chip'] in wafer_info['channel_length_nm']) else wafer_info['channel_length_nm'][identifiers['device']]
				if(L_ch < 1000):
					legend_entries.append('$L_{{ch}} = $ {:} nm'.format(L_ch))
				else:
					legend_entries.append('$L_{{ch}} = $ {:.1f} $\\mu$m'.format(L_ch/1000))
			except:
				print('Unable to find L_ch for device: ' + str(identifiers) + ' in the provided wafer.json.')
				
	if((mode_parameters is not None) and (mode_parameters['legendTitleSuffix'] != '')):
		legend_entries.append(mode_parameters['legendTitleSuffix'])
	
	# Concatentate legend entries with new lines
	for i in range(len(legend_entries)):
		if(i != 0):
			legend_title += '\n'
		legend_title += legend_entries[i]

	return legend_title
	


# === Curve Fitting ===

## EXAMPLE ##
#for deviceRun in deviceHistory:
#	startIndex, endIndex = steepestRegion(np.log10(np.abs(deviceRun['Results']['id_data'][0])), 10)
#	vgs_region = deviceRun['Results']['vgs_data'][0][startIndex:endIndex]
#	id_region = deviceRun['Results']['id_data'][0][startIndex:endIndex]
#	fitted_region = semilogFit(vgs_region, id_region)['fitted_data']
#	SS_list.append(avgSubthresholdSwing(vgs_region, fitted_region))
#	axis.plot(vgs_region, fitted_region, color='b', linestyle='--')
#SS_avg = np.mean(SS_list)

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
	return (abs( (vgs_data[0] - vgs_data[-1]) / (np.log10(np.abs(id_data[0])) - np.log10(np.abs(id_data[-1]))) ) * 1000)



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



