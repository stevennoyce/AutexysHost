from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 100,
	'dataFileDependencies': ['NoiseCollection.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'xlabel':'Time (s)',
		'ylabel':'I (nA)'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	for dh in deviceHistory:
		times = np.array(dh['Results']['timestamps'])
		times -= np.min(times)
		
		Ids = np.array(dh['Results']['id_data'])
		Igs = np.array(dh['Results']['ig_data'])
		
		ax.plot(times, Ids*1e9, label='Drain Current', alpha=0.5*(1+1/len(deviceHistory)))
		
		if len(deviceHistory) == 1:
			ax.plot(times, Igs*1e9, label='Gate Current')
			ax.legend()
	
	ax.set_ylabel('$I_D$ (nA)')
	ax.set_xlabel('Time (s)')
	
	return (fig, (ax,))

