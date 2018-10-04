from .PlotDefinitions import PlotDefinitions as dpd
from . import MatplotlibUtility as mplu



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
	
	if(plotType == 'SubthresholdCurve'):
		fig, axes = dpd.plotFullSubthresholdCurveHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'TransferCurve'):
		fig, axes = dpd.plotFullTransferCurveHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'GateCurrent'):
		fig, axes = dpd.plotFullGateCurrentHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'OutputCurve'):
		fig, axes = dpd.plotFullOutputCurveHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'BurnOut'):
		fig, axes = dpd.plotFullBurnOutHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'StaticBias'):
		fig, axes = dpd.plotFullStaticBiasHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'OnCurrent'):
		fig, axes = dpd.plotOnAndOffCurrentHistory(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'AFMSignalsOverTime'):
		fig, axes = dpd.plotAFMSignalsOverTime(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'AFMdeviationsVsX'):
		fig, axes = dpd.plotAFMdeviationsVsX(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	elif(plotType == 'AFMdeviationsVsXY'):
		fig, axes = dpd.plotAFMdeviationsVsXY(deviceHistory, identifiers, mode_parameters=updated_mode_parameters)
	else:
		raise NotImplementedError('Unrecognized "plotType": ' + str(plotType))
	
	return fig, axes

def makeChipPlot(plotType, identifiers=None, chipIndexes=None, firstRunChipHistory=None, recentRunChipHistory=None, mode_parameters=None):	
	if(plotType is 'ChipHistogram' and ((chipIndexes is None) or len(chipIndexes) <= 0)):
		print('No chip histogram to plot.')
		return
	elif((recentRunChipHistory is None) or len(recentRunChipHistory) <= 0):
		print('No ' + str(plotType) + ' chip history to plot.')
	
	if((recentRunChipHistory is None) or len(recentRunChipHistory) <= 0):
			print('No  ratios to plot.')
			return
	
	updated_mode_parameters = default_mode_parameters.copy()
	if(mode_parameters is not None):
		updated_mode_parameters.update(mode_parameters)

	if(plotType == 'ChipHistogram'):			
		return plotChipHistogram(chipIndexes, mode_parameters=updated_mode_parameters)
	elif(plotType == 'ChipOnOffRatios'):
		return plotChipOnOffRatios(firstRunChipHistory, recentRunChipHistory, mode_parameters=updated_mode_parameters)
	elif(plotType == 'ChipOnOffCurrents'):
		return plotChipOnOffCurrents(recentRunChipHistory, mode_parameters=updated_mode_parameters)
	elif(plotType == 'ChipTransferCurves'):
		return plotChipTransferCurves(recentRunChipHistory, identifiers, mode_parameters=updated_mode_parameters)
	else:
		raise NotImplementedError('Unrecognized "plotType": ' + str(plotType))

def show():
	mplu.show()


