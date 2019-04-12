from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 660,
	'dataFileDependencies': ['RapidBias.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'automaticAxisLabels':True,
		'colorMap':'white_blue_black',
		'colorDefault': ['#1f77b4'],
		'xlabel':'Time (s)',
		'ylabel':'Signal/Maximum (a.u.)',
		'micro_ylabel':'$I_{{D}}$ ($\\mu$A)',
		'nano_ylabel':'$I_{{D}}$ (nA)',
		'neg_micro_ylabel':'$-I_{{D}}$ ($\\mu$A)',
		'neg_nano_ylabel':'$-I_{{D}}$ (nA)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Build Color Map
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=[], colorBarAxisLabel='')		

	# Plot
	for i in range(len(deviceHistory)):
		line = ax.plot(np.array(deviceHistory[i]['Results']['timestamps']) - min(deviceHistory[i]['Results']['timestamps']),  np.array(deviceHistory[i]['Results']['id_data'])/max(np.abs((deviceHistory[i]['Results']['id_data']))), color=colors[i], marker='o', markersize=2, linewidth=1)
		line = ax.plot(np.array(deviceHistory[i]['Results']['timestamps']) - min(deviceHistory[i]['Results']['timestamps']),  np.array(deviceHistory[i]['Results']['vgs_data'])/max(np.abs((deviceHistory[i]['Results']['vgs_data']))), color='#333333', linewidth=0.75, ls='-')
							
	return (fig, (ax,))



