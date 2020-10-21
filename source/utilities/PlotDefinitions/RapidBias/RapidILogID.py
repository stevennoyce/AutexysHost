from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Drain Current',
	'plotCategory': 'device',
	'priority': 420,
	'dataFileDependencies': ['RapidBias.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'automaticAxisLabels':True,
		'colorMap':'white_blue_black',
		'colorDefault': ['#1f77b4'],
		'xlabel':'Time (s)',
		'ylabel':'|$I_{{D}}$| (A)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Build Color Map
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=[], colorBarAxisLabel='')		

	# Plot
	for i in range(len(deviceHistory)):
		line = ax.plot(np.array(deviceHistory[i]['Results']['timestamps']) - min(deviceHistory[i]['Results']['timestamps']),  np.array(deviceHistory[i]['Results']['id_data']), color=colors[i], marker='o', markersize=2, linewidth=1)
		
	ax.set_yscale('log')	

	return (fig, (ax,))



