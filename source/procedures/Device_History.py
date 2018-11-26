"""This module provides a complete interface for generating plots for a particular device. The primary method is DeviceHistory.makePlots()."""

# === Make this script runnable ===
if(__name__ == '__main__'):
	import sys
	sys.path.append(sys.path[0] + '/..')
	
	import os
	pathParents = os.getcwd().split('/')
	if('AutexysHost' in pathParents):
		os.chdir(os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source'))

# === Imports ===
from utilities import DataPlotterUtility as dpu
from utilities import DataLoggerUtility as dlu
from utilities import PlotPostingUtility as plotPoster



# === Defaults ===
default_dh_parameters = {
	'dataFolder': '../../AutexysData/',
	'minJSONIndex': 0,
	'maxJSONIndex':  float('inf'),
	'minJSONExperimentNumber': 0,
	'maxJSONExperimentNumber':  float('inf'),
	'minJSONRelativeIndex': 0,
	'maxJSONRelativeIndex':  float('inf'),
	'showFigures': True,
	'specificPlotToCreate': ''
}



# === External Interface ===
def makePlots(userID, projectID, waferID, chipID, deviceID, startExperimentNumber=0, endExperimentNumber=float('inf'), specificPlot='', figureSize=None, dataFolder=None, saveFolder=None, plotSaveName='', saveFigures=False, showFigures=True, sweepDirection='both', startRelativeIndex=0, endRelativeIndex=float('inf'), plot_mode_parameters=None):
	"""Make plots for the device found in the userID/projectID/waferID/chipID/deviceID folder.
	
	startExperimentNumber and endExperimentNumber specify a range of experiments to include in the plot(s).
	specificPlot can be specified to only make one specific plot found in the plotDefintions folder, or by default all available plots are made.
	figureSize can be specified as (width,height) to set the size of the plot.
	dataFolder and saveFolder can specify the paths for loading .json data and saving .png plots, but they should not be necessary by default.
	plotSaveName can add extra characters to the .png saved by this function if that is desireable.
	saveFigures and showFigures are booleans that specify if a plot should be shown with the matplotlib pyplot interface or saved as a .png
	sweepDirection is a commonly used plot decorator (can be 'both', 'forward', or 'reverse').
	startRelativeIndex and endRelativeIndex can be used to limit the number of data entries shown if all entries have the same experimentNumber
	
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
	parameters['minJSONExperimentNumber'] = startExperimentNumber
	parameters['maxJSONExperimentNumber'] = endExperimentNumber
	parameters['minJSONRelativeIndex'] = startRelativeIndex
	parameters['maxJSONRelativeIndex'] = endRelativeIndex
	
	# Plot selection parameters
	parameters['showFigures'] = showFigures
	parameters['specificPlotToCreate'] = specificPlot
	
	# Plot decoration parameters
	if(saveFolder is not None):
		mode_parameters['plotSaveFolder'] = saveFolder
	mode_parameters['saveFigures'] = saveFigures
	mode_parameters['showFigures'] = showFigures
	mode_parameters['plotSaveName'] = plotSaveName
	mode_parameters['figureSizeOverride'] = figureSize
	mode_parameters['sweepDirection'] = sweepDirection
	
	return run(parameters, plot_mode_parameters=mode_parameters)



# === Main ===
def run(additional_parameters, plot_mode_parameters=None):
	"""Legacy 'run' function from when DeviceHistory was treated more like a typical procedure with parameters."""
	
	parameters = default_dh_parameters.copy()
	parameters.update(additional_parameters)

	p = parameters
	plotList = []

	mode_parameters = {}
	if(plot_mode_parameters != None):
		mode_parameters.update(plot_mode_parameters)

	# Print information about the device and experiment being plotted
	print('  ' + parameters['Identifiers']['wafer'] + parameters['Identifiers']['chip'] + ':' + parameters['Identifiers']['device'])
	'' if((p['minJSONExperimentNumber'] == 0) and (p['maxJSONExperimentNumber'] == float('inf'))) else (print('  Experiment #{:}'.format(p['maxJSONExperimentNumber'])) if(p['minJSONExperimentNumber'] == p['maxJSONExperimentNumber']) else (print('  Experiments #{:} to #{:}'.format(p['minJSONExperimentNumber'],p['maxJSONExperimentNumber'])))) 
	'' if((p['minJSONRelativeIndex'] == 0) and (p['maxJSONRelativeIndex'] == float('inf'))) else (print('  Rel. Index #{:}'.format(p['maxJSONRelativeIndex'])) if(p['minJSONRelativeIndex'] == p['maxJSONRelativeIndex']) else (print('  Rel. Indices #{:} to #{:}'.format(p['minJSONRelativeIndex'],p['maxJSONRelativeIndex']))))
	'' if((p['minJSONIndex'] == 0) and (p['maxJSONIndex'] == float('inf'))) else (print('  Abs. Index #{:}'.format(p['maxJSONIndex'])) if(p['minJSONIndex'] == p['maxJSONIndex']) else (print('  Abs. Indices #{:} to #{:}'.format(p['minJSONIndex'],p['maxJSONIndex']))))

	# Try to load general information file 'wafer.json' if such a file exists
	if('generalInfo' not in mode_parameters):
		try:
			wafer_info = dlu.loadJSON(dlu.getWaferDirectory(parameters), 'wafer.json')[0]
			mode_parameters['generalInfo'] = wafer_info
		except:
			print('Error: no information in wafer.json for this device.')
	
	# Determine which plots are being requested and make them all
	plotsToCreate = [p['specificPlotToCreate']] if(p['specificPlotToCreate'] != '') else plotsForExperiments(parameters, minExperiment=p['minJSONExperimentNumber'], maxExperiment=p['maxJSONExperimentNumber'])
	for plotType in plotsToCreate:
		print('Loading data for ' + str(plotType) + ' plot.')
		dataFileDependencies = dpu.getDataFileDependencies(plotType)
		deviceHistory = []
		try:
			for dataFile in dataFileDependencies:
				deviceHistory += dlu.loadSpecificDeviceHistory(dlu.getDeviceDirectory(parameters), dataFile, minIndex=p['minJSONIndex'], maxIndex=p['maxJSONIndex'], minExperiment=p['minJSONExperimentNumber'], maxExperiment=p['maxJSONExperimentNumber'], minRelativeIndex=p['minJSONRelativeIndex'], maxRelativeIndex=p['maxJSONRelativeIndex'])
			plot = dpu.makeDevicePlot(plotType, deviceHistory, parameters['Identifiers'], mode_parameters=mode_parameters)
			plotList.append(plot)
		except FileNotFoundError:
			print("Error: Unable to load data files for '" + str(plotType) + "' plot.")
	
	# Show figures if desired		
	if(p['showFigures']):
		dpu.show()

	return plotList



def plotsForExperiments(parameters, minExperiment=0, maxExperiment=float('inf')):
	"""Given the typical parameters used to run experiments, return a list of plots that could be made from the data that has been already collected."""
	
	return dpu.getPlotTypesFromDependencies(dlu.getDataFileNamesForDeviceExperiments(dlu.getDeviceDirectory(parameters), minExperiment=minExperiment, maxExperiment=maxExperiment), plotCategory='device')



if __name__ == '__main__':
	"""Feel free to add your own makePlots function calls to try this out!"""
	
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 145, 145, 'FullStaticBiasHistory', (3.5,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S6 floating - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'staticBiasSegmentDividers':True, 'enableGradient':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 118, 118, 'FullStaticBiasHistory', (3.5,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S5 Grounded Between - ', saveFigures=True, showFigures=False, startRelativeIndex=9, endRelativeIndex=16, plot_mode_parameters={'publication_mode':True,'staticBiasSegmentDividers':True, 'enableGradient':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'E', '27-28', 3, 4, 'FullTransferCurveHistory', (1.48 *2.24/1.74,1.74 *2.24/1.74), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S1 Comparison - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'enableColorBar':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 137, 137, 'FullStaticBiasHistory', (2.2 *3.5/2.2,1.408 *3.5/2.2), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S8 Light - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'enableGradient':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 127, 127, 'FullStaticBiasHistory', (2.2 *3.25/2.2,2.24), dataFolder='../../../AutexysData', saveFolder='../../../AutexysPlots', plotSaveName='Figure S9a Light - ', saveFigures=False, showFigures=True, plot_mode_parameters={'publication_mode':True, 'enableGradient':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 125, 125, 'FullStaticBiasHistory', (2.2 *3.25/2.2,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S9b Light - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'enableGradient':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 127, 127, 'FullSubthresholdCurveHistory', (1.45 *2.24/1.55,1.55 *2.24/1.55), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S10a Light - ', saveFigures=True, showFigures=False, sweepDirection='both', plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 125, 125, 'FullSubthresholdCurveHistory', (1.45 *2.24/1.55,1.55 *2.24/1.55), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S10b Light - ', saveFigures=True, showFigures=False, sweepDirection='both', plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 104, 104, 'FullSubthresholdCurveHistory', (1.45 *2.24/1.55,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S12a - ', saveFigures=True, showFigures=False, sweepDirection='both', plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False}) 
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 104, 104, 'FullTransferCurveHistory', (1.45 *2.24/1.55,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S12b - ', saveFigures=True, showFigures=False, sweepDirection='both', plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False}) 
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 24, 24, 'FullSubthresholdCurveHistory', (1.45 *2.24/1.55,1.55 *2.24/1.55), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S11a - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True,'enableErrorBars':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 24, 24, 'FullTransferCurveHistory', (1.48 *2.24/1.74,1.74 *2.24/1.74), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S11b - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True,'enableErrorBars':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 155, 155, 'FullStaticBiasHistory', (3.5,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S7 no grounding or floating - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True,'staticBiasChangeDividers':False,'enableGradient':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 3, 6, 'FullSubthresholdCurveHistory', (1.48 *2.24/1.74, 2.24), dataFolder='../../../AutexysData', saveFolder='../../../AutexysPlots', plotSaveName='Figure S4a - ', saveFigures=False, showFigures=True, plot_mode_parameters={'publication_mode':True,'enableErrorBars':False,'legendLabels':['Initial','After 1 week'],'legendLoc':'lower left'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 3, 6, 'FullTransferCurveHistory', (1.48 *2.24/1.74, 2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S4b - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True,'enableErrorBars':False,'legendLabels':['Initial','After 1 week'],'legendLoc':'lower left'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'E', '15-16', 1, 1, 'FullBurnOutHistory', (2.2 *4.5/2.2,1.408 *3.5/2.2), dataFolder='../../../AutexysData', saveFolder='../../../AutexysPlots', plotSaveName='Figure S4a - ', saveFigures=False, showFigures=True, startRelativeIndex=5, plot_mode_parameters={'publication_mode':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'E', '15-16', 1, 1, 'FullSubthresholdCurveHistory', (1.48 *2.24/1.74,1.74 *2.24/1.74), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S3 burnout gs - ', saveFigures=True, showFigures=True, plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False, 'legendLabels':['Initial','After Burn-out']})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'P', '1-2', 8, 8, 'FullStaticBiasHistory', (2.2 *4.5/2.2,1.408 *3.5/2.2), dataFolder='../../../AutexysData', saveFolder='../../../AutexysPlots/', plotSaveName='Figure - ', saveFigures=False, showFigures=True, startRelativeIndex=20, endRelativeIndex=70, plot_mode_parameters={'publication_mode':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 101, 127, 'FullSubthresholdCurveHistory', (1.45 *2.24/1.55,1.55 *2.24/1.55), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S13 - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False, 'legendLoc':'lower left'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'E', '15-16', 6, 13, 'FullTransferCurveHistory', (1.48 *2.24/1.74, 2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S14 carriers - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False, 'legendLoc':'lower left'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 172, 172, '', (1.48 *2.24/1.74, 2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S14 carriers - ', saveFigures=False, showFigures=True, plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False, 'legendLoc':'lower left'})
	#makePlots('stevenjay', 'SolutionBias1', 'C127', 'V', '2-3', 15, 23, '', (2.2 *4.5/2.2,1.408 *3.5/2.2), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S? burnout - ', saveFigures=True, showFigures=True, plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False, 'legendLoc':'best'})
	#makePlots('stevenjay', 'SolutionBias1', 'C127', 'W', '2-3', 0, 50, '', (2.2 *4.5/2.2,1.408 *3.5/2.2), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S? burnout - ', saveFigures=True, showFigures=True, plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False, 'legendLoc':'best'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 80, 168, 'FullStaticBiasHistory', (2.2 *5.5/2.2,1.408 *3.5/2.2), dataFolder='../../../AutexysData', saveFolder='../../../AutexysPlots/', plotSaveName='Figure S17a full - ', saveFigures=False, showFigures=True, plot_mode_parameters={'publication_mode':True, 'staticBiasChangeDividers':False, 'enableGradient':False, 'legendLoc':'best', 'plotInRealTime':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 80, 168, 'OnAndOffCurrentHistory', (2.2 *5.78/2.2,1.408 *3.5/2.2), dataFolder='../../../AutexysData', saveFolder='../../../AutexysPlots/', plotSaveName='Figure S17b full - ', saveFigures=False, showFigures=True, plot_mode_parameters={'publication_mode':True, 'staticBiasChangeDividers':False, 'enableGradient':False, 'legendLoc':'lower left'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'P', '15-16', 0, 500, '', None, dataFolder='../../../AutexysData', saveFolder='../../../AutexysPlots/', plotSaveName='Figure S17b full - ', saveFigures=False, showFigures=True, plot_mode_parameters={'publication_mode':False, 'staticBiasChangeDividers':False, 'enableGradient':False, 'legendLoc':'best'})
	#makePlots('stevenjay', 'SolutionBias1', 'C127', 'V', '2-3', 0, 500, 'FullOutputCurveHistory', None, dataFolder='../../../AutexysData', saveFolder='../../../AutexysPlots/', plotSaveName='Figure S17b full - ', saveFigures=False, showFigures=True, plot_mode_parameters={'publication_mode':False, 'staticBiasChangeDividers':False, 'enableGradient':False, 'legendLoc':'best'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'P', '1-2', 5, 7, 'SubthresholdCurve', None, plotSaveName='Figure S17b full - ', saveFigures=False, showFigures=True, plot_mode_parameters={'publication_mode':False, 'staticBiasChangeDividers':False, 'enableGradient':False, 'legendLoc':'best'})	
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'E', '15-16', 10, 18, 'OnAndOffCurrentHistory', None, dataFolder='../../AutexysData', saveFolder='../../../AutexysPlots/', plotSaveName='Figure S17b full - ', saveFigures=False, showFigures=True, plot_mode_parameters={'publication_mode':False, 'staticBiasChangeDividers':False, 'enableGradient':False, 'legendLoc':'best'})	
	#makePlots('steven', 'SGM1', 'F1', 'E', 'E08N_10000', 51, 51, 'AFMdeviationsVsX', None, dataFolder='../data', showFigures=True)
	#makePlots('jay', 'MoS2FET', 'JM3', 'B', '53-54', 9, 9, 'StaticBias', None, plotSaveName='Figure S17b full - ', saveFigures=True, showFigures=True, plot_mode_parameters={'publication_mode':False, 'staticBiasChangeDividers':False, 'enableGradient':False, 'legendLoc':'best', 'colorsOverride':['#56638A','#56638A','#56638A']})	
	#makePlots('matthew', 'TFTBiasStress1', 'C144', 'T', '13-14', 1, 1, 'GateCurrent', None, plotSaveName='Matthew4', dataFolder='../../AutexysData', showFigures=True, saveFigures=True)
	pass





