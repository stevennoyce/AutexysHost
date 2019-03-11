from utilities.MatplotlibUtility import *
from procedures.AFM_Control import *


plotDescription = {
	'plotCategory': 'device',
	'priority': 510,
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'colorMap':'plasma'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Build Color Map and Color Bar	
	colors = colorsFromMap(plotDescription['plotDefaults']['colorMap'], 0, 0.87, len(deviceHistory))['colors']
	
	Vxs = []
	Vys = []
	currents = []
	
	# Plot
	for i in range(len(deviceHistory)):
		current = np.array(deviceHistory[i]['Results']['id_data'])
		currentLinearFit = np.polyval(np.polyfit(range(len(current)), current, 1), range(len(current)))
		currentLinearized = current - currentLinearFit
		currentLinearized = currentLinearized - np.median(currentLinearized)
		
		# currentLinearized[np.where(np.array(deviceHistory[i]['Results']['smu2_v1_data']) - max(deviceHistory[i]['Results']['smu2_v1_data']) < -2.2*0.157)[0]] = 0
		
		xs = np.array(deviceHistory[i]['Results']['smu2_v2_data'])
		xs -= min(xs)
		
		Vxs.extend(list(xs))
		Vys.extend(deviceHistory[i]['Results']['smu2_v1_data'])
		currents.extend(currentLinearized)
	
	Xs = -np.array(Vxs)/0.157
	Ys = np.array(Vys)/0.138
	
	Xs = Xs - np.min(Xs)
	Ys = Ys - np.min(Ys)
	
	# currents[np.where(Xs < 0.5)[0]] = 0
	
	# c, a, b = zip(*sorted(zip(np.array(currents)*1e9, Xs, Ys), reverse=True))
	c, a, b = zip(*zip(np.array(currents)*1e9, Xs, Ys))
	
	line = ax.scatter(a, b, c=c, cmap=plotDescription['plotDefaults']['colorMap'], alpha=0.6, marker='o', s=14)
	# line = ax.scatter(Xs, Ys, c=np.array(currents)*1e9, cmap=plotDescription['plotDefaults']['colorMap'], alpha=0.6)
	cbar = fig.colorbar(line, pad=0.015, aspect=50)
	cbar.set_label('Drain Current [nA]', rotation=270, labelpad=11)
	cbar.solids.set(alpha=1)
	
	# if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
		# setLabel(line, mode_parameters['legendLabels'][i])
	
	ax.set_ylabel('Y Position ($\\mu$m)')
	ax.set_xlabel('X Position ($\\mu$m)')	
	
	return (fig, (ax,))
	
	

		
	
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
		
		segments = getSegmentsOfTriangle(timestamps, Vx, discardThreshold=0.5, smoothSegmentsByOverlapping=False)
		
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

