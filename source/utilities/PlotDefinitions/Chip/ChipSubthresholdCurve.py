from utilities.MatplotlibUtility import *
from utilities.PlotDefinitions.GateSweep.SubthresholdCurve import plot as importedSubthresholdCurvePlot



plotDescription = {
	'plotCategory': 'chip',
	'priority': 20,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.5,3.125),
		'colorMap':'viridis',
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory, mode_parameters=None):
	if(mode_parameters is None):
		mode_parameters = {}
	#mode_parameters['enableColorBar'] = False
	mode_parameters['colorsOverride'] = (plotDescription['plotDefaults']['colorMap'], 0.85, 0) if(mode_parameters['colorsOverride'] == []) else mode_parameters['colorsOverride']
	mode_parameters['figureSizeOverride'] = plotDescription['plotDefaults']['figsize'] 		   if(mode_parameters['figureSizeOverride'] is None) else mode_parameters['figureSizeOverride']
	
	return importedSubthresholdCurvePlot(specificRunChipHistory, identifiers=identifiers, mode_parameters=mode_parameters)