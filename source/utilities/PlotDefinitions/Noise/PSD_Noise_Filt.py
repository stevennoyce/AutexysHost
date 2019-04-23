from utilities.MatplotlibUtility import *

from utilities.PlotDefinitions.Noise.GateUnfiltered import filter60HzAndHarmonics


plotDescription = {
	'plotCategory': 'device',
	'priority': 740,
	'dataFileDependencies': ['NoiseCollection.json'],
	'plotDefaults': {
		'figsize':(3.125,2.5),
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	for dh in deviceHistory:
		times = np.array(dh['Results']['timestamps'])
		
		Fs = 1/np.median(np.diff(times.flatten()))
		
		Ids = filter60HzAndHarmonics(np.array(dh['Results']['id_data']), times)
		Igs = filter60HzAndHarmonics(np.array(dh['Results']['ig_data']), times)
		
		NFFT = min(2**14, 2**int(np.log2(times.size/4)))
		
		if len(deviceHistory) == 1:
			ax.psd(Ids.flatten()*1e9, Fs=Fs, NFFT=NFFT, noverlap=NFFT//2-1, label='Drain Current')
			ax.psd(Igs.flatten()*1e9, Fs=Fs, NFFT=NFFT, noverlap=NFFT//2-1, label='Gate Current')
			ax.legend()
		else:
			ax.psd(Ids.flatten()*1e9, Fs=Fs, NFFT=NFFT, noverlap=NFFT//2-1, label='Drain Current')
	
	ax.set_xscale('log')
		
	return (fig, (ax,))

