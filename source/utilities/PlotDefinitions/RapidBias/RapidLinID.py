from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 610,
	'dataFileDependencies': ['RapidBias.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'colorMap':'white_blue_black',
		'colorDefault': ['#1f77b4'],
		'xlabel':'Time (s)',
		'micro_ylabel':'$I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'nano_ylabel':'$I_{{D}}$ (nA)',
		'neg_micro_ylabel':'$-I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'neg_nano_ylabel':'$-I_{{D}}$ (nA)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Build Color Map
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=[], colorBarAxisLabel='')		

	# Adjust y-scale and y-axis labels 
	max_current = np.max(np.abs(np.array(deviceHistory[0]['Results']['id_data'])))
	current_scale, ylabel = (1e6, plotDescription['plotDefaults']['micro_ylabel']) if(max_current >= 1e-6) else (1e9, plotDescription['plotDefaults']['nano_ylabel'])
	
	# If first segment of device history is mostly negative current, flip data
	if((len(deviceHistory) > 0) and ((np.array(deviceHistory[0]['Results']['id_data']) < 0).sum() > (np.array(deviceHistory[0]['Results']['id_data']) >= 0).sum())):
		deviceHistory = scaledData(deviceHistory, 'Results', 'id_data', -1)
		ylabel = plotDescription['plotDefaults']['neg_micro_ylabel'] if(max_current >= 1e-6) else (plotDescription['plotDefaults']['neg_nano_ylabel'])

	# Plot
	for i in range(len(deviceHistory)):
		line = ax.plot(np.array(deviceHistory[i]['Results']['timestamps']) - min(deviceHistory[i]['Results']['timestamps']),  np.array(deviceHistory[i]['Results']['id_data'])*current_scale, color=colors[i], marker='o', markersize=2, linewidth=1)
				
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)	
			
	return (fig, (ax,))



