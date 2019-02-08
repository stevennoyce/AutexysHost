import numpy as np
import igor.binarywave as igorbinary
import os
import glob
from datetime import datetime

from utilities import DataLoggerUtility as dlu

# pip install igor

# The instrument that generates these files is an Asylum MFP-3D AFM
# The software that generates the files is based on IGOR, a plotting software
# Gwyddion can be also used to view .ibw AFM files

def getAFMRegistryDirectory(dataFolder):
	return os.path.join(dataFolder, 'AFM')

def loadAFMRegistry(dataFolder):
	afm_registry_directory = getAFMRegistryDirectory(dataFolder)
	return dlu.loadJSON(afm_registry_directory, 'AFM_Registry.json')

def updateAFMRegistry(dataFolder):
	afm_image_root_directories = ['/Users/jaydoherty/Documents/myResearch/Images/AFM/', '/Users/stevennoyce/Documents/']
	afm_registry_directory = getAFMRegistryDirectory(dataFolder)
	
	# Load all AFM images found in one of the specific root directories
	image_paths = []
	for afm_root in afm_image_root_directories:
		if(os.path.exists(afm_root)):
			ibwFiles = glob.glob(afm_root + '**/*.ibw', recursive=True)
			image_paths.extend(ibwFiles)
	
	# Load the AFM registry and determine the list of new images that have not yet been entered in the registry	
	afm_registry = loadAFMRegistry(dataFolder)
	registered_paths = [entry['path'] for entry in afm_registry]
	new_paths = list(set(image_paths) - set(registered_paths))
	
	# Open the new images and save important meta-data to the registry
	for path in new_paths:
		image_data = getAFMTimeMetrics(path)
		stringtime = image_data['DateTime']
		dt = datetime.strptime(stringtime, '%Y-%m-%d %I:%M:%S %p')
		timestamp = dt.timestamp()
		entryData = {'path':path, 'timestamp':timestamp}
		afm_registry.append(entryData)
		dlu.saveJSON(afm_registry_directory, 'AFM_Registry.json', entryData, incrementIndex=False)
		
	return afm_registry

def searchAFMRegistry(dataFolder, minTimestamp=0, maxTimestamp=float('inf')):
	matches = []
	afm_registry = updateAFMRegistry(dataFolder)
	for entry in afm_registry:
		if(os.path.exists(entry['path'])):
			if((minTimestamp <= entry['timestamp']) and (entry['timestamp'] <= maxTimestamp)):
				matches.append(entry['path'])
	
	return matches

def bestMatchAFMRegistry(dataFolder, targetTimestamp, minTimestamp=0, maxTimestamp=float('inf')):
	matches_in_range = []
	afm_registry = loadAFMRegistry(dataFolder)
	for entry in afm_registry:
		if(os.path.exists(entry['path'])):
			if((minTimestamp <= entry['timestamp']) and (entry['timestamp'] <= maxTimestamp)):
				matches_in_range.append(entry)
	
	best_match = None
	min_distance = float('inf')
	for entry in matches_in_range:
		distance = abs(targetTimestamp - entry['timestamp'])
		if(distance < min_distance):
			best_match = entry['path']
			min_distance = distance
	
	return best_match
	
	
def deepDecodeASCII(input):
	if isinstance(input, dict):
		return {deepDecodeASCII(key): deepDecodeASCII(value) for key, value in input.items()}
	elif isinstance(input, list):
		return [deepDecodeASCII(element) for element in input]
	elif isinstance(input, bytes):
		return str(input, encoding='ascii')
	else:
		return input


def loadAFM(path):
	data = igorbinary.load(path)
	note = data['wave']['note']
	
	noteData = {}
	
	for line in note.splitlines():
		line = line.replace(b' \xb0C', b'')
		line = line.replace(b'\xb0', b'')
		line = str(line, encoding='ascii')
		
		key, colon, value = line.partition(':')
		
		value = value.strip()
		
		try:
			value = float(value)
		except ValueError:
			if ',' in value:
				array = []
				for number in value.split(','):
					try:
						array.append(float(number))
					except ValueError:
						pass
				value = array
		
		noteData[key] = value
		
	data['wave']['note'] = noteData
	data = deepDecodeASCII(data)
	
	return data

def loadAFMImageData(path):
	afm = loadAFM(path)
	
	image_data = {}
	image_types = []
	for binary_labels in afm['wave']['labels']:
		for label in binary_labels:
			if(len(label) > 0):
				image_types.append(label)
				image_data[label] = []
	
	# data_array = afm['wave']['wData']
	# for row in range(len(data_array)):
	# 	# Add a row to each of the images
	# 	for point in range(len(data_array[0][0])):
	# 		image_data[image_types[point]].append([])
			
	# 	# Iterate over the columns of this row
	# 	for col in range(len(data_array[0])):
	# 		# At each column, add one point to each of the images
	# 		for point in range(len(data_array[0][0])):
	# 			image_data[image_types[point]][row].append(data_array[row][col][point])
	
	data_array = afm['wave']['wData']
	data_array2 = np.array(data_array).transpose(2,0,1)
	for i in range(len(image_types)):
		image_data[image_types[i]] = data_array2[i]
	
	image_width = afm['wave']['note']['FastScanSize']
	image_height = afm['wave']['note']['SlowScanSize']
	image_rotation = afm['wave']['note']['ScanAngle']
	
	# Image data must be rotated in order to plot correctly with matplotlib
	for key in image_data.keys():
		image_data[key] = np.rot90(image_data[key])
	
	return (image_data, image_width, image_height)

def getAFMTimeMetrics(path):
	afm = loadAFM(path)
	
	timeMetrics = {
		'DateTime': afm['wave']['note']['Date'] + ' ' + afm['wave']['note']['Time'],
		'Timestamp1990': afm['wave']['note']['Seconds'],
		'FrameTime': afm['wave']['note']['ImageFrameTime']
	}
	
	return timeMetrics

def getAFMMetaData(path):
	afm = loadAFM(path)
	
	metadata = afm['wave']['note']
	metadata['labels'] = afm['wave']['labels']
	
	return metadata

def getImportantNames():
	importantNoteNames = ['Date','Time','Seconds','ImageFrameTime','NapHeight','labels','NapTipVoltage','NapSurfaceVoltage','ScanSize','FastScanSize','SlowScanSize','ScanRate','ScanPoints','ScanLines','ScanAngle','NapMode','Channel1DataType','Channel2DataType','Channel3DataType','Channel4DataType','Channel5DataType','Channel6DataType','Channel7DataType','Channel8DataType','Chip','ScanSpeed','IntegralGain','ProportionalGain','AmplitudeSetpointVolts','AmplitudeSetpointMeters','DriveAmplitude','DriveFrequency','SlowScanEnabled','ScanDown','StartHeadTemp','StartScannerTemp','EndHeadTemp','EndScannerTemp','TipVoltage','SurfaceVoltage','User0Voltage','User1Voltage','FreeAirAmplitude','FreeAirPhase','NapIntegralGain','NapProportionalGain','NapAmplitudeSetpointVolts','NapDriveAmplitude','NapDriveFrequency','NapStartHeight','NapTime']
	
	return importantNoteNames
	
def getImportantAFMMetaData(path):
	afm = loadAFM(path)
	
	importantNotes = {name: afm['wave']['note'][name] for name in importantNoteNames}
	return importantNotes


# Examples of relevant data contained in the metadata

# 'Date': '2018-09-26'
# 'Time': '12:05:27 PM'
# 'Seconds': 3620808327.836
# 'ImageFrameTime': 64.0
# 'NapHeight': 1e-08
# 'labels': [[], [], [b'', b'HeightRetrace', b'AmplitudeRetrace', b'NapAmplitudeRetrace', b'PhaseRetracee', b'NapPhaseRetrace', b'ZSensorRetrace'], []]
# 'NapTipVoltage': 0.0
# 'NapSurfaceVoltage': 0.0
# 'ScanSize': 1e-05
# 'FastScanSize': 1e-05
# 'SlowScanSize': 1e-05
# 'ScanRate': 0.5
# 'ScanPoints': 32.0
# 'ScanLines': 32.0
# 'ScanAngle': 90.0
# 'NapMode': 1.0
# 'Channel1DataType': 'Height'
# 'Channel2DataType': 'Amplitude'
# 'Channel3DataType': 'Phase'
# 'Channel4DataType': 'ZSensor'
# 'Channel5DataType': 'None'
# 'Channel6DataType': 'None'
# 'Channel7DataType': 'None'
# 'Channel8DataType': 'None'
# 'Chip': 'OutC'
# 'ScanSpeed': 1.25e-05
# 'IntegralGain': 8.0
# 'ProportionalGain': 0.0
# 'AmplitudeSetpointVolts': 0.3
# 'AmplitudeSetpointMeters': 1e-08
# 'DriveAmplitude': 0.41308
# 'DriveFrequency': 60218.0
# 'SlowScanEnabled': 1.0
# 'ScanDown': 0.0
# 'StartHeadTemp': 33.312
# 'StartScannerTemp': 27.438
# 'EndHeadTemp': 33.3125
# 'EndScannerTemp': 27.4375
# 'TipVoltage': 0.0
# 'SurfaceVoltage': 0.0
# 'User0Voltage': 0.0
# 'User1Voltage': 0.0
# 'FreeAirAmplitude': 0.96426
# 'FreeAirPhase': 68.901
# 'NapIntegralGain': 10.0
# 'NapProportionalGain': 0.0
# 'NapAmplitudeSetpointVolts': 0.8
# 'NapDriveAmplitude': 0.01
# 'NapDriveFrequency': 60309.0
# 'NapStartHeight': 0.0
# 'NapTime': 0.10016


if __name__ == '__main__':
	path = '../../../AutexysPlatforms/Analysis/AFM_Loading/AFM_Test_Files/SGM0000.ibw'
	
	print(loadAFM(path))
	# print(getAFMMetaData(path))
	# print(getAFMTimeMetrics(path))
	# print(getAFMTimestamp(path))


