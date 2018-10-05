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
def makeDevicePlot(plotType, deviceHistory, identifiers, mode_parameters=None):
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

def makeChipPlot(plotType, identifiers, chipIndexes=None, firstRunChipHistory=None, recentRunChipHistory=None, mode_parameters=None):	
	if(plotType is 'ChipHistogram'):
		if((chipIndexes is None) or len(chipIndexes) <= 0):
			print('No chip histogram to plot.')
			return
	elif((recentRunChipHistory is None) or len(recentRunChipHistory) <= 0):
		print('No ' + str(plotType) + ' chip history to plot.')
		return
	
	updated_mode_parameters = default_mode_parameters.copy()
	if(mode_parameters is not None):
		updated_mode_parameters.update(mode_parameters)

	try:
		fig, axes = plotDefinitions[plotType]['function'](identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, mode_parameters=updated_mode_parameters)
	except:
		raise NotImplementedError('Unrecognized "plotType": ' + str(plotType))

	return fig, axes

def getDataFileDependencies(plotType):
	try:
		return plotDefinitions[plotType]['description']['dataFileNames']
	except:
		raise NotImplementedError('Unrecognized "plotType": ' + str(plotType))

def show():
	mplu.show()


