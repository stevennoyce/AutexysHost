from utilities.MatplotlibUtility import *
from procedures import AFM_Control as afm_ctrl
from utilities import AFMReader as afm_reader
#from utilities import IgorReader as afm_reader

#import os
#import glob
#from datetime import datetime

plotDescription = {
	'plotCategory': 'device',
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'colorMap':'viridis'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
	# Get X/Y limits
	Vxs = []
	Vys = []
	for i in range(len(deviceHistory)):
		Vxs.extend(deviceHistory[i]['Results']['smu2_v2_data'])
		Vys.extend(deviceHistory[i]['Results']['smu2_v1_data'])
	Xs = -np.array(Vxs)/0.157
	Ys = np.array(Vys)/0.138
	Xs = Xs - np.min(Xs)
	Ys = Ys - np.min(Ys)
	
	# Axis Labels
	ax.set_ylabel('Y Position ($\\mu$m)')
	ax.set_xlabel('X Position ($\\mu$m)')
	
	# Get data
	Vx_vals = extractTraces(deviceHistory)['Vx'][0]
	Vy_vals = extractTraces(deviceHistory)['Vy'][0]
	Id_vals = extractTraces(deviceHistory)['Id'][0]
	
	# Plot
	ax.imshow(afm_ctrl.getRasteredMatrix(Vx_vals, Vy_vals, Id_vals), cmap=plotDescription['plotDefaults']['colorMap'], extent=(min(Xs), max(Xs), min(Ys), max(Ys)), interpolation=None)
	
	image = afm_reader.loadAFMImageFromTimeframe(deviceHistory[0]['dataFolder'], minTimestamp, maxTimestamp)
	
	# Add Legend and save figure
	adjustAndSaveFigure(fig, 'AFMdeviationsVsXY', mode_parameters)
	
	return (fig, ax)
	
	

		
	
def extractTraces(deviceHistory):
	Vx_topology_trace = []
	Vx_topology_retrace = []
	Vx_nap_trace = []
	Vx_nap_retrace = []
	
	Vy_topology_trace = []
	Vy_topology_retrace = []
	Vy_nap_trace = []
	Vy_nap_retrace = []
	
	Id_topology_trace = []
	Id_topology_retrace = []
	Id_nap_trace = []
	Id_nap_retrace = []
	
	for i in range(len(deviceHistory)):
		timestamps = deviceHistory[i]['Results']['timestamps_smu2']
		Vx = deviceHistory[i]['Results']['smu2_v2_data']
		Vy = deviceHistory[i]['Results']['smu2_v1_data']
		current = np.array(deviceHistory[i]['Results']['id_data'])
		currentLinearFit = np.polyval(np.polyfit(range(len(current)), current, 1), range(len(current)))
		currentLinearized = current - currentLinearFit
		currentLinearized = currentLinearized - np.median(currentLinearized)
		
		segments = afm_ctrl.getSegmentsOfTriangle(timestamps, Vx, discardThreshold=0.5, smoothSegmentsByOverlapping=False)
		
		for j in range(len(segments)):
			if((j % 4) == 0):
				Vx_topology_trace.append(list(np.array(Vx)[segments[j]]))
				Vy_topology_trace.append(list(np.array(Vy)[segments[j]]))
				Id_topology_trace.append(list(np.array(currentLinearized)[segments[j]]))
			elif((j % 4) == 1):
				Vx_topology_retrace.append(list(np.array(Vx)[segments[j]]))
				Vy_topology_retrace.append(list(np.array(Vy)[segments[j]]))
				Id_topology_retrace.append(list(np.array(currentLinearized)[segments[j]]))
			elif((j % 4) == 2):
				Vx_nap_trace.append(list(np.array(Vx)[segments[j]]))
				Vy_nap_trace.append(list(np.array(Vy)[segments[j]]))
				Id_nap_trace.append(list(np.array(currentLinearized)[segments[j]]))
			elif((j % 4) == 3):
				Vx_nap_retrace.append(list(np.array(Vx)[segments[j]]))
				Vy_nap_retrace.append(list(np.array(Vy)[segments[j]]))
				Id_nap_retrace.append(list(np.array(currentLinearized)[segments[j]]))
	
	return {
		'Vx': [Vx_topology_trace, Vx_topology_retrace, Vx_nap_trace, Vx_nap_retrace],
		'Vy': [Vy_topology_trace, Vy_topology_retrace, Vy_nap_trace, Vy_nap_retrace],
		'Id': [Id_topology_trace, Id_topology_retrace, Id_nap_trace, Id_nap_retrace]
	}
	
	
	

	
if(__name__=='__main__'):
	pass
	

