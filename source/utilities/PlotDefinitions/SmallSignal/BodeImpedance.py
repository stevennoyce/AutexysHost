from utilities.MatplotlibUtility import *



plotDescription = {
	'name': 'Imepdance Bode Plot',
	'plotCategory': 'device',
	'priority': 450,
	'dataFileDependencies': ['SmallSignal.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'colorMap':'white_blue_black',
		'colorDefault': ['#1f77b4'],
		'xlabel':'Frequency (Hz)',
		'ylabel':'|$\\dfrac{{v_{{ds}}}}{{i_{{d}}}}$| ($\\mathregular{\\Omega}$)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Build Color Map
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=False, colorBarTicks=[0,0.6,1], colorBarTickLabels=[], colorBarAxisLabel='')		

	# Function for calculating frequnecy from a periodic signal
	def extract_frequency(signal, timestamps):
		peak_max = np.max(signal)
		peak_min = np.min(signal)
		dc_offset = (peak_max + peak_min) / 2
		crossing_detected = lambda a, b, threshold: (((a <= threshold) and (b >= threshold)) or ((a >= threshold) and (b <= threshold)))
		
		center_crossings = []
		peak_detected = False
		for i in range(len(signal)-1):
			if(peak_detected):
				if(crossing_detected(signal[i], signal[i+1], dc_offset)):
					center_crossings.append(timestamps[i])
					peak_detected = False
			else:
				peak_detected = ((signal[i] >= (peak_max + dc_offset)/2) or (signal[i] <= (peak_min + dc_offset)/2))
		
		mean_time_between_center_crossings = np.mean([center_crossings[i+1]-center_crossings[i] for i in range(len(center_crossings)-1)])
		return 1/mean_time_between_center_crossings
		
	# Plot
	total_freqencies = []
	total_impedances = []
	for i in range(len(deviceHistory)):
		number_of_frequencies = len(deviceHistory[i]['Results']['timestamps'])
		
		frequencies    = [extract_frequency(deviceHistory[i]['Results']['vds_data'][j], deviceHistory[i]['Results']['timestamps'][j]) 					for j in range(number_of_frequencies)]
		vds_amplitudes = [(max(deviceHistory[i]['Results']['vds_data'][j]) - min(deviceHistory[i]['Results']['vds_data'][j])) 							for j in range(number_of_frequencies)]
		id_amplitudes  = [(np.percentile(deviceHistory[i]['Results']['id_data'][j], 98) - np.percentile(deviceHistory[i]['Results']['id_data'][j], 2))  for j in range(number_of_frequencies)]
		impedances     = [(vds_amplitudes[j]/id_amplitudes[j]) 																							for j in range(number_of_frequencies)]
		
		total_freqencies.append(frequencies)
		total_impedances.append(impedances)
		
		line = ax.plot(frequencies, impedances, color=colors[i], marker='s', markersize=4, linewidth=2)
	
	# Set Axis Logarithmic Scales
	ax.set_xscale('log')
	ax.set_yscale('log')
	ax.set_xlim(right=np.max(total_freqencies)*5, left=np.min(total_freqencies)/5)
	ax.set_ylim(top=np.max(total_impedances)*15, bottom=np.min(total_impedances)/15)
				
	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])	
			
	return (fig, (ax,))



