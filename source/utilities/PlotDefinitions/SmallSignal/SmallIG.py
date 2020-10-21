from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Gate Current',
	'plotCategory': 'device',
	'priority': 420,
	'dataFileDependencies': ['SmallSignal.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'colorMap':'white_green_black',
		'colorDefault': ['#4FB99F'],
		'xlabel':'Time (s)',
		'ylabel':'$i_{{g}}$ (A)',
		'micro_ylabel':'$i_{{g}}$ ($\\mathregular{\\mu}$A)',
		'nano_ylabel':'$i_{{g}}$ (nA)',
		'pico_ylabel':'$i_{{g}}$ (pA)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Build Color Map
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=[], colorBarAxisLabel='')		

	# Adjust y-scale and y-axis labels 
	max_current = np.max(np.abs(np.array(deviceHistory[0]['Results']['ig_data'])))
	current_scale, ylabel = (1, plotDescription['plotDefaults']['ylabel']) if(max_current >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_ylabel']) if(max_current >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_ylabel']) if(max_current >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_ylabel'])))

	# Plot
	for i in range(len(deviceHistory)):
		for j in range(len(deviceHistory[i]['Results']['timestamps'])):
			line = ax.plot(np.array(deviceHistory[i]['Results']['timestamps'][j]) - min(deviceHistory[i]['Results']['timestamps'][0]),  np.array(deviceHistory[i]['Results']['ig_data'][j])*current_scale, color=colors[i], marker='o', markersize=2, linewidth=1)
		
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)	
			
	return (fig, (ax,))



