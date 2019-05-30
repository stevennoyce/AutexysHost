from utilities.MatplotlibUtility import *
import numpy as np

from utilities.PlotDefinitions.Noise.GateUnfiltered import extractNoiseMagnitude

plotDescription = {
	'plotCategory': 'device',
	'priority': 713,
	'dataFileDependencies': ['NoiseCollection.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'colorMap':'white_blue_black',
		'colorDefault': ['#f2b134'],
		
		'xlabel':'$V_{{GS}}$ (V)',
		'ylabel':'SNR'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Get noise magnitude vs. VGS and VDS
	gateVoltages, drainVoltages, currentAverages, unfilteredNoise, filteredNoise = extractNoiseMagnitude(deviceHistory, groupBy='drain')
	
	# Signal is raw current of transfer curve, analyte is fully controlling the gate
	signal = np.array(currentAverages)
	
	# Signal is the change in drain current from a modulation on gate voltage, analyte is causing variation around an operating point
	signal = np.gradient(currentAverages, axis=1)
	
	# Signal is a percentage change in drain current for a given gate voltage modulation
	signal = np.gradient(currentAverages, axis=1)/np.array(currentAverages)
	
	SNRs = np.abs(signal)/np.array(filteredNoise)
	
	# Build Color Map and Color Bar
	colors = setupColors(fig, len(drainVoltages), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.1, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=['$V_{{DS}} = {:.2g}$ V'.format(drainVoltages[-1]), '', '$V_{{DS}} = {:.2g}$ V'.format(drainVoltages[0])], colorBarAxisLabel='')
	
	# Plot
	for i in range(len(drainVoltages)):
		line = ax.semilogy(gateVoltages[i], SNRs[i], color=colors[i], marker='o', markersize=4, linewidth=1, linestyle=None)
	
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOriginOnYaxis'], stretchfactor=1.05)
	
	return (fig, (ax,))

	
