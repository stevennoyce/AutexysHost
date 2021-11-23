"""This module provides a complete interface for generating plots for a particular device. The primary method is DeviceHistory.makePlots()."""

# === Imports ===
from utilities import DataPlotterUtility as dpu
from utilities import DataLoggerUtility as dlu

import time

# === Defaults ===
default_dh_parameters = {
	'dataFolder': '../../AutexysData/',
	'minJSONIndex': 0,
	'maxJSONIndex':  float('inf'),
	'minJSONExperimentNumber': 0,
	'maxJSONExperimentNumber':  float('inf'),
	'minJSONRelativeIndex': 0,
	'maxJSONRelativeIndex':  float('inf'),
	'loadOnlyMostRecentExperiments': False,
	'numberOfRecentExperiments': 1,
	'numberOfRecentIndexes': float('inf'),
	'showFigures': True,
	'specificPlotToCreate': ''
}

default_linking_file = 'DeviceCycling.json'



# === Deprecated External Interface ===
#def makePlots(userID, projectID, waferID, chipID, deviceID, minExperiment=0, maxExperiment=float('inf'), specificPlot='', figureSize=None, sweepDirection=None, dataFolder=None, saveFolder=None, plotSaveName='', saveFigures=False, showFigures=True, loadOnlyMostRecentExperiments=False, numberOfRecentExperiments=1, numberOfRecentIndexes=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf'), plot_mode_parameters=None, cacheBust=None):

# === External Interface ===
def makePlots(userID, projectID, waferID, chipID, deviceID, specificPlot='', 
				minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf'),
				loadOnlyMostRecentExperiments=False, numberOfRecentExperiments=1, numberOfRecentIndexes=float('inf'),
				dataFolder=None, saveFolder=None, plotSaveName='', saveFigures=False, showFigures=True, plot_mode_parameters=None, cacheBust=None):
	"""Make plots for the device found in the userID/projectID/waferID/chipID/deviceID folder.

	specificPlot can be specified to only make one specific plot found in the plotDefintions folder, or by default all available plots are made.
	minExperiment and maxExperiment specify a range of experiments to include in the plot(s).
	minRelativeIndex and maxRelativeIndex can be used to limit the number of data entries shown if all entries have the same experimentNumber
	dataFolder and saveFolder can specify the paths for loading .json data and saving .png plots, but they should not be necessary by default.
	plotSaveName can add extra characters to the .png saved by this function if that is desireable.
	saveFigures and showFigures are booleans that specify if a plot should be shown with the matplotlib pyplot interface or saved as a .png
	
	plot_mode_parameters is a catch-all dictionary for parameters that affect the style of plots (but not the data shown!). See the DataPlotterUtility
	for more information about available plot_mode_parameters."""

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
	parameters['Identifiers']['device'] = deviceID
	if(dataFolder is not None):
		parameters['dataFolder'] = dataFolder
	parameters['minJSONExperimentNumber'] = minExperiment
	parameters['maxJSONExperimentNumber'] = maxExperiment
	parameters['minJSONRelativeIndex'] = minRelativeIndex
	parameters['maxJSONRelativeIndex'] = maxRelativeIndex
	parameters['loadOnlyMostRecentExperiments'] = loadOnlyMostRecentExperiments
	parameters['numberOfRecentExperiments'] = numberOfRecentExperiments
	parameters['numberOfRecentIndexes'] = numberOfRecentIndexes

	# Plot selection parameters
	parameters['showFigures'] = showFigures
	parameters['specificPlotToCreate'] = specificPlot

	# Plot saving parameters
	if(saveFolder is not None):
		mode_parameters['plotSaveFolder'] = saveFolder
	mode_parameters['saveFigures'] = saveFigures
	mode_parameters['showFigures'] = showFigures
	mode_parameters['plotSaveName'] = plotSaveName

	return run(parameters, plot_mode_parameters=mode_parameters, cacheBust=cacheBust)



# === Main ===
def run(additional_parameters, plot_mode_parameters=None, cacheBust=None):
	"""Legacy 'run' function from when DeviceHistory was treated more like a typical procedure with parameters."""

	# Combine additional_parameters with the defaults
	parameters = default_dh_parameters.copy()
	parameters.update(additional_parameters)

	# Combine plot_mode_parameters with the empty default dictionary
	mode_parameters = {}
	if(plot_mode_parameters != None):
		mode_parameters.update(plot_mode_parameters)
	
	# Define return variable
	plotList = []
	
	# Define nickname
	p = parameters

	# Print information about the device and experiment being plotted
	print('[DH]: === ' + parameters['Identifiers']['wafer'] + parameters['Identifiers']['chip'] + ':' + parameters['Identifiers']['device'] + ' ===')
	'' if((p['minJSONExperimentNumber'] == 0) and (p['maxJSONExperimentNumber'] == float('inf'))) else (print('[DH]: Experiment #{:}'.format(p['maxJSONExperimentNumber'])) if(p['minJSONExperimentNumber'] == p['maxJSONExperimentNumber']) else (print('[DH]: Experiments #{:} to #{:}'.format(p['minJSONExperimentNumber'],p['maxJSONExperimentNumber']))))
	'' if((p['minJSONRelativeIndex'] == 0) and (p['maxJSONRelativeIndex'] == float('inf'))) else (print('[DH]: Rel. Index #{:}'.format(p['maxJSONRelativeIndex'])) if(p['minJSONRelativeIndex'] == p['maxJSONRelativeIndex']) else (print('[DH]: Rel. Indices #{:} to #{:}'.format(p['minJSONRelativeIndex'],p['maxJSONRelativeIndex']))))
	'' if((p['minJSONIndex'] == 0) and (p['maxJSONIndex'] == float('inf'))) else (print('[DH]: Abs. Index #{:}'.format(p['maxJSONIndex'])) if(p['minJSONIndex'] == p['maxJSONIndex']) else (print('[DH]: Abs. Indices #{:} to #{:}'.format(p['minJSONIndex'],p['maxJSONIndex']))))

	# Try to load general information file 'wafer.json' if such a file exists
	if('generalInfo' not in mode_parameters):
		try:
			wafer_info = dlu.loadJSON(dlu.getWaferDirectory(parameters), 'wafer.json')[0]
			mode_parameters['generalInfo'] = wafer_info
		except:
			pass

	# Determine which plots are being requested and make them all
	plotsToCreate = [p['specificPlotToCreate']] if(p['specificPlotToCreate'] != '') else [entry['type'] for entry in plotsForExperiments(parameters, minExperiment=p['minJSONExperimentNumber'], maxExperiment=p['maxJSONExperimentNumber'])]
	for plotType in plotsToCreate:
		print('[DH]: Loading data for ' + str(plotType) + ' plot.')
		
		# Get a list of relevant data files needed for this plot
		dataFileDependencies = dpu.getDataFileDependencies(plotType)
		
		try:
			# === Load the data ===
			deviceHistory = []
			for dataFile in dataFileDependencies:
				if(p['loadOnlyMostRecentExperiments']):
					deviceHistory += dlu.loadMostRecentDeviceHistory(dlu.getDeviceDirectory(parameters), dataFile, numberOfRecentExperiments=p['numberOfRecentExperiments'], numberOfRecentIndexes=p['numberOfRecentIndexes'])
				else:
					#deviceHistory += dlu.loadSpecificDeviceHistoryWithCaching((time.time() if(cacheBust is None) else cacheBust), dlu.getDeviceDirectory(parameters), dataFile, minIndex=p['minJSONIndex'], maxIndex=p['maxJSONIndex'], minExperiment=p['minJSONExperimentNumber'], maxExperiment=p['maxJSONExperimentNumber'], minRelativeIndex=p['minJSONRelativeIndex'], maxRelativeIndex=p['maxJSONRelativeIndex'])
					deviceHistory += dlu.loadSpecificDeviceHistory(dlu.getDeviceDirectory(parameters), dataFile, minIndex=p['minJSONIndex'], maxIndex=p['maxJSONIndex'], minExperiment=p['minJSONExperimentNumber'], maxExperiment=p['maxJSONExperimentNumber'], minRelativeIndex=p['minJSONRelativeIndex'], maxRelativeIndex=p['maxJSONRelativeIndex'])
			
			# If no data was loaded directly, check for possible linked data files
			if(len(deviceHistory) == 0):
				linkingHistory = dlu.loadSpecificDeviceHistory(dlu.getDeviceDirectory(parameters), default_linking_file, looseFiltering=True, minIndex=p['minJSONIndex'], maxIndex=p['maxJSONIndex'], minExperiment=p['minJSONExperimentNumber'], maxExperiment=p['maxJSONExperimentNumber'], minRelativeIndex=p['minJSONRelativeIndex'], maxRelativeIndex=p['maxJSONRelativeIndex'])
				for linkingData in linkingHistory:
					for dataFile in dataFileDependencies:
						deviceHistory += dlu.loadChipHistoryByIndex(dlu.getChipDirectory(parameters), dataFile, deviceIndexes=linkingData['DeviceCycling']['deviceIndexes'])
			
			# === Generate the plot ===
			plot = dpu.makeDevicePlot(plotType, deviceHistory, parameters['Identifiers'], mode_parameters=mode_parameters)
			
			# Add generated plot to the results list
			plotList.append(plot)
		except FileNotFoundError as e:
			print("[DH]: Error, unable to load data files for '" + str(plotType) + "' plot.")
			print(e)
			import traceback
			traceback.print_exc()

	# Show figures if desired
	if(p['showFigures']):
		dpu.show()

	return plotList



def plotsForExperiments(parameters, minExperiment=0, maxExperiment=float('inf'), maxPriority=float('inf'), linkingFile=default_linking_file):
	"""Given the typical parameters used to run experiments, return a list of plots that could be made from the data that has been already collected."""
	try:
		# Get a list of all saved data files for the given experiment range
		available_data_files = dataFilesForExperiments(parameters, minExperiment=minExperiment, maxExperiment=maxExperiment)
		
		# Add linked data files to the list of available saved data files
		if((linkingFile is not None) and (linkingFile in available_data_files)):
			available_data_files += dlu.getLinkedFileNamesForDeviceExperiments(dlu.getDeviceDirectory(parameters), linkingFile, minExperiment=minExperiment, maxExperiment=maxExperiment)

		# Return list of available plots based on the available data files
		return dpu.getPlotTypesFromDependencies(available_data_files, plotCategory='device', maxPriority=maxPriority)
	except FileNotFoundError:
		print('[DH]: No device plots available for the requested experiments.')
		return []

def dataFilesForExperiments(parameters, minExperiment=0, maxExperiment=float('inf')):
	"""Given the typical parameters used to run experiments, return a list files containing the saved data that has been collected."""

	return dlu.getDataFileNamesForDeviceExperiments(dlu.getDeviceDirectory(parameters), minExperiment=minExperiment, maxExperiment=maxExperiment)



if __name__ == '__main__':
	pass
	#makePlots('matthew', 'breadboard_FET', '1', '1', '1', 1, 1, 'SignalToNoiseRatio', None, dataFolder='C:\\Users\\Matthew\\Documents\\SeniorSpring\\FranklinLab\\software\\AutexysData', showFigures=True)
