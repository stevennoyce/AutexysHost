from utilities.MatplotlibUtility import *

import lmfit


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
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
	startTime = min(deviceHistory[0]['Results']['timestamps_device'])
	
	startTimeDiffs = []
	
	# Plot
	for history in deviceHistory:
		startTime1 = min(history['Results']['timestamps_device'])
		startTime2 = min(history['Results']['timestamps_smu2'])
		
		startTimeDiffs.append(startTime2 - startTime1)
	
	ax.plot(startTimeDiffs)
	
	ax.set_ylabel('Start Time Diffs [s]')
	ax.set_xlabel('Line Number [#]')
	
	# Add Legend and save figure
	adjustAndSaveFigure(fig, 'FullSubthresholdCurves', mode_parameters)
	
	return (fig, ax)

