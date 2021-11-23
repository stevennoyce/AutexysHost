"""This module provides an interface for generating plots for a particular chip. The primary method is ChipHistory.makePlots()."""

# === Imports ===
import numpy as np
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
	'minOnCurrent': None,
	'maxOnCurrent': None,
	'maxOffCurrent': None,
	'maxGateCurrent': None,
	'showFigures': True,
	'specificPlotToCreate': '',
}



# === External Interface ===
def makePlots(userID, projectID, waferID, chipID, specificPlot='', 
				minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf'), 
				loadOnlyMostRecentExperiments=True, numberOfRecentExperiments=1, numberOfRecentIndexes=1, specificDeviceList=None, 
				minOnCurrent=None, maxOnCurrent=None, maxOffCurrent=None, maxGateCurrent=None, deviceCategoryLists=None, 
				dataFolder=None, saveFolder=None, plotSaveName='', saveFigures=False, showFigures=True, plot_mode_parameters=None):

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
	parameters['minOnCurrent'] = minOnCurrent
	parameters['maxOnCurrent'] = maxOnCurrent
	parameters['maxOffCurrent'] = maxOffCurrent
	parameters['maxGateCurrent'] = maxGateCurrent
	parameters['deviceGroupList'] = deviceCategoryLists
		
	# Plot selection parameters	
	parameters['showFigures'] = showFigures
	parameters['specificPlotToCreate'] = specificPlot
	
	# Plot saving parameters
	if(saveFolder is not None):
		mode_parameters['plotSaveFolder'] = saveFolder
	mode_parameters['saveFigures'] = saveFigures
	mode_parameters['showFigures'] = showFigures
	mode_parameters['plotSaveName'] = plotSaveName

	return run(parameters, mode_parameters)



def run(additional_parameters, plot_mode_parameters=None):
	"""Legacy 'run' function from when ChipHistory was treated more like a typical procedure with parameters."""
	
	# Combine additional_parameters with the defaults
	parameters = default_ch_parameters.copy()
	parameters.update(additional_parameters)

	# Combine plot_mode_parameters with the empty default dictionary
	mode_parameters = {}
	if(plot_mode_parameters != None):
		mode_parameters.update(plot_mode_parameters)

	# Define return variable
	plotList = []

	# If desired, look at the on-current from a gate sweep for each device before deciding to include it based on a cutoff value
	devicesToInclude = parameters['specificDeviceList']
	if((parameters['minOnCurrent'] is not None) or (parameters['maxOnCurrent'] is not None) or (parameters['maxOffCurrent'] is not None) or(parameters['maxGateCurrent'] is not None)):
		(chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory) = loadDataBasedOnPlotDependencies(['GateSweep.json'], parameters, minIndex=parameters['minJSONIndex'], maxIndex=parameters['maxJSONIndex'], minExperiment=parameters['minJSONExperimentNumber'], maxExperiment=parameters['maxJSONExperimentNumber'], minRelativeIndex=parameters['minJSONRelativeIndex'], maxRelativeIndex=parameters['maxJSONRelativeIndex'], loadOnlyMostRecentExperiments=parameters['loadOnlyMostRecentExperiments'], numberOfOldestExperiments=1, numberOfOldestIndexes=1, numberOfRecentExperiments=parameters['numberOfRecentExperiments'], numberOfRecentIndexes=parameters['numberOfRecentIndexes'], specificDeviceList=devicesToInclude, deviceGroupList=parameters['deviceGroupList'])
		devicesToInclude = []
		for deviceRun in specificRunChipHistory:
			abs_max_drain_current = max(np.max(deviceRun['Results']['id_data']), abs(np.min(deviceRun['Results']['id_data'])))
			abs_min_drain_current = min(abs(np.min(deviceRun['Results']['id_data'])), abs(np.max(deviceRun['Results']['id_data'])))
			abs_max_gate_current  = max(np.max(deviceRun['Results']['ig_data']), abs(np.min(deviceRun['Results']['ig_data'])))
			if( ((parameters['minOnCurrent'] is None) or (abs_max_drain_current > parameters['minOnCurrent'])) and ((parameters['maxOnCurrent'] is None) or (abs_max_drain_current < parameters['maxOnCurrent'])) and ((parameters['maxOffCurrent'] is None) or (abs_min_drain_current < parameters['maxOffCurrent'])) and ((parameters['maxGateCurrent'] is None) or (abs_max_gate_current < parameters['maxGateCurrent'])) ):
				devicesToInclude.append(deviceRun['Identifiers']['device'])

	# Determine which plots are being requested and make them all
	plotsToCreate = [parameters['specificPlotToCreate']] if(parameters['specificPlotToCreate'] != '') else [entry['type'] for entry in plotsForExperiments(parameters, minExperiment=0, maxExperiment=float('inf'))]
	for plotType in plotsToCreate:
		dataFileDependencies = dpu.getDataFileDependencies(plotType)		
		(chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory) = loadDataBasedOnPlotDependencies(dataFileDependencies, parameters, minIndex=parameters['minJSONIndex'], maxIndex=parameters['maxJSONIndex'], minExperiment=parameters['minJSONExperimentNumber'], maxExperiment=parameters['maxJSONExperimentNumber'], minRelativeIndex=parameters['minJSONRelativeIndex'], maxRelativeIndex=parameters['maxJSONRelativeIndex'], loadOnlyMostRecentExperiments=parameters['loadOnlyMostRecentExperiments'], numberOfOldestExperiments=1, numberOfOldestIndexes=1, numberOfRecentExperiments=parameters['numberOfRecentExperiments'], numberOfRecentIndexes=parameters['numberOfRecentIndexes'], specificDeviceList=devicesToInclude, deviceGroupList=parameters['deviceGroupList'])
		plot = dpu.makeChipPlot(plotType, parameters['Identifiers'], chipIndexes=chipIndexes, firstRunChipHistory=firstRunChipHistory, recentRunChipHistory=recentRunChipHistory, specificRunChipHistory=specificRunChipHistory, groupedChipHistory=groupedChipHistory, mode_parameters=mode_parameters)
		plotList.append(plot)
	
	# Show figures if desired	
	if(parameters['showFigures']):
		dpu.show()

	return plotList



def loadDataBasedOnPlotDependencies(dataFileDependencies, parameters, minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf'), loadOnlyMostRecentExperiments=True, numberOfOldestExperiments=1, numberOfOldestIndexes=1, numberOfRecentExperiments=1, numberOfRecentIndexes=1, specificDeviceList=None, deviceGroupList=None):
	# Define data arrays to return
	chipIndexes = None
	firstRunChipHistory = None
	recentRunChipHistory = None
	specificRunChipHistory = None
	groupedChipHistory = None
	
	# For each fileName in dataFileDependencies, load data
	for dependency in dataFileDependencies:
		if(dependency == 'index.json'):
			chipIndexes = dlu.loadChipIndexes(dlu.getChipDirectory(parameters))
		elif(dependency in ['GateSweep.json', 'DrainSweep.json']):
			firstRunChipHistory = dlu.loadOldestChipHistory(dlu.getChipDirectory(parameters), dependency, numberOfOldestExperiments=numberOfOldestExperiments, numberOfOldestIndexes=numberOfOldestIndexes, specificDeviceList=specificDeviceList)
			recentRunChipHistory = dlu.loadMostRecentChipHistory(dlu.getChipDirectory(parameters), dependency, numberOfRecentExperiments=numberOfRecentExperiments, numberOfRecentIndexes=numberOfRecentIndexes, specificDeviceList=specificDeviceList)
			if(loadOnlyMostRecentExperiments):
				specificRunChipHistory = recentRunChipHistory.copy()
			else:
				specificRunChipHistory = dlu.loadSpecificChipHistory(dlu.getChipDirectory(parameters), dependency, specificDeviceList=specificDeviceList, minIndex=minIndex, maxIndex=maxIndex, minExperiment=minExperiment, maxExperiment=maxExperiment, minRelativeIndex=minRelativeIndex, maxRelativeIndex=maxRelativeIndex)
				if(deviceGroupList is not None):
					groupedChipHistory = []
					for deviceGroup in deviceGroupList:
						chipHistoryForDeviceGroup = dlu.loadSpecificChipHistory(dlu.getChipDirectory(parameters), dependency, specificDeviceList=deviceGroup, minIndex=minIndex, maxIndex=maxIndex, minExperiment=minExperiment, maxExperiment=maxExperiment, minRelativeIndex=minRelativeIndex, maxRelativeIndex=maxRelativeIndex)
						groupedChipHistory.append(chipHistoryForDeviceGroup)
						
	return (chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory)



def plotsForExperiments(parameters, minExperiment=0, maxExperiment=float('inf'), maxPriority=float('inf')):
	"""Given the typical parameters used to run experiments, return a list of plots that could be made from the data that has been already collected."""
	try:
		return dpu.getPlotTypesFromDependencies(dlu.getDataFileNamesForChipExperiments(dlu.getChipDirectory(parameters), minExperiment=minExperiment, maxExperiment=maxExperiment), plotCategory='chip', maxPriority=maxPriority)
	except FileNotFoundError:
		print('No chip plots available for the requested experiments.')
		return []



if(__name__ == '__main__'):
	pass
	#makePlots('jay', 'MoS2FET', 'JM4', 'D', specificPlot='ChipTransferCurve', specificDeviceList={'3-6', '3-4', '1-2', '28-29', '24-25', '7-11', '43-44'}, sweepDirection='forward')
	

