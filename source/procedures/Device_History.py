# === Make this script runnable ===
if(__name__ == '__main__'):
	import sys
	sys.path.append(sys.path[0] + '/..')

# === Imports ===
from utilities import DataPlotterUtility as dpu
from utilities import DataLoggerUtility as dlu
from utilities import PlotPostingUtility as plotPoster



# === Defaults ===
default_dh_parameters = {
	'dataFolder': 'data/',
	'postFolder': 'CurrentPlots/',
	'showFiguresGenerated': True,
	'saveFiguresGenerated': True,
	'postFiguresGenerated': False,
	'plotGateSweeps': True,
	'plotBurnOuts':   True,
	'plotStaticBias': True,
	'specificPlotToCreate': '',
	'excludeDataBeforeJSONIndex': 0,
	'excludeDataAfterJSONIndex':  float('inf'),
	'excludeDataBeforeJSONExperimentNumber': 0,
	'excludeDataAfterJSONExperimentNumber':  float('inf'),
	'excludeDataBeforeJSONRelativeIndex': 0,
	'excludeDataAfterJSONRelativeIndex':  float('inf'),
	'showOnlySuccessfulBurns': False,
}

plots_for_experiment = {
	'GateSweep' : {
		'primary':[	
			'FullSubthresholdCurveHistory',
			'FullTransferCurveHistory',
			'FullGateCurrentHistory'
		]
	},
	'DrainSweep': {
		'primary':[
			'FullOutputCurveHistory'
		]
	},
	'BurnOut' : {	
		'primary':[	
			'FullBurnOutHistory'
		]
	},
	'AutoBurnOut' : {
		'primary':[
			'FullBurnOutHistory',
			'FullSubthresholdCurveHistory',
			'FullTransferCurveHistory',
			'FullGateCurrentHistory',
			'OnAndOffCurrentHistory'
		]
	},
	'StaticBias' : {
		'primary':[
			'FullStaticBiasHistory'
		]
	},
	'AutoGateSweep' : {
		'primary':[
			'FullSubthresholdCurveHistory',
			'FullTransferCurveHistory',
			'FullGateCurrentHistory',
			'OnAndOffCurrentHistory',
			'FullStaticBiasHistory'
		],
	},
	'AutoStaticBias' : {
		'primary':[
			'FullStaticBiasHistory',
			
		],
		'secondary':[
			'FullStaticBiasHistory',
			'FullSubthresholdCurveHistory',
			'FullTransferCurveHistory',
			'FullGateCurrentHistory',
			'OnAndOffCurrentHistory'
		]
	},
	'AFMControl' : {
		'primary':[
			'AFMSignalsOverTime',
			'AFMdeviationsVsX',
			'AFMdeviationsVsXY'
		]
	}
}

def getPossiblePlotNames(parameters):
	try:
		p = parameters
		asb_parameters = parameters['runConfigs']['AutoStaticBias']
		ags_parameters = parameters['runConfigs']['AutoGateSweep']
		
		plotsType = 'primary'
		if(p['runType'] == 'AutoStaticBias'):
			plotsType = 'secondary' if((('doInitialGateSweep' in asb_parameters) and asb_parameters['doInitialGateSweep']) or asb_parameters['applyGateSweepBetweenBiases']) else 'primary' 
		
		return plots_for_experiment[p['runType']][plotsType]
	except Exception as e:
		print('Exception raised in getPossiblePlotNames')
		print(e)
		return [
			'FullStaticBiasHistory',
			'FullSubthresholdCurveHistory',
			'FullTransferCurveHistory',
			'FullGateCurrentHistory',
			'OnAndOffCurrentHistory',
			'FullBurnOutHistory'
		]



# === Optional External Interface ===
def makePlots(userID, projectID, waferID, chipID, deviceID, startExperimentNumber=0, endExperimentNumber=float('inf'), specificPlot='', figureSize=None, dataFolder=None, saveFolder=None, plotSaveName='', saveFigures=False, showFigures=True, sweepDirection='both', plotInRealTime=True, startRelativeIndex=0, endRelativeIndex=float('inf'), plot_mode_parameters=None):
	parameters = {}	
	mode_parameters = {}
	if(plot_mode_parameters is not None):
		mode_parameters.update(plot_mode_parameters)
	
	parameters['Identifiers'] = {}
	parameters['Identifiers']['user'] = userID
	parameters['Identifiers']['project'] = projectID
	parameters['Identifiers']['wafer'] = waferID
	parameters['Identifiers']['chip'] = chipID
	parameters['Identifiers']['device'] = deviceID

	if(dataFolder is not None):
		parameters['dataFolder'] = dataFolder

	parameters['showFiguresGenerated'] = showFigures
	parameters['saveFiguresGenerated'] = saveFigures
	parameters['postFiguresGenerated'] = False
	parameters['specificPlotToCreate'] = specificPlot
	parameters['excludeDataBeforeJSONExperimentNumber'] = startExperimentNumber
	parameters['excludeDataAfterJSONExperimentNumber'] = endExperimentNumber
	parameters['excludeDataBeforeJSONRelativeIndex'] = startRelativeIndex
	parameters['excludeDataAfterJSONRelativeIndex'] = endRelativeIndex
	
	if(saveFolder is not None):
		mode_parameters['plotSaveFolder'] = saveFolder
	mode_parameters['plotSaveName'] = plotSaveName
	mode_parameters['figureSizeOverride'] = figureSize
	mode_parameters['sweepDirection'] = sweepDirection
	mode_parameters['plotInRealTime'] = plotInRealTime
	
	return run(parameters, plot_mode_parameters=mode_parameters)



# === Main ===
def run(additional_parameters, plot_mode_parameters=None):
	parameters = default_dh_parameters.copy()
	parameters.update(additional_parameters)

	p = parameters
	plotList = []

	mode_parameters = {}
	if(plot_mode_parameters != None):
		mode_parameters.update(plot_mode_parameters)
	mode_parameters['showFigures'] = p['showFiguresGenerated']
	mode_parameters['saveFigures'] = p['saveFiguresGenerated']

	# Print information about the device and experiment being plotted
	print('  ' + parameters['Identifiers']['wafer'] + parameters['Identifiers']['chip'] + ':' + parameters['Identifiers']['device'])
	'' if((p['excludeDataBeforeJSONExperimentNumber'] == 0) and (p['excludeDataAfterJSONExperimentNumber'] == float('inf'))) else (print('  Experiment #{:}'.format(p['excludeDataAfterJSONExperimentNumber'])) if(p['excludeDataBeforeJSONExperimentNumber'] == p['excludeDataAfterJSONExperimentNumber']) else (print('  Experiments #{:} to #{:}'.format(p['excludeDataBeforeJSONExperimentNumber'],p['excludeDataAfterJSONExperimentNumber'])))) 
	'' if((p['excludeDataBeforeJSONRelativeIndex'] == 0) and (p['excludeDataAfterJSONRelativeIndex'] == float('inf'))) else (print('  Rel. Index #{:}'.format(p['excludeDataAfterJSONRelativeIndex'])) if(p['excludeDataBeforeJSONRelativeIndex'] == p['excludeDataAfterJSONRelativeIndex']) else (print('  Rel. Indices #{:} to #{:}'.format(p['excludeDataBeforeJSONRelativeIndex'],p['excludeDataAfterJSONRelativeIndex']))))
	'' if((p['excludeDataBeforeJSONIndex'] == 0) and (p['excludeDataAfterJSONIndex'] == float('inf'))) else (print('  Abs. Index #{:}'.format(p['excludeDataAfterJSONIndex'])) if(p['excludeDataBeforeJSONIndex'] == p['excludeDataAfterJSONIndex']) else (print('  Abs. Indices #{:} to #{:}'.format(p['excludeDataBeforeJSONIndex'],p['excludeDataAfterJSONIndex']))))

	# Try to load general information file 'wafer.json' if such a file exists
	if('generalInfo' not in mode_parameters):
		try:
			wafer_info = dlu.loadJSON(dlu.getWaferDirectory(parameters), 'wafer.json')[0]
			mode_parameters['generalInfo'] = wafer_info
		except:
			print('Error: no information in wafer.json for this device.')
	
	if(p['plotGateSweeps'] and (p['specificPlotToCreate'] in ['FullSubthresholdCurveHistory','FullTransferCurveHistory','FullGateCurrentHistory','OnAndOffCurrentHistory',''])):
		try:			
			gateSweepHistory = dlu.loadSpecificDeviceHistory(dlu.getDeviceDirectory(parameters), 'GateSweep.json', minIndex=p['excludeDataBeforeJSONIndex'], maxIndex=p['excludeDataAfterJSONIndex'], minExperiment=p['excludeDataBeforeJSONExperimentNumber'], maxExperiment=p['excludeDataAfterJSONExperimentNumber'], minRelativeIndex=p['excludeDataBeforeJSONRelativeIndex'], maxRelativeIndex=p['excludeDataAfterJSONRelativeIndex'])

			if p['specificPlotToCreate'] in ['FullSubthresholdCurveHistory','']:
				plot1 = dpu.makeDevicePlot('SubthresholdCurve', gateSweepHistory, parameters['Identifiers'], mode_parameters=mode_parameters)
				plotList.append(plot1)
			if p['specificPlotToCreate'] in ['FullTransferCurveHistory','']:
				plot2 = dpu.makeDevicePlot('TransferCurve', gateSweepHistory, parameters['Identifiers'], mode_parameters=mode_parameters)
				plotList.append(plot2)
			if p['specificPlotToCreate'] in ['FullGateCurrentHistory','']:
				plot3 = dpu.makeDevicePlot('GateCurrent', gateSweepHistory, parameters['Identifiers'], mode_parameters=mode_parameters)
				plotList.append(plot3)
			if p['specificPlotToCreate'] in ['OnAndOffCurrentHistory','']:
				plot4 = dpu.makeDevicePlot('OnCurrent', gateSweepHistory, parameters['Identifiers'], mode_parameters=mode_parameters)
				plotList.append(plot4)
		except FileNotFoundError:
			print("Error: Unable to find Gate Sweep history.")

	if(p['specificPlotToCreate'] in ['', 'FullOutputCurveHistory']):
		try:
			drainSweepHistory = dlu.loadSpecificDeviceHistory(dlu.getDeviceDirectory(parameters), 'DrainSweep.json', minIndex=p['excludeDataBeforeJSONIndex'], maxIndex=p['excludeDataAfterJSONIndex'], minExperiment=p['excludeDataBeforeJSONExperimentNumber'], maxExperiment=p['excludeDataAfterJSONExperimentNumber'], minRelativeIndex=p['excludeDataBeforeJSONRelativeIndex'], maxRelativeIndex=p['excludeDataAfterJSONRelativeIndex'])

			if p['specificPlotToCreate'] in ['FullOutputCurveHistory','']:
				plot = dpu.makeDevicePlot('OutputCurve', drainSweepHistory, parameters['Identifiers'], mode_parameters=mode_parameters)
				plotList.append(plot)
		except FileNotFoundError:
			print("Error: Unable to find Drain Sweep history.")

	if(p['plotBurnOuts'] and (p['specificPlotToCreate'] in ['FullBurnOutHistory',''])):
		try:
			burnOutHistory = dlu.loadSpecificDeviceHistory(dlu.getDeviceDirectory(parameters), 'BurnOut.json', minIndex=p['excludeDataBeforeJSONIndex'], maxIndex=p['excludeDataAfterJSONIndex'], minExperiment=p['excludeDataBeforeJSONExperimentNumber'], maxExperiment=p['excludeDataAfterJSONExperimentNumber'], minRelativeIndex=p['excludeDataBeforeJSONRelativeIndex'], maxRelativeIndex=p['excludeDataAfterJSONRelativeIndex'])

			if(p['showOnlySuccessfulBurns']):
				burnOutHistory = dlu.filterHistory(burnOutHistory, 'didBurnOut', True, ['Computed'])
			
			if p['specificPlotToCreate'] in ['FullBurnOutHistory','']:
				plot = dpu.makeDevicePlot('BurnOut', burnOutHistory, parameters['Identifiers'], mode_parameters=mode_parameters)
				plotList.append(plot)
		except FileNotFoundError:
			print("Error: Unable to find Burnout history.")

	if(p['plotStaticBias'] and (p['specificPlotToCreate'] in ['FullStaticBiasHistory',''])):
		try:
			staticBiasHistory = dlu.loadSpecificDeviceHistory(dlu.getDeviceDirectory(parameters), 'StaticBias.json', minIndex=p['excludeDataBeforeJSONIndex'], maxIndex=p['excludeDataAfterJSONIndex'], minExperiment=p['excludeDataBeforeJSONExperimentNumber'], maxExperiment=p['excludeDataAfterJSONExperimentNumber'], minRelativeIndex=p['excludeDataBeforeJSONRelativeIndex'], maxRelativeIndex=p['excludeDataAfterJSONRelativeIndex'])
			
			if p['specificPlotToCreate'] in ['FullStaticBiasHistory','']:
				plot = dpu.makeDevicePlot('StaticBias', staticBiasHistory, parameters['Identifiers'], mode_parameters=mode_parameters)
				plotList.append(plot)
		except FileNotFoundError:
			print("Error: Unable to find Static Bias history.")
	
	if( (p['specificPlotToCreate'] in ['AFMSignalsOverTime',''])):
		try:
			AFMHistory = dlu.loadSpecificDeviceHistory(dlu.getDeviceDirectory(parameters), 'AFMControl.json', minIndex=p['excludeDataBeforeJSONIndex'], maxIndex=p['excludeDataAfterJSONIndex'], minExperiment=p['excludeDataBeforeJSONExperimentNumber'], maxExperiment=p['excludeDataAfterJSONExperimentNumber'], minRelativeIndex=p['excludeDataBeforeJSONRelativeIndex'], maxRelativeIndex=p['excludeDataAfterJSONRelativeIndex'])
			
			if p['specificPlotToCreate'] in ['AFMSignalsOverTime','']:
				plot = dpu.makeDevicePlot('AFMSignalsOverTime', AFMHistory, parameters['Identifiers'], mode_parameters=mode_parameters)
				plotList.append(plot)
		except FileNotFoundError:
			print("Error: Unable to find AFM history.")
	
	if( (p['specificPlotToCreate'] in ['AFMdeviationsVsX',''])):
		try:
			AFMHistory = dlu.loadSpecificDeviceHistory(dlu.getDeviceDirectory(parameters), 'AFMControl.json', minIndex=p['excludeDataBeforeJSONIndex'], maxIndex=p['excludeDataAfterJSONIndex'], minExperiment=p['excludeDataBeforeJSONExperimentNumber'], maxExperiment=p['excludeDataAfterJSONExperimentNumber'], minRelativeIndex=p['excludeDataBeforeJSONRelativeIndex'], maxRelativeIndex=p['excludeDataAfterJSONRelativeIndex'])
			
			if p['specificPlotToCreate'] in ['AFMdeviationsVsX','']:
				plot = dpu.makeDevicePlot('AFMdeviationsVsX', AFMHistory, parameters['Identifiers'], mode_parameters=mode_parameters)
				plotList.append(plot)
		except FileNotFoundError:
			print("Error: Unable to find AFM history.")
	
	if( (p['specificPlotToCreate'] in ['AFMdeviationsVsXY',''])):
		try:
			AFMHistory = dlu.loadSpecificDeviceHistory(dlu.getDeviceDirectory(parameters), 'AFMControl.json', minIndex=p['excludeDataBeforeJSONIndex'], maxIndex=p['excludeDataAfterJSONIndex'], minExperiment=p['excludeDataBeforeJSONExperimentNumber'], maxExperiment=p['excludeDataAfterJSONExperimentNumber'], minRelativeIndex=p['excludeDataBeforeJSONRelativeIndex'], maxRelativeIndex=p['excludeDataAfterJSONRelativeIndex'])
			
			if p['specificPlotToCreate'] in ['AFMdeviationsVsXY','']:
				plot = dpu.makeDevicePlot('AFMdeviationsVsXY', AFMHistory, parameters['Identifiers'], mode_parameters=mode_parameters)
				plotList.append(plot)
		except FileNotFoundError:
			print("Error: Unable to find AFM history.")

	if(p['showFiguresGenerated']):
		dpu.show()
	
	if(p['postFiguresGenerated']):
		parameters['startIndexes'] = {
			'index': max( parameters['excludeDataBeforeJSONIndex'], min(loadIndexesOfExperiementRange(directory, parameters['excludeDataBeforeJSONExperimentNumber'], parameters['excludeDataAfterJSONExperimentNumber'])) ),
			'experimentNumber': parameters['excludeDataBeforeJSONExperimentNumber']
		}
		parameters['endIndexes'] = {
			'index': min( parameters['excludeDataAfterJSONIndex'], max(loadIndexesOfExperiementRange(directory, parameters['excludeDataBeforeJSONExperimentNumber'], parameters['excludeDataAfterJSONExperimentNumber'])) ),
			'experimentNumber': min(parameters['excludeDataAfterJSONExperimentNumber'], dlu.loadJSONIndex(dlu.getDeviceDirectory(parameters))['experimentNumber'])
		} 

		dlu.makeFolder(parameters['postFolder'])
		dlu.emptyFolder(parameters['postFolder'])

		print('Posting plots online...')
		plotPoster.postPlots(parameters)

	return plotList





if __name__ == '__main__':
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 145, 145, 'FullStaticBiasHistory', (3.5,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S6 floating - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'staticBiasSegmentDividers':True, 'enableGradient':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 118, 118, 'FullStaticBiasHistory', (3.5,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S5 Grounded Between - ', saveFigures=True, showFigures=False, startRelativeIndex=9, endRelativeIndex=16, plot_mode_parameters={'publication_mode':True,'staticBiasSegmentDividers':True, 'enableGradient':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'E', '27-28', 3, 4, 'FullTransferCurveHistory', (1.48 *2.24/1.74,1.74 *2.24/1.74), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S1 Comparison - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'enableColorBar':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 137, 137, 'FullStaticBiasHistory', (2.2 *3.5/2.2,1.408 *3.5/2.2), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S8 Light - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'enableGradient':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 127, 127, 'FullStaticBiasHistory', (2.2 *3.25/2.2,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S9a Light - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'enableGradient':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 125, 125, 'FullStaticBiasHistory', (2.2 *3.25/2.2,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S9b Light - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'enableGradient':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 127, 127, 'FullSubthresholdCurveHistory', (1.45 *2.24/1.55,1.55 *2.24/1.55), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S10a Light - ', saveFigures=True, showFigures=False, sweepDirection='both', plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 125, 125, 'FullSubthresholdCurveHistory', (1.45 *2.24/1.55,1.55 *2.24/1.55), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S10b Light - ', saveFigures=True, showFigures=False, sweepDirection='both', plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 104, 104, 'FullSubthresholdCurveHistory', (1.45 *2.24/1.55,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S12a - ', saveFigures=True, showFigures=False, sweepDirection='both', plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False}) 
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 104, 104, 'FullTransferCurveHistory', (1.45 *2.24/1.55,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S12b - ', saveFigures=True, showFigures=False, sweepDirection='both', plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False}) 
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 24, 24, 'FullSubthresholdCurveHistory', (1.45 *2.24/1.55,1.55 *2.24/1.55), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S11a - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True,'enableErrorBars':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 24, 24, 'FullTransferCurveHistory', (1.48 *2.24/1.74,1.74 *2.24/1.74), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S11b - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True,'enableErrorBars':False})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 155, 155, 'FullStaticBiasHistory', (3.5,2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S7 no grounding or floating - ', saveFigures=True, showFigures=False, plotInRealTime=True, plot_mode_parameters={'publication_mode':True,'staticBiasChangeDividers':False,'enableGradient':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 3, 6, 'FullSubthresholdCurveHistory', (1.48 *2.24/1.74, 2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S4a - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True,'enableErrorBars':False,'legendLabels':['Initial','After 1 week'],'legendLoc':'lower left'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 3, 6, 'FullTransferCurveHistory', (1.48 *2.24/1.74, 2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S4b - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True,'enableErrorBars':False,'legendLabels':['Initial','After 1 week'],'legendLoc':'lower left'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'E', '15-16', 1, 1, 'FullBurnOutHistory', (2.2 *4.5/2.2,1.408 *3.5/2.2), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S4a - ', saveFigures=True, showFigures=False, startRelativeIndex=5, plot_mode_parameters={'publication_mode':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'E', '15-16', 1, 1, 'FullSubthresholdCurveHistory', (1.48 *2.24/1.74,1.74 *2.24/1.74), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S3 burnout gs - ', saveFigures=True, showFigures=True, plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False, 'legendLabels':['Initial','After Burn-out']})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'P', '1-2', 8, 8, 'FullStaticBiasHistory', (2.2 *4.5/2.2,1.408 *3.5/2.2), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure - ', saveFigures=False, showFigures=True, startRelativeIndex=20, endRelativeIndex=70, plot_mode_parameters={'publication_mode':True})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 101, 127, 'FullSubthresholdCurveHistory', (1.45 *2.24/1.55,1.55 *2.24/1.55), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S13 - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False, 'legendLoc':'lower left'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'E', '15-16', 6, 13, 'FullTransferCurveHistory', (1.48 *2.24/1.74, 2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S14 carriers - ', saveFigures=True, showFigures=False, plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False, 'legendLoc':'lower left'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 172, 172, '', (1.48 *2.24/1.74, 2.24), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S14 carriers - ', saveFigures=False, showFigures=True, plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False, 'legendLoc':'lower left'})
	#makePlots('stevenjay', 'SolutionBias1', 'C127', 'V', '2-3', 15, 23, '', (2.2 *4.5/2.2,1.408 *3.5/2.2), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S? burnout - ', saveFigures=True, showFigures=True, plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False, 'legendLoc':'best'})
	#makePlots('stevenjay', 'SolutionBias1', 'C127', 'W', '2-3', 0, 50, '', (2.2 *4.5/2.2,1.408 *3.5/2.2), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S? burnout - ', saveFigures=True, showFigures=True, plot_mode_parameters={'publication_mode':True, 'enableErrorBars':False, 'legendLoc':'best'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 80, 168, 'FullStaticBiasHistory', (2.2 *5.5/2.2,1.408 *3.5/2.2), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S17a full - ', saveFigures=True, showFigures=False, plotInRealTime=False, plot_mode_parameters={'publication_mode':True, 'staticBiasChangeDividers':False, 'enableGradient':True, 'legendLoc':'best'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'X', '15-16', 80, 168, 'OnAndOffCurrentHistory', (2.2 *5.78/2.2,1.408 *3.5/2.2), dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S17b full - ', saveFigures=True, showFigures=False, plotInRealTime=True, plot_mode_parameters={'publication_mode':True, 'staticBiasChangeDividers':False, 'enableGradient':False, 'legendLoc':'lower left'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'P', '15-16', 0, 500, '', None, dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S17b full - ', saveFigures=False, showFigures=True, plotInRealTime=True, plot_mode_parameters={'publication_mode':False, 'staticBiasChangeDividers':False, 'enableGradient':False, 'legendLoc':'best'})
	#makePlots('stevenjay', 'SolutionBias1', 'C127', 'V', '2-3', 0, 500, 'FullOutputCurveHistory', None, dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S17b full - ', saveFigures=False, showFigures=True, plotInRealTime=True, plot_mode_parameters={'publication_mode':False, 'staticBiasChangeDividers':False, 'enableGradient':False, 'legendLoc':'best'})
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'P', '1-2', 5, 7, 'FullTransferCurveHistory', None, dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S17b full - ', saveFigures=False, showFigures=True, plotInRealTime=True, plot_mode_parameters={'publication_mode':False, 'staticBiasChangeDividers':False, 'enableGradient':False, 'legendLoc':'best'})	
	#makePlots('stevenjay', 'BiasStress1', 'C127', 'E', '15-16', 10, 18, 'OnAndOffCurrentHistory', None, dataFolder='../data', saveFolder='../CurrentPlots', plotSaveName='Figure S17b full - ', saveFigures=False, showFigures=True, plotInRealTime=True, plot_mode_parameters={'publication_mode':False, 'staticBiasChangeDividers':False, 'enableGradient':False, 'legendLoc':'best'})	
	makePlots('steven', 'SGM1', 'F1', 'E', 'E08N_10000', 51, 51, 'AFMdeviationsVsX', None, dataFolder='../data', showFigures=True)
	pass





