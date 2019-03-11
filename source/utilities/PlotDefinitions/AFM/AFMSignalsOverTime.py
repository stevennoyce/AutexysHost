from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'priority': 540,
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'xlabel':'Time (s)',
		'ylabel':'$I_D$ (nA)'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	ax2 = ax.twinx()
	startTime = min(deviceHistory[0]['Results']['timestamps_device'])
	
	times1 = np.array([dh['Results']['timestamps_device'] for dh in deviceHistory]) - startTime
	times2 = np.array([dh['Results']['timestamps_smu2'] for dh in deviceHistory]) - startTime
	
	Ids = np.array([dh['Results']['id_data'] for dh in deviceHistory])
	Igs = np.array([dh['Results']['ig_data'] for dh in deviceHistory])
	
	Vxs = np.array([dh['Results']['smu2_v1_data'] for dh in deviceHistory])
	Vys = np.array([dh['Results']['smu2_v2_data'] for dh in deviceHistory])
	
	# Plot
	ax2.plot([])
	ax2.plot(times2.flatten(), Vxs.flatten(), alpha=0.7)
	ax2.plot(times2.flatten(), Vys.flatten(), alpha=0.7)
	
	ax.plot(times1.flatten(), Ids.flatten()*1e9, '.')
	ax.plot(times1.flatten(), np.poly1d(np.polyfit(times1.flatten(), Ids.flatten(), 20))(times1.flatten())*1e9, c='#15659e')
	ax.plot(np.median(times1, 1), np.median(Ids, 1)*1e9, c='#40578c')
	
	ax.set_ylabel('$I_D$ (nA)')
	ax.set_xlabel('Time (s)')
	ax2.set_ylabel('AFM Voltages (V)', rotation=-90, va='bottom', labelpad=5)
		
	return (fig, (ax,))

