from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'colorMap':'plasma'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
	# Build Color Map
	colors = colorsFromMap(plotDescription['plotDefaults']['colorMap'], 0, 0.87, len(deviceHistory))['colors']
	# E07N is a sister device, E22N_10000 is another with 40nm device, 5 fin devices E33N E64N, Bigger cavity E27N and E27P 5 fin
	# Bonded devices E07N_10000 (pins 7-8), E08N_10000 (pins 9-10), E22N_10000 (pins 11-12), E27N_10000 (pins 13-14), E33N_10000 (pins 15-16)
	# CNT devices that could be used for AFM: C127V2-3 C127X15-16
	# Plot
	for i in range(len(deviceHistory)):
		current = np.array(deviceHistory[i]['Results']['id_data'])
		currentLinearFit = np.polyval(np.polyfit(range(len(current)), current, 1), range(len(current)))
		currentLinearized = current - currentLinearFit
		currentLinearized = currentLinearized - np.median(currentLinearized)
		
		Vxs = np.array(deviceHistory[i]['Results']['smu2_v2_data'])
		Xs = -Vxs/0.157
		Xs = Xs - np.min(Xs)
		
		line = ax.plot(Xs, currentLinearized*1e9, color=colors[i], alpha=0.01+(1.0/(len(deviceHistory)+1))**0.2)
		
		# if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			# setLabel(line, mode_parameters['legendLabels'][i])
	
	ax.set_ylabel('$I_D$ (nA)')
	ax.set_xlabel('X Position ($\mu$m)')
	
	# Add Legend and save figure
	adjustAndSaveFigure(fig, 'AFMdeviationsVsX', mode_parameters)
	
	return (fig, ax)

