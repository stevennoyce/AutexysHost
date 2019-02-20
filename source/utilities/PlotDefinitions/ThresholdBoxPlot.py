from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu



plotDescription = {
	'plotCategory': 'device',
	'priority': 2020,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'automaticAxisLabels':True,
		'xlabel':'Trial',
		'ylabel':'Threshold Voltage (V)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
		
	# Plot
	gm, vt, r2 = dpu.fitBasicDeviceModel(deviceHistory)
	if mode_parameters['useBoxWhiskerPlot']: 
		line = boxplot(ax, vt)
	else: 
		line = ax.plot(range(len(vt)), vt, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)

	return (fig, (ax,))