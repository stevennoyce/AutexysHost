from utilities.MatplotlibUtility import *
from procedures import AFM_Control as afm_ctrl
from utilities import AFMReader as afm_reader

import time
import numpy as np
import difflib

plotDescription = {
	'plotCategory': 'device',
	'priority': 530,
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(4,3),
		'colorMap':'plasma'
	},
}


def interpolate_nans(X):
	"""Overwrite NaNs with column value interpolations."""
	for j in range(X.shape[1]):
		mask_j = np.isnan(X[:,j])
		X[mask_j,j] = np.interp(np.flatnonzero(mask_j), np.flatnonzero(~mask_j), X[~mask_j,j])
	return X

def plot(deviceHistory, identifiers, mode_parameters=None, 
		showBackgroundAFMImage=False,
		showSMUData=True,
		aspectRatio='auto',
		interpolateNans=True, 
		translucentSGM=False):
	
	startTime = time.time()
	
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Get X/Y limits
	times = []
	for i in range(len(deviceHistory)):
		times.extend(deviceHistory[i]['Results']['timestamps_smu2'])
	
	etStartTime = time.time()
	print('Time elapsed before extracting Traces is {} s'.format(etStartTime - startTime))
	
	if showSMUData:
		# Get data
		traces = extractTraces(deviceHistory)
		
		etEndTime = time.time()
		print('Time taken to extract traces is {} s'.format(etEndTime - etStartTime))
		
		traceNumber = 0
		
		Vx_vals = traces['Vx'][traceNumber]
		Vy_vals = traces['Vy'][traceNumber]
		Id_vals = traces['Id'][traceNumber]
	
	imageWidth = 0
	imageHeight = 0
	
	if showBackgroundAFMImage:
		# Determine the path to the correct AFM image to use
		image_path = None
		if(mode_parameters['AFMImagePath'] is not None):
			image_path = mode_parameters['AFMImagePath']
		else:
			min_timestamp = min(times)
			max_timestamp = max(times)
			avg_timestamp = np.mean(times)
			deviceHistory[0]['dataFolder'] = '../../AutexysData'
			image_path = afm_reader.bestMatchAFMRegistry(deviceHistory[0]['dataFolder'], targetTimestamp=avg_timestamp)
		
		# Draw the image (if there is one to show)
		if (image_path is not None):
			full_data, imageWidth, imageHeight = afm_reader.loadAFMImageData(image_path)
			traceName = difflib.get_close_matches('HeightTrace', full_data.keys(), n=1, cutoff=0)[0]
			
			heightValues = np.array(full_data[traceName])
			heightValues -= np.nanmin(heightValues)
			heightValues *= 1e9
			
			heightline = ax.imshow(heightValues, cmap='Greys', extent=(0, imageWidth*1e6, 0, imageHeight*1e6), interpolation='spline36', aspect=aspectRatio)
			
			cbar = fig.colorbar(heightline, pad=0.015, aspect=50)
			cbar.set_label('Height [nm]', rotation=270, labelpad=11)
			# ax2.imshow(full_data['HeightRetrace'], cmap='Greys_r', extent=(0, imageWidth*10**6, 0, imageHeight*10**6), interpolation='spline36')
	
	# Axis Labels
	ax.set_ylabel('Y Position ($\\mu$m)')
	ax.set_xlabel('X Position ($\\mu$m)')
	# ax2.set_ylabel('Y Position ($\\mu$m)')
	# ax2.set_xlabel('X Position ($\\mu$m)')
	
	if showSMUData:
		IdAlpha = 1
		if showBackgroundAFMImage:
			IdAlpha = 0.5
		
		rmStartTime = time.time()
		print('Time elapsed before rastered matrix is {} s'.format(rmStartTime - etEndTime))
		
		# Plot data on top of AFM image
		afm_data, dataWidth, dataHeight = afm_ctrl.getRasteredMatrix(Vx_vals, Vy_vals, Id_vals)
		
		inStartTime = time.time()
		print('Time taken to rastere matrix is {} s'.format(inStartTime - rmStartTime))
		
		if interpolateNans:
			afm_data = interpolate_nans(afm_data)
		
		isStartTime = time.time()
		print('Time taken to interpolate nans is {} s'.format(isStartTime - inStartTime))
		
		colorMap = plotDescription['plotDefaults']['colorMap']
		if translucentSGM:
			colorMap = rgba_to_rgba_map((255, 200, 0, 255),	(255, 200, 0, 0))
		
		img = ax.imshow(afm_data*1e9, cmap=colorMap, extent=(0, dataWidth*1e6, 0, dataHeight*1e6), interpolation='spline36', aspect=aspectRatio, vmin=None, vmax=None)
		
		cbar = fig.colorbar(img, pad=0.015, aspect=50)
		cbar.set_label('Drain Current [nA]', rotation=270, labelpad=11)
		
		# afm_data_2, dataWidth_2, dataHeight_2 = afm_ctrl.getRasteredMatrix(Vx_vals_2, Vy_vals_2, Id_vals_2)
		# if interpolateNans:
		# 	afm_data_2 = interpolate_nans(afm_data_2)
		# ax2.imshow(afm_data_2, cmap=plotDescription['plotDefaults']['colorMap'], extent=(0, dataWidth_2, 0, dataHeight_2), alpha=IdAlpha, interpolation='spline36', aspect='auto')
	
	fig.tight_layout()
	
	if imageWidth == 0:
		imageWidth = dataWidth
	if imageHeight == 0:
		imageHeight = dataHeight
	
	# Re-adjust the axes to be centered on the image
	# ax.set_xlim((0, imageWidth*10**6))
	# ax.set_ylim((0, imageHeight*10**6))
	# ax2.set_xlim((0, imageWidth*10**6))
	# ax2.set_ylim((0, imageHeight*10**6))
		
	print('Total time is {} s'.format(time.time() - startTime))
	
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
	

