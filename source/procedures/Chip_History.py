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



# === Optional External Interface ===
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



# === Main ===
def run(additional_parameters, plot_mode_parameters={}):
	parameters = default_ch_parameters.copy()
	parameters.update(additional_parameters)

	plot_mode_parameters['showFigures'] = parameters['showFiguresGenerated']
	plot_mode_parameters['saveFigures'] = parameters['saveFiguresGenerated']

	plotList = []

	if(parameters['specificPlotToCreate'] in ['', 'ChipHistogram']):
		chipIndexes = dlu.loadChipIndexes(dlu.getChipDirectory(parameters))
		plot = dpu.makeChipPlot('ChipHistogram', parameters['Identifiers'], chipIndexes=chipIndexes, mode_parameters=plot_mode_parameters)
		plotList.append(plot)

	if(parameters['specificPlotToCreate'] in ['', 'ChipOnOffRatios']):
		firstRunChipHistory = dlu.loadFirstRunChipHistory(dlu.getChipDirectory(parameters), 'GateSweep.json')
		recentRunChipHistory = dlu.loadMostRecentRunChipHistory(dlu.getChipDirectory(parameters), 'GateSweep.json')
		plot = dpu.makeChipPlot('ChipOnOffRatios', parameters['Identifiers'], firstRunChipHistory=firstRunChipHistory, recentRunChipHistory=recentRunChipHistory, mode_parameters=plot_mode_parameters)
		plotList.append(plot)
	
	if(parameters['specificPlotToCreate'] in ['', 'ChipOnOffCurrents']):
		recentRunChipHistory = dlu.loadMostRecentRunChipHistory(dlu.getChipDirectory(parameters), 'GateSweep.json')
		plot = dpu.makeChipPlot('ChipOnOffCurrents', parameters['Identifiers'], recentRunChipHistory=recentRunChipHistory, mode_parameters=plot_mode_parameters)
		plotList.append(plot)
	
	if(parameters['specificPlotToCreate'] in ['', 'ChipTransferCurves']):
		recentRunChipHistory = dlu.loadMostRecentRunChipHistory(dlu.getChipDirectory(parameters), 'GateSweep.json')
		plot = dpu.makeChipPlot('ChipTransferCurves', parameters['Identifiers'], recentRunChipHistory=recentRunChipHistory, mode_parameters=plot_mode_parameters)
		plotList.append(plot)

	if(parameters['showFiguresGenerated']):
		dpu.show()

	return plotList





if(__name__ == '__main__'):
	makePlots('stevenjay', 'RedBoard', 'C127', 'D')


