from utilities.MatplotlibUtility import *
from utilities import DataProcessorUtility as dpu



plotDescription = {
	'plotCategory': 'device',
	'priority': 2010,
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'automaticAxisLabels':True,
		'xlabel':'Trial',
		'ylabel':'Transconductance ($\\mu$A/V)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
		
	# Plot
	gm, vt, r2 = dpu.fitBasicDeviceModel(deviceHistory)
	gm = [val*1000000 for val in gm] #Convert to uA
	if mode_parameters['useBoxWhiskerPlot'] :
		line = boxplot(ax, gm)
	else:
		line = ax.plot(range(len(gm)), gm, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][0], marker='o', markersize=4, linewidth=0, linestyle=None)

	return (fig, (ax,))
