from utilities.MatplotlibUtility import *

from utilities.PlotDefinitions.Noise.GateUnfiltered import filter60HzAndHarmonics


plotDescription = {
	'plotCategory': 'device',
	'priority': 770,
	'dataFileDependencies': ['NoiseCollection.json'],
	'plotDefaults': {
		'figsize':(3.125,2.5),

		'xlabel':'Time (s)',
		'ylabel':'$I_{{D}}$ (A)',
		'micro_ylabel':'$I_{{D}}$ ($\\mu$A)',
		'nano_ylabel':'$I_{{D}}$ (nA)',
		'pico_ylabel':'$I_{{D}}$ (pA)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	times = []
	Ids = []
	Igs = []
	for dh in deviceHistory:
		t = np.array(dh['Results']['timestamps'])
		t -= np.min(t)
		times.append(t)
		
		Ids.append(filter60HzAndHarmonics(np.array(dh['Results']['id_data']), t))
		Igs.append(filter60HzAndHarmonics(np.array(dh['Results']['ig_data']), t))
	
	# Adjust y-scale and y-axis labels 
	max_current = max(np.max(np.abs(Ids)), np.max(np.abs(Igs)))
	current_scale, ylabel = (1, plotDescription['plotDefaults']['ylabel']) if(max_current >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_ylabel']) if(max_current >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_ylabel']) if(max_current >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_ylabel'])))		
	
	# Plot	
	for i in range(len(times)):
		ax.plot(times[i], Ids[i]*current_scale, label='Drain Current', alpha=0.5*(1+1/len(deviceHistory)))
		
		if len(deviceHistory) == 1:
			ax.plot(times, Igs[i]*current_scale, label='Gate Current')
			ax.legend()
	
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)
	
	return (fig, (ax,))

