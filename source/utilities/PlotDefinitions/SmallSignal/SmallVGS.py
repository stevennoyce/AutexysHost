from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 450,
	'dataFileDependencies': ['SmallSignal.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'automaticAxisLabels':True,
		'colorMap':'white_violet_black',
		'colorDefault': ['#351996'],
		'xlabel':'Time (s)',
		'ylabel':'$v_{{gs}}$ (V)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Build Color Map
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=[], colorBarAxisLabel='')		

	# Plot
	for i in range(len(deviceHistory)):
		for j in range(len(deviceHistory[i]['Results']['timestamps'])):
			line = ax.plot(np.array(deviceHistory[i]['Results']['timestamps'][j]) - min(deviceHistory[i]['Results']['timestamps'][0]),  np.array(deviceHistory[i]['Results']['vgs_data'][j]), color=colors[i], marker='o', markersize=2, linewidth=1)
					
	return (fig, (ax,))



