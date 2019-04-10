from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 300,
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
	
	Ids = np.array([dh['Results']['id_data'] for dh in deviceHistory])
	Igs = np.array([dh['Results']['ig_data'] for dh in deviceHistory])
	
	dt = np.median(np.diff(times.flatten()))
	IdFs = np.fft.rfftfreq(Ids.size, d=dt)
	IdXs = np.fft.rfft(Ids.flatten())
	IdAs = np.abs(IdXs)*dt
	
	IgFs = np.fft.rfftfreq(Igs.size, d=dt)
	IgXs = np.fft.rfft(Igs.flatten())
	IgAs = np.abs(IgXs)*dt
	
	minAmbientIndex = np.argmax(IdFs > 50)
	ambientNoiseIndexes = np.argpartition(IdAs[minAmbientIndex:], -100)[-100:] + minAmbientIndex
	ambientNoiseFs = IdFs[ambientNoiseIndexes]
	
	distances = np.abs(ambientNoiseFs - np.round(ambientNoiseFs/60)*60)
	ambientNoiseIndexes = ambientNoiseIndexes[distances < 3*IdFs[1]]
	
	ambientNoiseFs = IdFs[ambientNoiseIndexes]
	ambientNoiseAs = IdAs[ambientNoiseIndexes]
	
	for i in np.sort(ambientNoiseIndexes):
		IdXs[i] = IdXs[i-1]
	
	IdsNew = np.fft.irfft(IdXs)
	
	ax.plot(times.flatten(), IdsNew.flatten()*1e9, '.-', label='Drain Current')
	ax.plot(times.flatten(), Igs.flatten()*1e9, '.-', label='Gate Current')
	
	ax.set_ylabel('$I_D$ (nA)')
	ax.set_xlabel('Time (s)')
	ax.legend()
	
	return (fig, (ax,))

