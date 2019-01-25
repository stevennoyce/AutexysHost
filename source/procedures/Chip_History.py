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
	'minJSONIndex': 0,
	'maxJSONIndex': float('inf'),
	'minJSONExperimentNumber': 0,
	'maxJSONExperimentNumber': float('inf'),
	'minJSONRelativeIndex': 0,
	'maxJSONRelativeIndex': float('inf'),
	'loadOnlyMostRecentExperiments': True,
	'numberOfRecentExperiments': 1,
	'numberOfRecentIndexes': 1,
	'specificDeviceList': None,
	'showFigures': True,
	'specificPlotToCreate': '',
}



# === External Interface ===
def makePlots(userID, projectID, waferID, chipID, dataFolder=None, specificPlot='', minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf'), loadOnlyMostRecentExperiments=True, numberOfRecentExperiments=1, numberOfRecentIndexes=1, specificDeviceList=None, deviceCategoryLists=None, saveFolder=None, plotSaveName='', showFigures=True, saveFigures=False, plot_mode_parameters=None):
	parameters = {}	
	mode_parameters = {}
	if(plot_mode_parameters is not None):
		mode_parameters.update(plot_mode_parameters)

	# Data loading parameters
	parameters['Identifiers'] = {}
	parameters['Identifiers']['user'] = userID
	parameters['Identifiers']['project'] = projectID
	parameters['Identifiers']['wafer'] = waferID
	parameters['Identifiers']['chip'] = chipID
	if(dataFolder is not None):
		parameters['dataFolder'] = dataFolder
	parameters['minJSONIndex'] = minIndex
	parameters['maxJSONIndex'] = maxIndex
	parameters['minJSONExperimentNumber'] = minExperiment
	parameters['maxJSONExperimentNumber'] = maxExperiment
	parameters['minJSONRelativeIndex'] = minRelativeIndex
	parameters['maxJSONRelativeIndex'] = maxRelativeIndex
	parameters['loadOnlyMostRecentExperiments'] = loadOnlyMostRecentExperiments
	parameters['numberOfRecentExperiments'] = numberOfRecentExperiments
	parameters['numberOfRecentIndexes'] = numberOfRecentIndexes
	parameters['specificDeviceList'] = specificDeviceList
	parameters['deviceGroupList'] = deviceCategoryLists
		
	# Plot selection parameters	
	parameters['showFigures'] = showFigures
	parameters['specificPlotToCreate'] = specificPlot
	
	# Plot decoration parameters
	if(saveFolder is not None):
		mode_parameters['plotSaveFolder'] = saveFolder
	mode_parameters['plotSaveName'] = plotSaveName
	mode_parameters['saveFigures'] = saveFigures
	mode_parameters['showFigures'] = showFigures

	return run(parameters, mode_parameters)



def run(additional_parameters, plot_mode_parameters={}):
	"""Legacy 'run' function from when ChipHistory was treated more like a typical procedure with parameters."""
	
	parameters = default_ch_parameters.copy()
	parameters.update(additional_parameters)

	plotList = []

	# Determine which plots are being requested and make them all
	plotsToCreate = [parameters['specificPlotToCreate']] if(parameters['specificPlotToCreate'] != '') else plotsForExperiments(parameters, minExperiment=0, maxExperiment=float('inf'))

	for plotType in plotsToCreate:
		dataFileDependencies = dpu.getDataFileDependencies(plotType)		
		(chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory) = loadDataBasedOnPlotDependencies(dataFileDependencies, parameters, minIndex=parameters['minJSONIndex'], maxIndex=parameters['maxJSONIndex'], minExperiment=parameters['minJSONExperimentNumber'], maxExperiment=parameters['maxJSONExperimentNumber'], minRelativeIndex=parameters['minJSONRelativeIndex'], maxRelativeIndex=parameters['maxJSONRelativeIndex'], loadOnlyMostRecentExperiments=parameters['loadOnlyMostRecentExperiments'], numberOfOldestExperiments=1, numberOfOldestIndexes=1, numberOfRecentExperiments=parameters['numberOfRecentExperiments'], numberOfRecentIndexes=parameters['numberOfRecentIndexes'], specificDeviceList=parameters['specificDeviceList'], deviceGroupList=parameters['deviceGroupList'])
		plot = dpu.makeChipPlot(plotType, parameters['Identifiers'], chipIndexes=chipIndexes, firstRunChipHistory=firstRunChipHistory, recentRunChipHistory=recentRunChipHistory, specificRunChipHistory=specificRunChipHistory, groupedChipHistory=groupedChipHistory, mode_parameters=plot_mode_parameters)
		plotList.append(plot)
	
	# Show figures if desired	
	if(parameters['showFigures']):
		dpu.show()

	return plotList



def loadDataBasedOnPlotDependencies(dataFileDependencies, parameters, minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf'), loadOnlyMostRecentExperiments=True, numberOfOldestExperiments=1, numberOfOldestIndexes=1, numberOfRecentExperiments=1, numberOfRecentIndexes=1, specificDeviceList=None, deviceGroupList=None):
	chipIndexes = None
	firstRunChipHistory = None
	recentRunChipHistory = None
	specificRunChipHistory = None
	groupedChipHistory = None
	if('index.json' in dataFileDependencies):
		chipIndexes = dlu.loadChipIndexes(dlu.getChipDirectory(parameters))
	if('GateSweep.json' in dataFileDependencies):
		firstRunChipHistory = dlu.loadOldestChipHistory(dlu.getChipDirectory(parameters), 'GateSweep.json', numberOfOldestExperiments=numberOfOldestExperiments, numberOfOldestIndexes=numberOfOldestIndexes, specificDeviceList=specificDeviceList)
		recentRunChipHistory = dlu.loadMostRecentChipHistory(dlu.getChipDirectory(parameters), 'GateSweep.json', numberOfRecentExperiments=numberOfRecentExperiments, numberOfRecentIndexes=numberOfRecentIndexes, specificDeviceList=specificDeviceList)
		if(loadOnlyMostRecentExperiments):
			specificRunChipHistory = recentRunChipHistory.copy()
		else:
			specificRunChipHistory = dlu.loadSpecificChipHistory(dlu.getChipDirectory(parameters), 'GateSweep.json', specificDeviceList=specificDeviceList, minIndex=minIndex, maxIndex=maxIndex, minExperiment=minExperiment, maxExperiment=maxExperiment, minRelativeIndex=minRelativeIndex, maxRelativeIndex=maxRelativeIndex)
			if(deviceGroupList is not None):
				groupedChipHistory = []
				for deviceGroup in deviceGroupList:
					chipHistoryForDeviceGroup = dlu.loadSpecificChipHistory(dlu.getChipDirectory(parameters), 'GateSweep.json', specificDeviceList=deviceGroup, minIndex=minIndex, maxIndex=maxIndex, minExperiment=minExperiment, maxExperiment=maxExperiment, minRelativeIndex=minRelativeIndex, maxRelativeIndex=maxRelativeIndex)
					groupedChipHistory.append(chipHistoryForDeviceGroup)
	return (chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory)



def plotsForExperiments(dataFolder, user, project, wafer, chip, minExperiment=0, maxExperiment=float('inf')):
	"""Given the typical parameters used to run experiments, return a list of plots that could be made from the data that has been already collected."""
	parameters = {'dataFolder':dataFolder, 'Identifiers':{'user':user, 'project':project, 'wafer':wafer, 'chip':chip}}
	return dpu.getPlotTypesFromDependencies(dlu.getDataFileNamesForChipExperiments(dlu.getChipDirectory(parameters), minExperiment=minExperiment, maxExperiment=maxExperiment), plotCategory='chip')




if(__name__ == '__main__'):
	pass
	#parameters = {'Identifiers':{'user':'stevenjay','project':'RedBoard','wafer':'Resistor','chip':'MegaOhm'}, 'dataFolder':'../../AutexysData'}
	#print(dlu.getDataFileNamesForChipExperiments(dlu.getChipDirectory(parameters), minExperiment=0, maxExperiment=float('inf')))
	#print(plotsForExperiments(parameters, minExperiment=0, maxExperiment=float('inf')))
	makePlots('jay', 'MoS2FET', 'JM4', 'C', specificPlot='ChipTransferCurve', specificDeviceList={'24-25'})#specificDeviceList={'3-6', '5-6', '4-5', '27-30', '28-29', '24-25', '34-35', '20-31', '31-32', '19-32'})


