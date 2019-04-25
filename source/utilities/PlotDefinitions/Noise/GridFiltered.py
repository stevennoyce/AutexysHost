from utilities.MatplotlibUtility import *
import numpy as np

from utilities.PlotDefinitions.Noise.GateUnfiltered import extractNoiseMagnitude


plotDescription = {
	'plotCategory': 'device',
	'priority': 114,
	'dataFileDependencies': ['NoiseCollection.json'],
	'plotDefaults': {
		'figsize':(2.5,2.5),
		'includeOriginOnYaxis':True,
		'automaticAxisLabels':False,
		'includeFiltered': False,
		'colorMap':'white_blue_black',
		'colorDefault': ['#f2b134'],
		'xlabel':'$V_{{GS}}$ (V)',
		'ylabel':'$V_{{DS}}$ (V)',
		'micro_ylabel':'$\\Delta$ $I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'nano_ylabel':'$\\Delta$ $I_{{D}}$ (nA)',
		'pico_ylabel':'$\\Delta$ $I_{{D}}$ (pA)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Get noise magnitude vs. VGS and VDS
	gateVoltages, drainVoltages, currentAverages, unfilteredNoise, filteredNoise = extractNoiseMagnitude(deviceHistory, groupBy='drain')
	
	print(gateVoltages)
	print(drainVoltages)
	
	# Plot
	for i in range(len(drainVoltages)):
		extent = (gateVoltages[0][0], gateVoltages[0][-1], drainVoltages[0], drainVoltages[-1])
		line = ax.imshow(np.array(filteredNoise)*1e9, aspect='auto', origin='top', extent=extent)
	
	cbar = fig.colorbar(line, pad=0.015, aspect=50)
	cbar.set_label('$\Delta I_D$ (nA)', rotation=270, labelpad=8)
	
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])
	
	return (fig, (ax,))
	
