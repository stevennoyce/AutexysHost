from utilities.MatplotlibUtility import *
from procedures.AFM_Control import *


plotDescription = {
	'plotCategory': 'device',
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'colorMap':'plasma'
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
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
		
		Vxs.extend(deviceHistory[i]['Results']['smu2_v2_data'])
		Vys.extend(deviceHistory[i]['Results']['smu2_v1_data'])
		currents.extend(currentLinearized)
	
	Xs = -np.array(Vxs)/0.157
	Ys = np.array(Vys)/0.138
	
	Xs = Xs - np.min(Xs)
	Ys = Ys - np.min(Ys)
	
	# currents[np.where(Xs < 0.5)[0]] = 0
	
	c, a, b = zip(*sorted(zip(np.array(currents)*1e9, Xs, Ys), reverse=False))
	line = ax.scatter(a, b, c=c, cmap=plotDescription['plotDefaults']['colorMap'], alpha=0.6, marker='o')
	# line = ax.scatter(Xs, Ys, c=np.array(currents)*1e9, cmap=plotDescription['plotDefaults']['colorMap'], alpha=0.6)
	cbar = fig.colorbar(line, pad=0.015, aspect=50)
	cbar.set_label('Drain Current [nA]', rotation=270, labelpad=11)
	cbar.solids.set(alpha=1)
	
	# if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
		# setLabel(line, mode_parameters['legendLabels'][i])
	
	ax.set_ylabel('Y Position ($\mu$m)')
	ax.set_xlabel('X Position ($\mu$m)')
	
	# Add Legend and save figure
	adjustAndSaveFigure(fig, 'AFMdeviationsVsXY', mode_parameters)
	
	# ========= TEST ==========
	Vx_topolgy_trace = []
	Vx_topolgy_retrace = []
	Vx_nap_trace = []
	Vx_nap_retrace = []
	
	Vy_topolgy_trace = []
	Vy_topolgy_retrace = []
	Vy_nap_trace = []
	Vy_nap_retrace = []
	
	Id_topolgy_trace = []
	Id_topolgy_retrace = []
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
		
		indices = getSegmentsOfTriangle(timestamps, Vx)
		if(len(indices) > 4):
			if(len(indices[0]) > len(indices[-1])):
				indices = indices[0:-1]
			else:
				indices = indices[1:]
			
		Vx_topolgy_trace.append(np.array(Vx)[indices[0]])
		Vy_topolgy_trace.append(np.array(Vy)[indices[0]])
		Id_topolgy_trace.append(np.array(currentLinearized)[indices[0]])
		
		Vx_topolgy_retrace.append(np.array(Vx)[indices[1]])
		Vy_topolgy_retrace.append(np.array(Vy)[indices[1]])
		Id_topolgy_retrace.append(np.array(currentLinearized)[indices[1]])
		
		Vx_nap_trace.append(np.array(Vx)[indices[2]])
		Vy_nap_trace.append(np.array(Vy)[indices[2]])
		Id_nap_trace.append(np.array(currentLinearized)[indices[2]])
		
		Vx_nap_retrace.append(np.array(Vx)[indices[3]])
		Vy_nap_retrace.append(np.array(Vy)[indices[3]])
		Id_nap_retrace.append(np.array(currentLinearized)[indices[3]])
	
	
	return (fig, ax)
	


