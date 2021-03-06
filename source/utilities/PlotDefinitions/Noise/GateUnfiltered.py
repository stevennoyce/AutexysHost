from utilities.MatplotlibUtility import *
import numpy as np

import scipy.signal

plotDescription = {
	'plotCategory': 'device',
	'priority': 713,
	'dataFileDependencies': ['NoiseCollection.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'colorMap':'white_blue_black',
		'colorDefault': ['#f2b134'],
		
		'xlabel':'$V_{{GS}}$ (V)',
		'ylabel':'$\\Delta$ $I_{{D}}$ (A)',
		'micro_ylabel':'$\\Delta$ $I_{{D}}$ ($\\mathregular{\\mu}$A)',
		'nano_ylabel':'$\\Delta$ $I_{{D}}$ (nA)',
		'pico_ylabel':'$\\Delta$ $I_{{D}}$ (pA)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Get noise magnitude vs. VGS and VDS
	gateVoltages, drainVoltages, currentAverages, unfilteredNoise, filteredNoise = extractNoiseMagnitude(deviceHistory, groupBy='drain')
	
	# Adjust y-scale and y-axis labels 
	max_noise = np.max(np.abs(np.array(unfilteredNoise)))
	noise_scale, ylabel   = (1, plotDescription['plotDefaults']['ylabel']) if(max_noise >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_ylabel']) if(max_noise >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_ylabel']) if(max_noise >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_ylabel'])))		
	
	# Build Color Map and Color Bar
	colors = setupColors(fig, len(drainVoltages), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.1, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=['$V_{{DS}} = {:.2g}$ V'.format(drainVoltages[-1]), '', '$V_{{DS}} = {:.2g}$ V'.format(drainVoltages[0])], colorBarAxisLabel='')

	# Plot	
	for i in range(len(drainVoltages)):
		line = ax.plot(gateVoltages[i], np.array(unfilteredNoise[i]) * noise_scale, color=colors[i], marker='o', markersize=4, linewidth=1, linestyle=None)
	
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)
	
	# Adjust Y-lim (if desired)
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOriginOnYaxis'], stretchfactor=1.05)
	
	return (fig, (ax,))

def noiseFromData(data):
	return 4*np.std(data) # 95% interval

def noiseFromData(data):
    data = np.array(data)
    data = data.flatten()
    
    windowSize = 50
    slidingWindow = np.arange(windowSize)[None, :] + windowSize*np.arange(data.size//windowSize)[:, None]
    stds = np.std(data[slidingWindow], axis=1)
    
    return 4*np.median(stds) # 95% interval

def filter60HzAndHarmonics(Id, timestamps):
	Id = np.array(Id)
	Id = Id - np.poly1d(np.polyfit(timestamps, Id, 3))(timestamps)
	timestamps = np.array(timestamps)
	
	dt = np.median(np.diff(timestamps))
	Fsamp = 1/dt
	FNyquist = Fsamp/2
	Fs = np.fft.rfftfreq(Id.size, d=dt)
	Xs = np.fft.rfft(Id)
	As = np.abs(Xs)*dt
	
	minAmbientIndex = np.argmax(Fs > 50)
	ambientNoiseIndexes = np.argpartition(As[minAmbientIndex:], -100)[-100:] + minAmbientIndex
	ambientNoiseFs = Fs[ambientNoiseIndexes]
	
	distances = np.abs(ambientNoiseFs - np.round(ambientNoiseFs/60)*60)
	maxDistance = np.clip(3*Fs[1], 2, 8)
	ambientNoiseIndexes = ambientNoiseIndexes[distances < maxDistance]
	
	ambientNoiseFs = Fs[ambientNoiseIndexes]
	ambientNoiseAs = As[ambientNoiseIndexes]
	
	for i in np.sort(ambientNoiseIndexes):
		Xs[i] = Xs[i-1]
	
	IdFiltered = np.fft.irfft(Xs)
	
	# print('FNyquist is', FNyquist)
	
	b, a = scipy.signal.butter(1, min(60, FNyquist/2)/FNyquist, btype='highpass', analog=False) #, fs=Fsamp
	IdFiltered = np.mean(IdFiltered) + scipy.signal.filtfilt(b, a, IdFiltered)
	
	# IdFiltered = scipy.signal.filtfilt(b, a, IdFiltered)
	# IdFiltered = Id - np.poly1d(np.polyfit(timestamps, Id, 3))(timestamps)
	
	return IdFiltered

def extractNoiseMagnitude(deviceHistory, groupBy=None):
	# === Extract noise magnitude from data ===
	gateVoltages = []
	drainVoltages = []
	currentAverages = []
	unfilteredNoise = []
	filteredNoise = []
	for i in range(len(deviceHistory)):
		vgs = deviceHistory[i]['runConfigs']['NoiseCollection']['gateVoltage']
		vds = deviceHistory[i]['runConfigs']['NoiseCollection']['drainVoltage']
		timestamps = deviceHistory[i]['Results']['timestamps']
		id_unfiltered = deviceHistory[i]['Results']['id_data']
		id_filtered = filter60HzAndHarmonics(id_unfiltered, timestamps) 
		
		gateVoltages.append(vgs)
		drainVoltages.append(vds)
		unfilteredNoise.append(noiseFromData(id_unfiltered))
		filteredNoise.append(noiseFromData(id_filtered))
		currentAverages.append(np.mean(id_unfiltered))
		
	# === Group data into sub-arrays ===
	gateVoltages_sorted = []
	drainVoltages_sorted = []
	currentAverages_sorted = []
	unfilteredNoise_sorted = []
	filteredNoise_sorted = []
	if(groupBy == 'drain'):
		# Get a set of unique drainVoltages, and group other arrays accordingly
		for i in range(len(gateVoltages)):	
			if(drainVoltages[i] in drainVoltages_sorted):
				index = drainVoltages_sorted.index(drainVoltages[i])
				gateVoltages_sorted[index].append(gateVoltages[i])
				currentAverages_sorted[index].append(currentAverages[i])
				unfilteredNoise_sorted[index].append(unfilteredNoise[i])
				filteredNoise_sorted[index].append(filteredNoise[i])
			else:
				drainVoltages_sorted.append(drainVoltages[i])
				gateVoltages_sorted.append([gateVoltages[i]])
				currentAverages_sorted.append([currentAverages[i]])
				unfilteredNoise_sorted.append([unfilteredNoise[i]])
				filteredNoise_sorted.append([filteredNoise[i]])
		
		# Sort outer-level arrays by V_DS
		drainVoltages_sorted, gateVoltages_sorted, currentAverages_sorted, unfilteredNoise_sorted, filteredNoise_sorted = (list(elem) for elem in zip(*sorted(zip(drainVoltages_sorted, gateVoltages_sorted, currentAverages_sorted, unfilteredNoise_sorted, filteredNoise_sorted))))	
		for i in range(len(gateVoltages_sorted)):
			# Sort inner-level arrays by V_GS
			gateVoltages_sorted[i], currentAverages_sorted[i], unfilteredNoise_sorted[i], filteredNoise_sorted[i] = (list(elem) for elem in zip(*sorted(zip(gateVoltages_sorted[i], currentAverages_sorted[i], unfilteredNoise_sorted[i], filteredNoise_sorted[i]))))	
	elif(groupBy == 'gate'):	
		# Get a set of unique gateVoltages, and group other arrays accordingly
		for i in range(len(gateVoltages)):	
			if(gateVoltages[i] in gateVoltages_sorted):
				index = gateVoltages_sorted.index(gateVoltages[i])
				drainVoltages_sorted[index].append(drainVoltages[i])
				currentAverages_sorted[index].append(currentAverages[i])
				unfilteredNoise_sorted[index].append(unfilteredNoise[i])
				filteredNoise_sorted[index].append(filteredNoise[i])
			else:
				gateVoltages_sorted.append(gateVoltages[i])
				drainVoltages_sorted.append([drainVoltages[i]])
				currentAverages_sorted.append([currentAverages[i]])
				unfilteredNoise_sorted.append([unfilteredNoise[i]])
				filteredNoise_sorted.append([filteredNoise[i]])
		
		# Sort outer-level arrays by V_GS
		gateVoltages_sorted, drainVoltages_sorted, currentAverages_sorted, unfilteredNoise_sorted, filteredNoise_sorted = (list(elem) for elem in zip(*sorted(zip(gateVoltages_sorted, drainVoltages_sorted, currentAverages_sorted, unfilteredNoise_sorted, filteredNoise_sorted))))	
		for i in range(len(gateVoltages_sorted)):
			# Sort inner-level arrays by V_DS
			drainVoltages_sorted[i], currentAverages_sorted[i], unfilteredNoise_sorted[i], filteredNoise_sorted[i] = (list(elem) for elem in zip(*sorted(zip(drainVoltages_sorted[i], currentAverages_sorted[i], unfilteredNoise_sorted[i], filteredNoise_sorted[i]))))	
	else:
		# Don't group into sub-arrays
		gateVoltages_sorted = gateVoltages
		drainVoltages_sorted = drainVoltages
		currentAverages_sorted = currentAverages
		unfilteredNoise_sorted = unfilteredNoise
		filteredNoise_sorted = filteredNoise
		
	return gateVoltages_sorted, drainVoltages_sorted, currentAverages_sorted, unfilteredNoise_sorted, filteredNoise_sorted
	
