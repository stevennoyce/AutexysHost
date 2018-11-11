from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu
import copy



plotDescription = {
	'plotCategory': 'chip',
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'ylabel':'Transconductance [$\\mu$A/V]',
	},
}

def plot(identifiers, chipIndexes, firstRunChipHistory, recentRunChipHistory, specificRunChipHistory, mode_parameters=None):
	# Load Defaults
	plotDescrip_current = copy.deepcopy(plotDescription)

	# Init Figure
	fig, ax = initFigure(1, 1, plotDescrip_current['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title('Chip ' + str(identifiers['wafer']) + str(identifiers['chip']))
		
	# Plot
	gm, vt, r2 = dpu.fitBasicDeviceModel(specificRunChipHistory)
	gm = [val*1000000 for val in gm] #Convert to uA
	line = boxplot(ax, gm)

	axisLabels(ax, y_label=plotDescrip_current['plotDefaults']['ylabel'])


	# Save figure	
	adjustAndSaveFigure(fig, 'ChipTransconductance', mode_parameters)

	return (fig, ax)

