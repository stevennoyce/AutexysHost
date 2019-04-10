from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 540,
	'dataFileDependencies': ['NoiseCollection.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'xlabel':'Time (s)',
		'ylabel':'I (nA)'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	times = np.array([dh['Results']['timestamps'] for dh in deviceHistory])
	
	Fs = 1/np.median(np.diff(times.flatten()))
	
	Ids = np.array([dh['Results']['id_data'] for dh in deviceHistory])
	Igs = np.array([dh['Results']['ig_data'] for dh in deviceHistory])
	
	
	
	ax.psd(Ids.flatten()*1e9, Fs=Fs, NFFT=2**15, noverlap=2**14-1, label='Drain Current')
	ax.psd(Igs.flatten()*1e9, Fs=Fs, NFFT=2**15, noverlap=2**14-1, label='Gate Current')
	
	ax.set_xscale('log')
	# ax.set_ylabel('$I_D$ (nA)')
	# ax.set_xlabel('Time (s)')
	ax.legend()
		
	return (fig, (ax,))

