from utilities.MatplotlibUtility import *
from procedures import AFM_Control as afm_ctrl
from utilities import AFMReader as afm_reader

import numpy as np

plotDescription = {
	'plotCategory': 'device',
	'priority': 530,
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(5,4),
		'colorMap':'viridis'
	},
}


def interpolate_nans(X):
    """Overwrite NaNs with column value interpolations."""
    for j in range(X.shape[1]):
        mask_j = np.isnan(X[:,j])
        X[mask_j,j] = np.interp(np.flatnonzero(mask_j), np.flatnonzero(~mask_j), X[~mask_j,j])
    return X

def plot(deviceHistory, identifiers, mode_parameters=None, showBackgroundAFMImage=False, interpolateNans=True):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		fig.suptitle(getTestLabel(deviceHistory, identifiers))
		ax.set_title(' ')
	
	# Get X/Y limits
	times = []
	for i in range(len(deviceHistory)):
		times.extend(deviceHistory[i]['Results']['timestamps_smu2'])
	
	# Get data
	traces = extractTraces(deviceHistory)
	
	Vx_vals_1 = traces['Vx'][0]
	Vy_vals_1 = traces['Vy'][0]
	Id_vals_1 = traces['Id'][0]
	
	Vx_vals_2 = traces['Vx'][1]
	Vy_vals_2 = traces['Vy'][1]
	Id_vals_2 = traces['Id'][1]
	
	try:
		imageWidth = max(max(max(Vx_vals_1, key=max))-min(min(Vx_vals_1, key=min)), max(max(Vx_vals_2, key=max))-min(min(Vx_vals_2, key=min)))/0.157e6
		imageHeight = max(max(max(Vy_vals_1, key=max))-min(min(Vy_vals_1, key=min)), max(max(Vy_vals_2, key=max))-min(min(Vy_vals_2, key=min)))/0.138e6
	except Exception as e:
		imageWidth = 1
		imageHeight = 1
	
	# Determine the path to the correct AFM image to use
	image_path = None
	if(mode_parameters['AFMImagePath'] is not None):
		image_path = mode_parameters['AFMImagePath']
	else:
		min_timestamp = min(times)
		max_timestamp = max(times)
		avg_timestamp = np.mean(times)
		image_path = afm_reader.bestMatchAFMRegistry(deviceHistory[0]['dataFolder'], targetTimestamp=avg_timestamp)
	
	# Draw the image (if there is one to show)
	if((image_path is not None) and showBackgroundAFMImage):
		full_data, imageWidth, imageHeight = afm_reader.loadAFMImageData(image_path)
		ax.imshow(full_data['HeightRetrace'], cmap='Greys_r', extent=(0, imageWidth*10**6, 0, imageHeight*10**6), interpolation='spline36')
		# ax2.imshow(full_data['HeightRetrace'], cmap='Greys_r', extent=(0, imageWidth*10**6, 0, imageHeight*10**6), interpolation='spline36')
	
	# Axis Labels
	ax.set_ylabel('Y Position ($\\mu$m)')
	ax.set_xlabel('X Position ($\\mu$m)')
	# ax2.set_ylabel('Y Position ($\\mu$m)')
	# ax2.set_xlabel('X Position ($\\mu$m)')
	
	IdAlpha = 1
	if showBackgroundAFMImage:
		IdAlpha = 0.5
	
	# Plot data on top of AFM image
	afm_data, dataWidth, dataHeight = afm_ctrl.getRasteredMatrix(Vx_vals_1, Vy_vals_1, Id_vals_1)
	if interpolateNans:
		afm_data = interpolate_nans(afm_data)
	ax.imshow(afm_data, cmap=plotDescription['plotDefaults']['colorMap'], extent=(0, dataWidth, 0, dataHeight), alpha=IdAlpha, interpolation='spline36', aspect='auto')
	
	# afm_data_2, dataWidth_2, dataHeight_2 = afm_ctrl.getRasteredMatrix(Vx_vals_2, Vy_vals_2, Id_vals_2)
	# if interpolateNans:
	# 	afm_data_2 = interpolate_nans(afm_data_2)
	# ax2.imshow(afm_data_2, cmap=plotDescription['plotDefaults']['colorMap'], extent=(0, dataWidth_2, 0, dataHeight_2), alpha=IdAlpha, interpolation='spline36', aspect='auto')
	
	fig.tight_layout()
	
	# Re-adjust the axes to be centered on the image
	ax.set_xlim((0, imageWidth*10**6))
	ax.set_ylim((0, imageHeight*10**6))
	# ax2.set_xlim((0, imageWidth*10**6))
	# ax2.set_ylim((0, imageHeight*10**6))
	
	# Save figure
	adjustAndSaveFigure(fig, 'AFMdeviationsImage', mode_parameters)
	
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
	

