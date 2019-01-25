from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu



plotDescription = {
	'plotCategory': 'device',
	'priority': 220,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'xlabel':'Trial',
		'ylabel':'Threshold Voltage (V)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
		
	# Plot
	gm, vt, r2 = dpu.fitBasicDeviceModel(deviceHistory)
	if mode_parameters['useBoxWhiskerPlot']: 
		line = boxplot(ax, vt)
	else: 
		line = ax.plot(range(len(vt)), vt, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)

	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])

	# Save figure	
	adjustAndSaveFigure(fig, 'Threshold', mode_parameters)

	return (fig, ax)