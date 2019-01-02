from utilities.MatplotlibUtility import *

import lmfit


plotDescription = {
	'plotCategory': 'device',
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'xlabel':'Time',
		'ylabel':'Current'
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
	
	fft = np.fft.rfft(values)
	fft /= len(fft)
	
	offset = fft[0]
	fft[0] = 0
	maxFpos = np.argsort(np.abs(fft))[-1]
	Fs = np.fft.rfftfreq(len(values), d=(max(times) - min(times))/len(times))
	maxF = Fs[maxFpos]
	phaseAngle = np.angle(fft[maxFpos])
	amplitude = np.abs(fft[maxFpos])
	
	print('Frequency is: {}'.format(maxF))
	print('Period is: {}'.format(1/maxF))
	params['phase'].value = phaseAngle
	params['period'].value = 1/maxF/2*1.1
	
	# params['phase'].min = 0
	# params['phase'].max = 2*np.pi
	
	if True: # Fit only period first
		for param in params:
			params[param].vary = False
		# params['phase'].vary = True
		params['period'].vary = True
		
		result = model.fit(values, params, times=times)
		# params['phase'].value  = result.best_values['phase']
		params['period'].value = result.best_values['period']
		
		for param in params:
			params[param].vary = True
	
	# result = model.fit(values, params, times=times)
	
	return result

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
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
	
	# VxFit = fitTriangleWave(VxTimes, VxValues)
	# ax2.plot(VxTimes, VxFit.init_fit, '--', label='Guess')
	# ax2.plot(VxTimes, VxFit.best_fit, label='Fit')
	
	import scipy.signal
	
	timespan = max(VxTimes) - min(VxTimes)
	lombFs = np.linspace(1/timespan/10, 1/timespan*1000, 1000)
	pgram = scipy.signal.lombscargle(VxTimes, VxValues, lombFs, normalize=True)
	
	ax2.plot(lombFs, pgram, 'r')
	
	ax.set_ylabel('$I_D$ (nA)')
	ax.set_xlabel('Time (s)')
	ax2.set_ylabel('AFM Voltages (V)', rotation=-90, va='bottom', labelpad=5)
	
	
	# Add Legend and save figure
	adjustAndSaveFigure(fig, 'FullSubthresholdCurves', mode_parameters)
	
	return (fig, ax)

