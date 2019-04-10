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
	
	times = np.array([dh['Results']['timestamps'] for dh in deviceHistory])
	
	dt = np.median(np.diff(times.flatten()))
	
	Ids = np.array([dh['Results']['id_data'] for dh in deviceHistory])
	Igs = np.array([dh['Results']['ig_data'] for dh in deviceHistory])
	
	IdFs = np.fft.rfftfreq(Ids.size, d=dt)
	IdXs = np.fft.rfft(Ids.flatten())
	IdAs = np.abs(IdXs)*dt
	
	ax.semilogx(IdFs[1:], IdAs[1:], '.-', label='Drain Current')
	
	IgFs = np.fft.rfftfreq(Igs.size, d=dt)
	IgXs = np.fft.rfft(Igs.flatten())
	IgAs = np.abs(IgXs)*dt
	
	ax.semilogx(IgFs[1:], IgAs[1:], '.-', label='Gate Current')
	
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
			
	print(distances[distances < 3*IdFs[1]])
	
	ax.semilogx(ambientNoiseFs, ambientNoiseAs, 'o', label='Ambient Noise')
	
	ax.set_ylabel('Current Noise [A]')
	ax.set_xlabel('Frequency [Hz]')
	ax.legend()
	
	return (fig, (ax,))

