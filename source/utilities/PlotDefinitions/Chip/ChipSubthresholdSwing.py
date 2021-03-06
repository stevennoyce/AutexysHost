from utilities.MatplotlibUtility import *
from utilities.PlotDefinitions.Metrics.BoxPlotSubthresholdSwing import plot as importedBoxPlot



plotDescription = {
	'name':'Chip SS',
	'plotCategory': 'chip',
	'priority': 1050,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.3),
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, groupedChipHistory, mode_parameters=None):
	if(mode_parameters is None):
		mode_parameters = {}
	mode_parameters['figureSizeOverride'] = plotDescription['plotDefaults']['figsize'] if(mode_parameters['figureSizeOverride'] is None) else mode_parameters['figureSizeOverride']
	
	return importedBoxPlot(specificRunChipHistory, identifiers, mode_parameters=mode_parameters)
