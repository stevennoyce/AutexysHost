from utilities.MatplotlibUtility import *

import scipy.signal

plotDescription = {
	'plotCategory': 'device',
	'priority': 550,
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'xlabel':'Time',
		'ylabel':'Current'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	ax2 = ax.twinx()
	
	VxValues = np.array([])
	VxTimes = np.array([])
	
	# Plot
	for i in range(len(deviceHistory)):
		
		timestamps = np.array(deviceHistory[i]['Results']['timestamps_smu2'])
		timestamps -= min(timestamps)
		
		Vxs = np.array(deviceHistory[i]['Results']['smu2_v2_data'])#+i*0.01
		
		line1 = ax.plot(timestamps, Vxs)
		
		Vxsp = scipy.signal.savgol_filter(Vxs, 11, 2, 1)
		
		# line2 = ax2.plot(timestamps[1:], Vxs[1:]-Vxs[0:-1])
		line2 = ax2.plot(timestamps, Vxsp)
		
		# VxValues = np.append(VxValues, deviceHistory[i]['Results']['smu2_v2_data'])
		# VxTimes = np.append(VxTimes, np.array(deviceHistory[i]['Results']['timestamps_smu2']) - startTime)
	
	ax.set_ylabel('AFM X Voltage [V]')
	ax.set_xlabel('Time (s)')
	
	return (fig, (ax,))

