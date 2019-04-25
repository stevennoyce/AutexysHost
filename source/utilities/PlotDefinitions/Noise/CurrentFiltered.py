from utilities.MatplotlibUtility import *
import numpy as np

from utilities.PlotDefinitions.Noise.GateUnfiltered import extractNoiseMagnitude



plotDescription = {
	'plotCategory': 'device',
	'priority': 716,
	'dataFileDependencies': ['NoiseCollection.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'colorMap':'white_orange_black',
		'colorDefault': ['#ee7539'],
		
		'xlabel':'$I_{{D}}$ (A)',
		'micro_xlabel':'$I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'nano_xlabel':'$I_{{D}}$ (nA)',
		'pico_xlabel':'$I_{{D}}$ (pA)',
		
		'ylabel':'$\\Delta$  $I_{{D}}$ (A)',
		'micro_ylabel':'$\\Delta$ $I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'nano_ylabel':'$\\Delta$ $I_{{D}}$ (nA)',
		'pico_ylabel':'$\\Delta$ $I_{{D}}$ (pA)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Get noise magnitude vs. VGS and VDS
	gateVoltages, drainVoltages, currentAverages, unfilteredNoise, filteredNoise = extractNoiseMagnitude(deviceHistory, groupBy='gate')
	
	# Adjust scale and axis labels 
	max_noise = np.max(np.abs(np.array(unfilteredNoise)))
	max_current = np.max(np.abs(np.array(currentAverages)))
	noise_scale, ylabel   = (1, plotDescription['plotDefaults']['ylabel']) if(max_noise >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_ylabel']) if(max_noise >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_ylabel']) if(max_noise >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_ylabel'])))		
	current_scale, xlabel = (1, plotDescription['plotDefaults']['xlabel']) if(max_current >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_xlabel']) if(max_current >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_xlabel']) if(max_current >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_xlabel'])))		
	
	# Build Color Map and Color Bar
	colors = setupColors(fig, len(gateVoltages), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.1, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=['$V_{{GS}} = {:.2g}$ V'.format(gateVoltages[-1]), '', '$V_{{GS}} = {:.2g}$ V'.format(gateVoltages[0])], colorBarAxisLabel='')

	# Plot	
	for i in range(len(gateVoltages)):
		line = ax.plot(np.array(currentAverages[i]) * current_scale, np.array(filteredNoise[i]) * noise_scale, color=colors[i], marker='o', markersize=4, linewidth=1, linestyle=None)
		
	# Set Axis Labels
	axisLabels(ax, x_label=xlabel, y_label=ylabel)
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOriginOnYaxis'], stretchfactor=1.05)
	
	return (fig, (ax,))
