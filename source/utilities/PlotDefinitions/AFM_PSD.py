from utilities.MatplotlibUtility import *
from procedures import AFM_Control as afm_ctrl
from utilities import AFMReader as afm_reader

import time
import numpy as np
import scipy.signal

plotDescription = {
	'plotCategory': 'device',
	'priority': 550,
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(4,3),
		'colorMap':'viridis'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None, showBackgroundAFMImage=False, interpolateNans=True):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	Xps = []
	Yps = []
	Ips = []
	
	for i in range(len(deviceHistory)):
		times = np.array(deviceHistory[i]['Results']['timestamps_smu2'])
		Xs = np.array(deviceHistory[i]['Results']['smu2_v2_data'])
		Ys = np.array(deviceHistory[i]['Results']['smu2_v1_data'])
		Is = np.array(deviceHistory[i]['Results']['id_data'])
		sampleSpacing = np.median(times[1:]-times[0:-1])
		samplingFrequency = 1/sampleSpacing
		
		frequencies, Xp = scipy.signal.welch(Xs, fs=samplingFrequency)
		frequencies, Yp = scipy.signal.welch(Ys, fs=samplingFrequency)
		frequencies, Ip = scipy.signal.welch(Is, fs=samplingFrequency)
		
		Xps.append(list(Xp))
		Yps.append(list(Yp))
		Ips.append(list(Ip))
		
		# ax.psd(Is, Fs=samplingFrequency)
	
	ax.plot(frequencies, 10*np.log10(np.mean(Xps, axis=0)**2), label='$V_X$')
	ax.plot(frequencies, 10*np.log10(np.mean(Yps, axis=0)**2), label='$V_Y$')
	ax.plot(frequencies, 10*np.log10(np.mean(Ips, axis=0)**2), label='$I_D$')
	
	print('Sum is ', np.sum(np.abs(np.mean(Xps, axis=0)))*frequencies[1])
	
	ax.legend()
	ax.set_xlabel('Frequency [Hz]')
	ax.set_ylabel('Power Spectral Density [dB/Hz]')
	
	fig.tight_layout()
		
	return (fig, (ax,))


if(__name__=='__main__'):
	pass
	

