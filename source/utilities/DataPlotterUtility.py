from utilities import MatplotlibUtility as mplu

import pkgutil
import os

# Import all Plot Definitions and save a reference to run their 'plot' function
plotDefinitions = {}
for importer, packageName, isPackage in pkgutil.iter_modules([os.path.join(os.path.dirname(os.path.realpath(__file__)), 'PlotDefinitions')]):
	module = importer.find_module(packageName).load_module(packageName)
	plotDefinitions[packageName] = {}
	plotDefinitions[packageName]['module'] = module
	plotDefinitions[packageName]['description'] = module.plotDescription
	plotDefinitions[packageName]['function'] = module.plot



# === Plot Parameters ===
default_mode_parameters = {
	'showFigures': True,
	'saveFigures': True,
	'plotSaveFolder': '../../AutexysPlots/',
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
	if(len(deviceHistory) <= 0):
		print('No ' + str(plotType) + ' device history to plot.')
		return
	
	updated_mode_parameters = default_mode_parameters.copy()
	if(mode_parameters is not None):
		updated_mode_parameters.update(mode_parameters)
	
	try:
		fig, axes = plotDefinitions[plotType]['function'](deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	except:
		raise NotImplementedError('Unrecognized "plotType": ' + str(plotType))
	
	return fig, axes

def makeChipPlot(plotType, identifiers, chipIndexes=None, firstRunChipHistory=None, recentRunChipHistory=None, specificRunChipHistory=None, mode_parameters=None):
	"""Given a plotType that matches one of the plotDefinitions in the plotDefinitions folder, as well as a variety of chip data, 
	and a dictionary containing the user/project/wafer/chip identifiers for this data, generate the requested plot. The plot can
	be shown by a later call to show(). Given the complexity of different requirements for different plots, it is highly recommended
	that Chip_History.makePlot() is used instead.

	mode_parameters is an optional dictionary of plotting parameters that affect the style of many of the plots. mode_parameters should
	be a dictionary that includes some of the keys shown above in default_mode_parameters, and the union of these two dictionaries will
	be passed to the plots."""	
	
	if(plotType == 'ChipHistogram'):
		if((chipIndexes is None) or len(chipIndexes.keys()) <= 0):
			print('No chip histogram to plot.')
			return
	elif((recentRunChipHistory is None) or len(recentRunChipHistory) <= 0):
		print('No ' + str(plotType) + ' chip history to plot.')
		return
	
	updated_mode_parameters = default_mode_parameters.copy()
	if(mode_parameters is not None):
		updated_mode_parameters.update(mode_parameters)
	
	try:
		fig, axes = plotDefinitions[plotType]['function'](identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, mode_parameters=updated_mode_parameters)
	except:
		print('Error plotting "plotType": ' + str(plotType))
		raise
		
	return fig, axes

def getDataFileDependencies(plotType):
	"""Returns a list of data files needed to make the given plotType."""
	try:
		return plotDefinitions[plotType]['description']['dataFileDependencies']
	except:
		raise NotImplementedError('Unrecognized "plotType": ' + str(plotType))
		
def getPlotTypesFromDependencies(availableDataFiles, plotCategory='device'):
	"""Returns a list of plotTypes that can be made from the given data files. plotCategory can choose between device or chip plots."""
	plotTypes = list(plotDefinitions.keys())
	for plotType, definition in plotDefinitions.items():
		for dataFileDependency in definition['description']['dataFileDependencies']:
			if((dataFileDependency not in availableDataFiles) or (plotCategory != definition['description']['plotCategory'])):
				if(plotType in plotTypes):
					plotTypes.remove(plotType)
	plotTypes.sort(reverse=True)
	return plotTypes
				 
def show():
	"""Shows all plots that have been previously generated by makeDevicePlot() or makeChipPlot()"""
	mplu.show()


