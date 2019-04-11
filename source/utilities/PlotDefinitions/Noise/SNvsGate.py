from utilities.MatplotlibUtility import *
import scipy.signal
import numpy as np


plotDescription = {
	'plotCategory': 'device',
	'priority': 200,
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
	
		dt = np.median(np.diff(times.flatten()))
		
		Ids = np.array(dh['Results']['id_data'])
		Igs = np.array(dh['Results']['ig_data'])
		
		IdFs = np.fft.rfftfreq(Ids.size, d=dt)
		IdXs = np.fft.rfft(Ids.flatten())
		IdAs = np.abs(IdXs)*dt
		
		ax.loglog(IdFs[1:], IdAs[1:], '.-', label='Drain Current')
		
		minAmbientIndex = np.argmax(IdFs > 50)
		ambientNoiseIndexes = np.argpartition(IdAs[minAmbientIndex:], -100)[-100:] + minAmbientIndex
		ambientNoiseFs = IdFs[ambientNoiseIndexes]
		
		distances = np.abs(ambientNoiseFs - np.round(ambientNoiseFs/60)*60)
		ambientNoiseIndexes = ambientNoiseIndexes[distances < 3*IdFs[1]]
		
		ambientNoiseFs = IdFs[ambientNoiseIndexes]
		ambientNoiseAs = IdAs[ambientNoiseIndexes]
		
		# for f in ambientNoiseFs:
		# 	distance = abs(f - round(f/60)*60)
		# 	if distance < 3*IdFs[1]:
		# 		print(distance)
		
		if len(deviceHistory) == 1:
			IgFs = np.fft.rfftfreq(Igs.size, d=dt)
			IgXs = np.fft.rfft(Igs.flatten())
			IgAs = np.abs(IgXs)*dt
			ax.semilogx(IgFs[1:], IgAs[1:], '.-', label='Gate Current')
			
			ax.semilogx(ambientNoiseFs, ambientNoiseAs, 'o', label='Ambient Noise')
	
	ax.set_ylabel('Current Noise [A]')
	ax.set_xlabel('Frequency [Hz]')
	ax.legend()
	
	return (fig, (ax,))

