from utilities.MatplotlibUtility import *
import scipy.signal
import numpy as np


plotDescription = {
	'plotCategory': 'device',
	'priority': 750,
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
	
	Fsamp = 1/np.median(np.diff(times.flatten()))
	
	Ids = np.array([dh['Results']['id_data'] for dh in deviceHistory])
	Igs = np.array([dh['Results']['ig_data'] for dh in deviceHistory])
	
	Fs = np.logspace(np.log10(10),np.log10(1e4),200)
	
	lombId = scipy.signal.lombscargle(times.flatten(), Ids.flatten()-np.median(Ids), Fs)
	lombIg = scipy.signal.lombscargle(times.flatten(), Igs.flatten()-np.median(Igs), Fs)
	
	ax.loglog(Fs, lombId, label='Drain Current')
	ax.loglog(Fs, lombIg, label='Gate Current')
	
	ax.set_xlabel('Frequency [Hz]')
	ax.set_ylabel('Amplitude')
	# ax.legend()
	
	return (fig, (ax,))

