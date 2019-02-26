from utilities.MatplotlibUtility import *
from procedures.AFM_Control import *


plotDescription = {
	'plotCategory': 'device',
	'priority': 610,
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'colorMap':'plasma'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Build Color Map and Color Bar	
	colors = colorsFromMap(plotDescription['plotDefaults']['colorMap'], 0, 0.87, len(deviceHistory))['colors']
	
	Vxs = []
	Vys = []
	currents = []
	
	for i in range(len(deviceHistory)):
		current = np.array(deviceHistory[i]['Results']['ig_data'])
		
		xs = np.array(deviceHistory[i]['Results']['smu2_v2_data'])
		xs -= min(xs)
		
		Vxs.extend(list(xs))
		Vys.extend(deviceHistory[i]['Results']['smu2_v1_data'])
		currents.extend(current)
	
	Xs = -np.array(Vxs)/0.157
	Ys = np.array(Vys)/0.138
	
	Xs = Xs - np.min(Xs)
	Ys = Ys - np.min(Ys)
	
	# c, a, b = zip(*sorted(zip(np.array(currents)*1e9, Xs, Ys), reverse=True))
	c, a, b = zip(*zip(np.array(currents)*1e9, Xs, Ys))
	line = ax.scatter(a, b, c=c, cmap=plotDescription['plotDefaults']['colorMap'], alpha=0.6, marker='o', s=14)
	
	cbar = fig.colorbar(line, pad=0.015, aspect=50)
	cbar.set_label('Drain Current [nA]', rotation=270, labelpad=11)
	cbar.solids.set(alpha=1)
	
	ax.set_ylabel('Y Position ($\\mu$m)')
	ax.set_xlabel('X Position ($\\mu$m)')	
	
	return (fig, (ax,))


