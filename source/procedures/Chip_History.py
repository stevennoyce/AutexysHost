"""This module provides an interface for generating plots for a particular chip. The primary method is ChipHistory.makePlots()."""

# === Make this script runnable ===
if(__name__ == '__main__'):
	import sys
	sys.path.append(sys.path[0] + '/..')
	
	import os
	pathParents = os.getcwd().split('/')
	if 'AutexysHost' in pathParents:
		os.chdir(os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source'))

# === Imports ===
from utilities import DataPlotterUtility as dpu
from utilities import DataLoggerUtility as dlu



# === Defaults ===
default_ch_parameters = {
	'dataFolder': '../../AutexysData/',
	'showFiguresGenerated': True,
	'saveFiguresGenerated': True,
	'specificPlotToCreate': ''
}



# === External Interface ===
def makePlots(userID, projectID, waferID, chipID, dataFolder=None, specificPlot='', saveFolder=None, plotSaveName='', showFigures=True, saveFigures=False, plot_mode_parameters=None):
	parameters = {}	
	mode_parameters = {}
	if(plot_mode_parameters is not None):
		mode_parameters.update(plot_mode_parameters)

	parameters['Identifiers'] = {}
	parameters['Identifiers']['user'] = userID
	parameters['Identifiers']['project'] = projectID
	parameters['Identifiers']['wafer'] = waferID
	parameters['Identifiers']['chip'] = chipID

	if(dataFolder is not None):
		parameters['dataFolder'] = dataFolder
	parameters['showFiguresGenerated'] = showFigures
	parameters['saveFiguresGenerated'] = saveFigures
	parameters['specificPlotToCreate'] = specificPlot
	
	if(saveFolder is not None):
		mode_parameters['plotSaveFolder'] = saveFolder

	return run(parameters, mode_parameters)



def run(additional_parameters, plot_mode_parameters={}):
	"""Legacy 'run' function from when ChipHistory was treated more like a typical procedure with parameters."""
	
	parameters = default_ch_parameters.copy()
	parameters.update(additional_parameters)

	plot_mode_parameters['showFigures'] = parameters['showFiguresGenerated']
	plot_mode_parameters['saveFigures'] = parameters['saveFiguresGenerated']

	plotList = []

	# Determine which plots are being requested and make them all
	plotsToCreate = [p['specificPlotToCreate']] if(p['specificPlotToCreate'] != '') else plotsForExperiments(parameters, minExperiment=p['excludeDataBeforeJSONExperimentNumber'], maxExperiment=p['excludeDataAfterJSONExperimentNumber'])

	for plotType in plotsToCreate:
		if(plotType == 'ChipHistogram'):
			chipIndexes = dlu.loadChipIndexes(dlu.getChipDirectory(parameters))
			firstRunChipHistory = None
			recentRunChipHistory = None
		elif(plotType == 'ChipOnOffRatios'):
			chipIndexes = None
			firstRunChipHistory = dlu.loadFirstRunChipHistory(dlu.getChipDirectory(parameters), 'GateSweep.json')
			recentRunChipHistory = dlu.loadMostRecentChipHistory(dlu.getChipDirectory(parameters), 'GateSweep.json', numberOfRecentExperiments=1)
		elif(plotType == 'ChipOnOffCurrents'):
			chipIndexes = None
			firstRunChipHistory = None
			recentRunChipHistory = dlu.loadMostRecentChipHistory(dlu.getChipDirectory(parameters), 'GateSweep.json', numberOfRecentExperiments=1)
		elif(plotType == 'ChipTransferCurves'):
			chipIndexes = None
			firstRunChipHistory = None
			recentRunChipHistory = dlu.loadMostRecentChipHistory(dlu.getChipDirectory(parameters), 'GateSweep.json', numberOfRecentExperiments=1)
						
		plot = dpu.makeChipPlot(plotType, parameters['Identifiers'], chipIndexes=chipIndexes, firstRunChipHistory=firstRunChipHistory, recentRunChipHistory=recentRunChipHistory, mode_parameters=plot_mode_parameters)
		plotList.append(plot)
	
	# Show figures if desired	
	if(parameters['showFiguresGenerated']):
		dpu.show()

	return plotList



def plotsForExperiments(parameters, minExperiment=0, maxExperiment=float('inf')):
	"""Given the typical parameters used to run experiments, return a list of plots that could be made from the data that has been already collected."""
	
	return dpu.getPlotTypesFromDependencies(dlu.getDataFileNamesForExperiments(dlu.getDeviceDirectory(parameters), minExperiment=minExperiment, maxExperiment=maxExperiment), plotCategory='chip')




if(__name__ == '__main__'):
	makePlots('stevenjay', 'RedBoard', 'C127', 'D')


