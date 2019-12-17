from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 440,
	'dataFileDependencies': ['RapidBias.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'automaticAxisLabels':False,
		'colorMap':'white_magenta_black',
		'colorDefault': ['#9F3285'],
		'xlabel':'Time (s)',
		'ylabel':'$V_{{DS}}$ (V)',
		'milli_ylabel':'$V_{{DS}}$ (mV)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Build Color Map
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=[], colorBarAxisLabel='')		
	
	# Adjust y-scale and y-axis labels 
	max_voltage = np.max(np.abs(np.array(deviceHistory[0]['Results']['vds_data'])))
	voltage_scale, ylabel = (1, plotDescription['plotDefaults']['ylabel']) if(max_voltage >= 1) else (1e3, plotDescription['plotDefaults']['milli_ylabel'])
	
	# Plot
	for i in range(len(deviceHistory)):
		line = ax.plot(np.array(deviceHistory[i]['Results']['timestamps']) - min(deviceHistory[i]['Results']['timestamps']),  np.array(deviceHistory[i]['Results']['vds_data'])*voltage_scale, color=colors[i], marker='o', markersize=2, linewidth=1)

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)	

	return (fig, (ax,))



