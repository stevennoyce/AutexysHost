from utilities import MatplotlibUtility as mplu

import pkgutil
import os
import glob

# Import all Plot Definitions and save a reference to run their 'plot' function
plotDefinitions = {}
plotDefinitionsBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'PlotDefinitions')
for importer, packageName, isPackage in pkgutil.iter_modules([plotDefinitionsBasePath] + glob.glob(plotDefinitionsBasePath + '/*/')):
	module = importer.find_module(packageName).load_module(packageName)
	plotDefinitions[packageName] = {}
	plotDefinitions[packageName]['module'] = module
	plotDefinitions[packageName]['description'] = module.plotDescription
	plotDefinitions[packageName]['function'] = module.plot



# === Plot Parameters ===
default_mode_parameters = {
	# Figure saving options
	'showFigures': True,
	'saveFigures': True,
	'plotSaveFolder': '../../AutexysPlots/',
	'plotSaveName': '',
	'plotSaveExtension': '.png',
	
	# Figure loaded data passthroughs
	'generalInfo': None,
	'AFMImagePath': None,
	
	# Image quality
	'publication_mode': False,
	'default_png_dpi': 300,
	
	# Generic complex options
	'figureSizeOverride': None,
	'colorsOverride': [],
	'legendLoc': 'best',
	'legendLabels': [],
	'legendTitleOverride':'',
	
	# Generic axis options
	'xlim': None,
	'ylim': None,
	'xscale': None,
	'yscale': None,
	'xticks': None,
	'yticks': None,
	
	# Generic enable/disable options
	'enableLegend':    True,
	'enableErrorBars': False,
	'enableColorBar':  True,
	'enableGradient':  False,
	
	# Plot-specific options
	'sweepDirection': ['both','forward','reverse'][0],
	'timescale': ['','seconds','minutes','hours','days','weeks'][0],
	'plotInRealTime': True,
	'boxPlotBarChart':True,
	'boxPlotShowPoints':True,
	'boxPlotCategories':[('',float('inf'))],
	
	# Plot-specific sub-plot options
	'includeDualAxis': True,	
	'staticBiasSegmentDividers': False,
	'staticBiasChangeDividers': True,
}



# === External API ===
"""IMPORTANT: while these methods are helpful, they have also been completely wrapped by Device_History and Chip_History, and so these 
versions are intended to be private."""

def makeDevicePlot(plotType, deviceHistory, identifiers, mode_parameters=None):
	"""Given a plotType that matches one of the plotDefinitions in the plotDefinitions folder, as well as an array of data for a device, 
	and a dictionary containing the user/project/wafer/chip/device identifiers for this data, generate the requested plot. The plot can
	be shown by a later call to show().

	mode_parameters is an optional dictionary of plotting parameters that affect the style of many of the plots. mode_parameters should
	be a dictionary that includes some of the keys shown above in default_mode_parameters, and the union of these two dictionaries will
	be passed to the plots."""
	
	# If no data is available, do not proceed
	if(len(deviceHistory) <= 0):
		print('No ' + str(plotType) + ' device history to plot.')
		return
	
	# Merge mode_parameters with defaults
	updated_mode_parameters = default_mode_parameters.copy()
	if(mode_parameters is not None):
		updated_mode_parameters.update(mode_parameters)
	
	print('Plotting ' + str(plotType) + ' plot.')
	try:
		fig, axes = plotDefinitions[plotType]['function'](deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	except:
		print('Error plotting "plotType": ' + str(plotType))
		raise
	print('Finished plotting ' + str(plotType) + ' plot.')
	
	# If axis labels are the standard 'xlabel', 'ylabel' go ahead and make sure those are on the plot
	if(('automaticAxisLabels' in plotDefinitions[plotType]['description']['plotDefaults']) and (plotDefinitions[plotType]['description']['plotDefaults']['automaticAxisLabels'])):
		mplu.axisLabels(axes[0], x_label=plotDefinitions[plotType]['description']['plotDefaults']['xlabel'], y_label=plotDefinitions[plotType]['description']['plotDefaults']['ylabel'])
	
	# Adjust figure y-limits if desired
	if('includeOriginOnYaxis' in plotDefinitions[plotType]['description']['plotDefaults']):
		mplu.includeOriginOnYaxis(axes[0], include=plotDefinitions[plotType]['description']['plotDefaults']['includeOriginOnYaxis'])
	
	# Add title label to figure
	if(not updated_mode_parameters['publication_mode']):
		axes[0].set_title(mplu.getTestLabel(deviceHistory, identifiers))
	
	# Override axis dimensions if desired
	if(updated_mode_parameters['xlim'] is not None):
		if(isinstance(updated_mode_parameters['xlim'], dict)):
			axes[0].set_xlim(**updated_mode_parameters['xlim'])
		else:
			axes[0].set_xlim(updated_mode_parameters['xlim'])
	if(updated_mode_parameters['ylim'] is not None):
		if(isinstance(updated_mode_parameters['ylim'], dict)):
			axes[0].set_ylim(**updated_mode_parameters['ylim'])
		else:
			axes[0].set_ylim(updated_mode_parameters['ylim'])
	if(updated_mode_parameters['xticks'] is not None):
		axes[0].set_xticks(updated_mode_parameters['xticks'])
	if(updated_mode_parameters['yticks'] is not None):
		axes[0].set_yticks(updated_mode_parameters['yticks'])
	
	# Save figure
	subplotWidthPad  = (0) if(not 'subplotWidthPad'  in plotDefinitions[plotType]['description']['plotDefaults']) else (plotDefinitions[plotType]['description']['plotDefaults']['subplotWidthPad'])
	subplotHeightPad = (0) if(not 'subplotHeightPad' in plotDefinitions[plotType]['description']['plotDefaults']) else (plotDefinitions[plotType]['description']['plotDefaults']['subplotHeightPad'])
	mplu.adjustAndSaveFigure(fig, plotType, updated_mode_parameters, subplotWidthPad=subplotWidthPad, subplotHeightPad=subplotHeightPad)
	
	return fig, axes

def makeChipPlot(plotType, identifiers, chipIndexes=None, firstRunChipHistory=None, recentRunChipHistory=None, specificRunChipHistory=None, groupedChipHistory=None, mode_parameters=None):
	"""Given a plotType that matches one of the plotDefinitions in the plotDefinitions folder, as well as a variety of chip data, 
	and a dictionary containing the user/project/wafer/chip identifiers for this data, generate the requested plot. The plot can
	be shown by a later call to show(). Given the complexity of different requirements for different plots, it is highly recommended
	that Chip_History.makePlot() is used instead.

	mode_parameters is an optional dictionary of plotting parameters that affect the style of many of the plots. mode_parameters should
	be a dictionary that includes some of the keys shown above in default_mode_parameters, and the union of these two dictionaries will
	be passed to the plots."""	
	
	# If no data is available, do not proceed
	if(plotType == 'ChipHistogram'):
		if((chipIndexes is None) or len(chipIndexes.keys()) <= 0):
			print('No chip histogram to plot.')
			return
	elif((recentRunChipHistory is None) or len(recentRunChipHistory) <= 0):
		print('No ' + str(plotType) + ' chip history to plot.')
		return
	
	# Merge mode_parameters with defaults
	updated_mode_parameters = default_mode_parameters.copy()
	if(mode_parameters is not None):
		updated_mode_parameters.update(mode_parameters)
	
	print('Plotting ' + str(plotType) + ' plot.')
	try:
		fig, axes = plotDefinitions[plotType]['function'](identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory, mode_parameters=updated_mode_parameters)
	except:
		print('Error plotting "plotType": ' + str(plotType))
		raise
		
	# If axis labels are the standard 'xlabel', 'ylabel' go ahead and make sure those are on the plot
	if(('automaticAxisLabels' in plotDefinitions[plotType]['description']['plotDefaults']) and (plotDefinitions[plotType]['description']['plotDefaults']['automaticAxisLabels'])):
		mplu.axisLabels(axes[0], x_label=plotDefinitions[plotType]['description']['plotDefaults']['xlabel'], y_label=plotDefinitions[plotType]['description']['plotDefaults']['ylabel'])
		
	# Adjust figure y-limits if desired
	if('includeOriginOnYaxis' in plotDefinitions[plotType]['description']['plotDefaults']):
		mplu.includeOriginOnYaxis(axes[0], include=plotDefinitions[plotType]['description']['plotDefaults']['includeOriginOnYaxis'])
		
	# Add title label to figure
	if(not updated_mode_parameters['publication_mode']):
		axes[0].set_title('Chip ' + str(identifiers['wafer']) + str(identifiers['chip']))		
	
	# Override axis dimensions if desired
	if(updated_mode_parameters['xlim'] is not None):
		if(isinstance(updated_mode_parameters['xlim'], dict)):
			axes[0].set_xlim(**updated_mode_parameters['xlim'])
		else:
			axes[0].set_xlim(updated_mode_parameters['xlim'])
	if(updated_mode_parameters['ylim'] is not None):
		if(isinstance(updated_mode_parameters['ylim'], dict)):
			axes[0].set_ylim(**updated_mode_parameters['ylim'])
		else:
			axes[0].set_ylim(updated_mode_parameters['ylim'])
	if(updated_mode_parameters['xticks'] is not None):
		axes[0].set_xticks(updated_mode_parameters['xticks'])
	if(updated_mode_parameters['yticks'] is not None):
		axes[0].set_yticks(updated_mode_parameters['yticks'])
	
	# Save figure
	subplotWidthPad  = (0) if(not 'subplotWidthPad'  in plotDefinitions[plotType]['description']['plotDefaults']) else (plotDefinitions[plotType]['description']['plotDefaults']['subplotWidthPad'])
	subplotHeightPad = (0) if(not 'subplotHeightPad' in plotDefinitions[plotType]['description']['plotDefaults']) else (plotDefinitions[plotType]['description']['plotDefaults']['subplotHeightPad'])
	mplu.adjustAndSaveFigure(fig, plotType, updated_mode_parameters, subplotWidthPad=subplotWidthPad, subplotHeightPad=subplotHeightPad)
	
	return fig, axes

def makeBlankPlot(figsize=None):
	return mplu.initFigure(1,1, figsizeDefault=figsize)
	
def saveExternalPlot(figure, fileName, mode_parameters=None):
	updated_mode_parameters = default_mode_parameters.copy()
	if(mode_parameters is not None):
		updated_mode_parameters.update(mode_parameters)
	
	mplu.adjustAndSaveFigure(figure, fileName, updated_mode_parameters)

def getDataFileDependencies(plotType):
	"""Returns a list of data files needed to make the given plotType."""
	try:
		return plotDefinitions[plotType]['description']['dataFileDependencies']
	except:
		raise NotImplementedError('Unrecognized "plotType": ' + str(plotType))
		
def getPlotTypesFromDependencies(availableDataFiles, plotCategory='device', maxPriority=float('inf')):
	"""Returns a list of plotTypes that can be made from the given data files. plotCategory can choose between device or chip plots."""
	
	# Obtain a list of possible plotTypes, filtering out those that are the wrong category
	plotTypes = list(plotDefinitions.keys())
	for plotType, definition in plotDefinitions.items():
		try:
			for dataFileDependency in definition['description']['dataFileDependencies']:
				if((dataFileDependency not in availableDataFiles) or (plotCategory != definition['description']['plotCategory'])):
					if(plotType in plotTypes):
						plotTypes.remove(plotType)
		except:
			print('Error checking plot dependencies or category. Ignoring plotType: ' + str(plotType))
			plotTypes.remove(plotType)
	
	# Obtain the corresponding list of plot priorities, filtering out those that exceed the maximum allowed priority
	default_plot_priority = 1000000
	plotPriorities = []
	for plotType, definition in plotDefinitions.items():
		if(plotType in plotTypes):
			priority = 0
			try:
				priority = float(plotDefinitions[plotType]['description']['priority'])
			except:
				priority = default_plot_priority
			
			if(priority <= maxPriority):
				plotPriorities.append(priority)
			else:
				plotTypes.remove(plotType)
	
	# Sort plots by their assigned priority
	if(len(plotTypes) > 0):
		plotPriorities, plotTypes = zip(*sorted(zip(plotPriorities, plotTypes)))
	
	return list(plotTypes)
				 
def show():
	"""Shows all plots that have been previously generated by makeDevicePlot() or makeChipPlot()"""
	mplu.show()


