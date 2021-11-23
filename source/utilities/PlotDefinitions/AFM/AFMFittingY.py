from utilities.MatplotlibUtility import *

plotDescription = {
	'plotCategory': 'device',
	'priority': 570,
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(5,4),
	},
}

def triangleSine(x):
	coefficients = [(-1)**i*(2*i+1)**(-2)*np.sin((2*i+1)*x) for i in range(15)]
	wave = np.sum(coefficients, axis=0)
	return wave/np.max(wave)

def triangleSinWave(times, amplitude, period, phase, offset):
	return offset + amplitude*triangleSine(2*np.pi*(times - phase)/period)

def triangleCosWave(times, amplitude, period, phase, offset):
	return triangleSinWave(times, amplitude, period, phase - period/4, offset)

def fitTriangleWave(times, values):
	import lmfit
	model = lmfit.Model(triangleCosWave)
	
	values = np.array(values)
	minTime = np.min(times)
	times = np.array(times) - minTime
	
	slopes = np.abs(values[1:]-values[0:-1])/((max(times)-min(times))/len(times))
	slope = np.mean(slopes)
	
	params = model.make_params()
	
	params['amplitude'].value = (np.max(values) - np.min(values))/2
	params['period'].value = 4*params['amplitude'].value/slope
	params['offset'].value = np.mean(values)
	params['phase'].value = (1-(values[0] - np.min(values))/(params['amplitude'].value*2))/(params['period'].value/2)
	
#     params['phase'].min = 0
	
	if False: # Fit only phase first
		for param in params:
			params[param].vary = False
		params['phase'].vary = True

		result = model.fit(values, params, times=times)
		params['phase'].value = result.best_values['phase']

		for param in params:
			params[param].vary = True
	
	result = model.fit(values, params, times=times)
	
	return result

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	ax2 = ax.twinx()
	startTime = min(deviceHistory[0]['Results']['timestamps_device'])
	
	VyValues = np.array([])
	VyTimes = np.array([])
	
	# Plot
	for i in range(len(deviceHistory)):
		ax.set_prop_cycle(None)
		ax2.set_prop_cycle(None)
		line = ax.plot(np.array(deviceHistory[i]['Results']['timestamps_device']) - startTime, np.array(deviceHistory[i]['Results']['id_data'])*1e9)
		ax2.plot([])
		line = ax2.plot(np.array(deviceHistory[i]['Results']['timestamps_smu2']) - startTime, deviceHistory[i]['Results']['smu2_v1_data'], alpha=0.8)
		line = ax2.plot(np.array(deviceHistory[i]['Results']['timestamps_smu2']) - startTime, deviceHistory[i]['Results']['smu2_v2_data'], alpha=0.8)
		
		VyValues = np.append(VyValues, deviceHistory[i]['Results']['smu2_v1_data'])
		VyTimes = np.append(VyTimes, np.array(deviceHistory[i]['Results']['timestamps_smu2']) - startTime)
		
		# if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			# setLabel(line, mode_parameters['legendLabels'][i])
	
	VyFit = fitTriangleWave(VyTimes, VyValues)
	ax2.plot(VyTimes, VyFit.init_fit, '--', label='Guess')
	ax2.plot(VyTimes, VyFit.best_fit, label='Fit')
	
	ax.set_ylabel('$I_D$ (nA)')
	ax.set_xlabel('Time (s)')
	ax2.set_ylabel('AFM Voltages (V)', rotation=-90, va='bottom', labelpad=5)
	
	return (fig, (ax,))

