import os
import json
import glob
import re

import time



# === File System ===
def makeFolder(folderPath):
	"""Create all of the folders in folderPath if they do not already exist."""
	if (not os.path.exists(folderPath)):
		print('New Folder: ' + str(folderPath))
		os.makedirs(folderPath)

def emptyFolder(folderPath):
	"""Remove all png files from a folder."""
	if os.path.exists(folderPath):
		fileNames = glob.glob(folderPath + '*.png')
		for fileName in fileNames:
			os.remove(fileName)

def emptyFile(folderPath, fileName):
	"""Make an empty file called fileName.json in the folderPath directory."""
	makeFolder(folderPath)
	
	if '.json' not in fileName:
		fileName += '.json'
	
	with open(os.path.join(folderPath, fileName), 'w') as file:
		file.write('')
	


# === JSON ===
def saveJSON(directory, saveFileName, jsonData, subDirectory=None, incrementIndex=True):
	"""Save the jsonData dictionary to as saveFileName.json in directory. 
	If incrementIndex is True, also create an index.json file that tracks the index and experimentNumber of this jsonData.
	If subDirectory is not None, put saveFileName.json in a folder specified by directory + subDirectory. index.json is still put in directory."""
	savePath = directory
	if(subDirectory is not None):
		savePath = os.path.join(directory, subDirectory)
	makeFolder(savePath)
	
	if '.json' not in saveFileName:
		saveFileName += '.json'
	
	with open(os.path.join(savePath, saveFileName), 'a') as file:
		if(incrementIndex):
			indexData = loadJSONIndex(directory)
			jsonData['index'] = indexData['index']
			jsonData['experimentNumber'] = indexData['experimentNumber']
			jsonData['timestamp'] = time.time()
			incrementJSONIndex(directory)
		json.dump(jsonData, file)
		file.write('\n')	

def loadJSON(directory, loadFileName):
	"""Load loadFileName.json as a dictionary."""
	return loadJSON_slow(directory, loadFileName)

def loadJSONIndex(directory):
	"""Load the first line of index.json in directory."""
	indexData = {}
	try:
		with open(os.path.join(directory, 'index.json'), 'r') as file:
			indexData = json.loads(file.readline())
	except FileNotFoundError:	
		indexData = {'index':0, 'experimentNumber':0, 'timestamp':0}
	return indexData

def incrementJSONIndex(directory):
	"""Increase index in index.json by 1 and refresh the timestamp."""
	indexData = loadJSONIndex(directory)
	with open(os.path.join(directory, 'index.json'), 'w') as file:
		indexData['index'] += 1
		indexData['timestamp'] = time.time()
		json.dump(indexData, file)
		file.write('\n')
	return indexData['index']

def incrementJSONExperimentNumber(directory):
	"""Increase experimentNumber in index.json by 1 and refresh the timestamp."""
	indexData = loadJSONIndex(directory)
	with open(os.path.join(directory, 'index.json'), 'w') as file:
		indexData['experimentNumber'] += 1
		indexData['timestamp'] = time.time()
		json.dump(indexData, file)
		file.write('\n')
	return indexData['experimentNumber']
	
def loadJSON_slow(directory, loadFileName):
	"""Private method. This is the traditional way of parsing json data files, but it can be slow if you only need to see one line in a large file."""
	jsonData = []
	with open(os.path.join(directory, loadFileName)) as file:
		for line in file:
			try:
				jsonData.append(json.loads(str(line)))
			except:
				print('Error loading JSON line in file {:}/{:}'.format(directory, loadFileName))
	return jsonData

def loadJSON_fast(directory, loadFileName, minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf')):
	"""Private method. Given filters of min/max index, experimentNumber, and relativeIndex this loads individual file lines much faster."""
	fileLines = loadJSONtoStringArray(directory, loadFileName)
	filteredFileLines = filterStringArrayByIndexAndExperiment(directory, fileLines, minIndex, maxIndex, minExperiment, maxExperiment, minRelativeIndex, maxRelativeIndex)
	jsonData = parseJSON(filteredFileLines)
	return jsonData



# === Device History API ===
"""These are the public methods used specifically to load device data."""

def getDeviceDirectory(parameters):
	"""Given the typical parameters used to run an experiment, return the path to the directory where data will be saved for this device."""
	return os.path.join(parameters['dataFolder'], parameters['Identifiers']['user'], parameters['Identifiers']['project'], parameters['Identifiers']['wafer'], parameters['Identifiers']['chip'], parameters['Identifiers']['device']) + os.sep

def loadSpecificDeviceHistory(directory, fileName, minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf')):
	"""Given a folder path and fileName, load data for a device over a range of indices or experiments. 
	If minIndex/maxIndex or minExperiment/maxExperiment are negative, then index backwards (-1 == the most recent index/experiment)"""
	indexData = loadJSONIndex(directory)
	if(minExperiment < 0):
		minExperiment = indexData['experimentNumber'] + (minExperiment+1)
	if(maxExperiment < 0):
		maxExperiment = indexData['experimentNumber'] + (maxExperiment+1)
	if(minIndex < 0):
		minIndex = indexData['index'] + minIndex
	if(maxIndex < 0):
		maxIndex = indexData['index'] + maxIndex
	
	#folderlist = set()
	#for name in os.listdir(directory):
	#	if (os.path.isdir(os.path.join(directory, name)) and os.path.exists(os.path.join(directory, name, fileName)) and (name[0:2] == 'Ex' and name[2:].isdigit()) and (int(name[2:]) >= minExperiment) and (int(name[2:]) <= maxExperiment)):
	#		folderlist.add(int(name[2:]))

	#filteredHistory = []
	#for experimentSubdirectory in ["Ex" + str(val) for val in folderlist]:
	#	filteredHistory += loadJSON_fast(os.path.join(directory, experimentSubdirectory), fileName, minIndex, maxIndex, minExperiment, maxExperiment, minRelativeIndex, maxRelativeIndex)
	
	for experimentSubdirectory in sorted([name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and os.path.exists(os.path.join(directory, name, fileName)) and (name[0:2] == 'Ex' and name[2:].isdigit()) and (int(name[2:]) >= minExperiment) and (int(name[2:]) <= maxExperiment))]):
		filteredHistory += loadJSON_fast(os.path.join(directory, experimentSubdirectory), fileName, minIndex, maxIndex, minExperiment, maxExperiment, minRelativeIndex, maxRelativeIndex)	
		
	return filteredHistory

def loadOldestDeviceHistory(directory, fileName, numberOfOldestExperiments=1, numberOfOldestIndexes=1):
	"""Given a folder path and fileName, load oldest data for a device. Can specify the number of oldest experiments to include, and the number of data entries within each old experiment to include."""
	mostRecentExperimentNumber = loadJSONIndex(directory)['experimentNumber']
	oldDeviceExperimentNumber = 1
	while(not os.path.exists(os.path.join(directory, 'Ex' + str(oldDeviceExperimentNumber), fileName)) and (oldDeviceExperimentNumber < mostRecentExperimentNumber)):
		oldDeviceExperimentNumber += 1
	oldestExperiments = loadSpecificDeviceHistory(directory, fileName, minExperiment=oldDeviceExperimentNumber, maxExperiment=oldDeviceExperimentNumber+(numberOfOldestExperiments-1))
	return oldestExperiments[-numberOfOldestIndexes:]

def loadMostRecentDeviceHistory(directory, fileName, numberOfRecentExperiments=1, numberOfRecentIndexes=1):
	"""Given a folder path and fileName, load most recent data for a device. Can specify the number of recent experiments to include, and the number of data entries within each recent experiment to include."""
	mostRecentExperimentNumber = loadJSONIndex(directory)['experimentNumber']
	recentDeviceExperimentNumber = mostRecentExperimentNumber
	while(not os.path.exists(os.path.join(directory, 'Ex' + str(recentDeviceExperimentNumber), fileName)) and (recentDeviceExperimentNumber > 0)):
		recentDeviceExperimentNumber -= 1
	recentExperiments = loadSpecificDeviceHistory(directory, fileName, minExperiment=recentDeviceExperimentNumber-(numberOfRecentExperiments-1), maxExperiment=recentDeviceExperimentNumber)
	return recentExperiments[-numberOfRecentIndexes:]

def getDataFileNamesForDeviceExperiments(directory, minExperiment=0, maxExperiment=float('inf')):
	"""Given a folder path and range of experiments, get all of the unique .json file names that hold data in that directory."""
	dataFileNames = []
	for experimentSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and (name[0:2] == 'Ex' and name[2:].isdigit()) and (int(name[2:]) >= minExperiment) and (int(name[2:]) <= maxExperiment))]:
		for filePath in glob.glob(os.path.join(directory, experimentSubdirectory) + '/*.json'):
			dataFileName = os.path.basename(filePath)
			if(dataFileName not in dataFileNames):
				dataFileNames.append(dataFileName)
	return dataFileNames

def getIndexesForExperiments(directory, minExperiment, maxExperiment):
	"""Given a device folder path and range of experiments, get a list of the indices for the data in those experiments."""
	indexes = []
	for experimentSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and (name[0:2] == 'Ex' and name[2:].isdigit()) and (int(name[2:]) >= minExperiment) and (int(name[2:]) <= maxExperiment))]:	
		for filePath in glob.glob(os.path.join(directory, experimentSubdirectory) + '/*.json'):
			jsonData = loadJSON_fast('', filePath, minExperiment=minExperiment, maxExperiment=maxExperiment)
			for deviceRun in jsonData:
				if(deviceRun['experimentNumber'] >= minExperiment) and (deviceRun['experimentNumber'] <= maxExperiment):
					indexes.append(deviceRun['index'])
	indexes.sort()
	return indexes
		


# === Chip History API ===
"""These are the public methods used specifically to load data from multiple devices on the same chip."""

def getChipDirectory(parameters):
	"""Given the typical parameters used to run an experiment, return the path to the directory where data will be saved for this chip."""
	return os.path.join(parameters['dataFolder'], parameters['Identifiers']['user'], parameters['Identifiers']['project'], parameters['Identifiers']['wafer'], parameters['Identifiers']['chip'])

def loadChipIndexes(directory):
	"""Given a chip's folder path, load the index.json data for every device."""
	chipIndexes = {}
	for deviceSubdirectory in [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]:
		indexData = loadJSONIndex(os.path.join(directory, deviceSubdirectory))
		chipIndexes[deviceSubdirectory] = indexData
	return chipIndexes

def loadSpecificChipHistory(directory, fileName, specificDeviceList=None, minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf')):
	"""Given a chip's folder path and a data fileName, load data over a range of indices or experiments for devices on that chip.
	The default loads all devices on the chip but specific devices can also be specified."""
	chipHistory = []
	for deviceSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and (specificDeviceList is None or name in specificDeviceList))]:
		jsonData = loadSpecificDeviceHistory(os.path.join(directory, deviceSubdirectory), fileName, minIndex=minIndex, maxIndex=maxIndex, minExperiment=minExperiment, maxExperiment=maxExperiment, minRelativeIndex=minRelativeIndex, maxRelativeIndex=maxRelativeIndex)
		for deviceRun in jsonData:
			chipHistory.append(deviceRun)
	return chipHistory

def loadOldestChipHistory(directory, fileName, numberOfOldestExperiments=1, numberOfOldestIndexes=1, specificDeviceList=None):
	"""Given a chip's folder path and a data fileName, load the oldest saved jsonData for devices on that chip. 
	The default loads all devices on the chip but specific devices can also be specified."""
	chipHistory = []
	for deviceSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and (specificDeviceList is None or name in specificDeviceList))]:
		jsonData = loadOldestDeviceHistory(os.path.join(directory, deviceSubdirectory), fileName, numberOfOldestExperiments=numberOfOldestExperiments, numberOfOldestIndexes=numberOfOldestIndexes)
		for deviceRun in jsonData:
			chipHistory.append(deviceRun)
	return chipHistory

def loadMostRecentChipHistory(directory, fileName, numberOfRecentExperiments=1, numberOfRecentIndexes=1, specificDeviceList=None):
	"""Given a chip's folder path and a data fileName, load the most recently saved jsonData for devices on that chip. 
	The default loads all devices on the chip but specific devices can also be specified."""
	chipHistory = []
	for deviceSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and (specificDeviceList is None or name in specificDeviceList))]:
		jsonData = loadMostRecentDeviceHistory(os.path.join(directory, deviceSubdirectory), fileName, numberOfRecentExperiments=numberOfRecentExperiments, numberOfRecentIndexes=numberOfRecentIndexes)
		for deviceRun in jsonData:
			chipHistory.append(deviceRun)
	return chipHistory

def getDataFileNamesForChipExperiments(directory, minExperiment=0, maxExperiment=float('inf'), specificDeviceList=None):
	"""Given a folder path and range of experiments, get all of the unique .json file names that hold data in that directory."""
	dataFileNames = []
	for deviceSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and (specificDeviceList is None or name in specificDeviceList))]:
		# Get all .json files for this device's experiments
		deviceFileNames = getDataFileNamesForDeviceExperiments(os.path.join(directory, deviceSubdirectory), minExperiment=minExperiment, maxExperiment=maxExperiment)
		# Plus all of the supporting .json files in the device's subdirectory
		for filePath in glob.glob(os.path.join(directory, deviceSubdirectory) + '/*.json'):
			deviceInfoFileName = os.path.basename(filePath)
			if(deviceInfoFileName not in deviceFileNames):
				deviceFileNames.append(deviceInfoFileName)
		# Add all of those to the list of files available for this chip
		for dataFileName in deviceFileNames:
			if(dataFileName not in dataFileNames):
				dataFileNames.append(dataFileName)
	return dataFileNames



# === Wafer History API ===
"""These are the public methods used specifically to load data from multiple chips on the same wafer."""

def getWaferDirectory(parameters):
	"""Given the typical parameters used to run an experiment, return the path to the directory where data will be saved for this wafer."""
	return os.path.join(parameters['dataFolder'], parameters['Identifiers']['user'], parameters['Identifiers']['project'], parameters['Identifiers']['wafer'])



# === Faster JSON Loading ===
"""Private methods used to load data faster when only a few lines are needed from a large file."""

def loadJSONtoStringArray(directory, loadFileName):
	fileLines = []
	with open(os.path.join(directory, loadFileName)) as file:
		for line in file:
			fileLines.append(line)
	return fileLines

def filterStringArrayByIndexAndExperiment(directory, fileLines, minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf')):
	filteredFileLines = fileLines

	if(minExperiment == maxExperiment):
		filteredFileLines = filterFileLines(filteredFileLines, 'experimentNumber', minExperiment)
	else:
		if(minExperiment > 0):
			filteredFileLines = filterFileLinesGreaterThan(filteredFileLines, 'experimentNumber', minExperiment)
		if(maxExperiment < float('inf')):
			filteredFileLines = filterFileLinesLessThan(filteredFileLines, 'experimentNumber', maxExperiment)

	if(minIndex == maxIndex):
		filteredFileLines = filterFileLines(filteredFileLines, 'index', minIndex)
	else:
		if(minIndex > 0):
			filteredFileLines = filterFileLinesGreaterThan(filteredFileLines, 'index', minIndex)
		if(maxIndex < float('inf')):
			filteredFileLines = filterFileLinesLessThan(filteredFileLines, 'index', maxIndex)
	
	if(minRelativeIndex > 0 or maxRelativeIndex < 1e10):
		experimentBaseIndex = min(getIndexesForExperiments(directory, minExperiment, maxExperiment))
		if(minRelativeIndex > 0):
			filteredFileLines = filterFileLinesGreaterThan(filteredFileLines, 'index', experimentBaseIndex + minRelativeIndex)
		if(maxRelativeIndex < float('inf')):
			filteredFileLines = filterFileLinesLessThan(filteredFileLines, 'index', experimentBaseIndex + maxRelativeIndex)

	return filteredFileLines

def parseJSON(fileLines):
	jsonData = []
	for line in fileLines:
		try:
			jsonData.append(json.loads(str(line)))
		except:
			print('Error loading JSON line in file {:}/{:}'.format(directory, loadFileName))
	return jsonData



# === Filtering ===
"""Private methods used to filter either 1) arrays of parsed device data or 2) raw strings from files."""

def filterHistory(deviceHistory, property, value, subproperties=[]):
	filteredHistory = []
	for deviceRun in deviceHistory:
		propertyLocation = deviceRun
		for sub in subproperties:
			propertyLocation = propertyLocation[sub]
		try:
			if(propertyLocation[property] == value):
				filteredHistory.append(deviceRun)
		except:
			print("Unable to apply filter on '"+str(property)+"' == '"+str(value)+"'")
	return filteredHistory

def filterHistoryGreaterThan(deviceHistory, property, threshold):
	filteredHistory = []
	for deviceRun in deviceHistory:
		try:
			if(deviceRun[property] >= threshold):
				filteredHistory.append(deviceRun)
		except:
			print("Unable to apply filter on '"+str(property)+"' >= '"+str(value)+"'")
	return filteredHistory

def filterHistoryLessThan(deviceHistory, property, threshold):
	filteredHistory = []
	for deviceRun in deviceHistory:
		try:
			if(deviceRun[property] <= threshold):
				filteredHistory.append(deviceRun)
		except:
			print("Unable to apply filter on '"+str(property)+"' <= '"+str(value)+"'")
	return filteredHistory

def filterFileLines(fileLines, property, value):
	filteredFileLines = []
	for line in fileLines:
		match = re.search(' "' + str(property) + '": ([^,}]*)' , line)
		if(match and (match.group(1) == str(value))):
			filteredFileLines.append(line)
	return filteredFileLines

def filterFileLinesGreaterThan(fileLines, property, value):
	filteredFileLines = []
	for line in fileLines:
		match = re.search(' "' + str(property) + '": ([^,}]*)' , line)
		if(match and (float(match.group(1)) >= value)):
			filteredFileLines.append(line)

	return filteredFileLines

def filterFileLinesLessThan(fileLines, property, value):
	filteredFileLines = []
	for line in fileLines:
		match = re.search(' "' + str(property) + '": ([^,}]*)' , line)
		if(match and (float(match.group(1)) <= value)):
			filteredFileLines.append(line)
	return filteredFileLines

	

