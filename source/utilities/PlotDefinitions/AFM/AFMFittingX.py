from utilities.MatplotlibUtility import *

plotDescription = {
	'plotCategory': 'device',
	'priority': 560,
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
	startTime = min(deviceHistory[0]['Results']['timestamps_device'])
	
	VxValues = np.array([])
	VxTimes = np.array([])
	
	# Plot
	for i in range(len(deviceHistory)):
		ax.set_prop_cycle(None)
		ax2.set_prop_cycle(None)
		line = ax.plot(np.array(deviceHistory[i]['Results']['timestamps_device']) - startTime, np.array(deviceHistory[i]['Results']['id_data'])*1e9)
		# ax2.plot([])
		# line = ax2.plot(np.array(deviceHistory[i]['Results']['timestamps_smu2']) - startTime, deviceHistory[i]['Results']['smu2_v1_data'], alpha=0.8)
		# line = ax2.plot(np.array(deviceHistory[i]['Results']['timestamps_smu2']) - startTime, deviceHistory[i]['Results']['smu2_v2_data'], alpha=0.8)
		
		VxValues = np.append(VxValues, deviceHistory[i]['Results']['smu2_v2_data'])
		VxTimes = np.append(VxTimes, np.array(deviceHistory[i]['Results']['timestamps_smu2']) - startTime)
		
		# if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			# setLabel(line, mode_parameters['legendLabels'][i])
	
	import scipy.signal
	
	timespan = max(VxTimes) - min(VxTimes)
	lombFs = np.linspace(1/timespan/10, 1/timespan*1000, 1000)
	pgram = scipy.signal.lombscargle(VxTimes, VxValues, lombFs, normalize=True)
	
	ax2.plot(lombFs, pgram, 'r')
	
	ax.set_ylabel('$I_D$ (nA)')
	ax.set_xlabel('Time (s)')
	ax2.set_ylabel('AFM Voltages (V)', rotation=-90, va='bottom', labelpad=5)
		
	return (fig, (ax,))

