import os
import json
import glob
import re

import time



# === File System ===
def makeFolder(folderPath):
	if (not os.path.exists(folderPath)):
		print('New Folder: ' + str(folderPath))
		os.makedirs(folderPath)

def emptyFolder(folderPath):
	if os.path.exists(folderPath):
		fileNames = glob.glob(folderPath + '*.png')
		for fileName in fileNames:
			os.remove(fileName)



# === JSON ===
def saveJSON(directory, saveFileName, jsonData, subDirectory=None, incrementIndex=True):
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
	return loadJSON_slow(directory, loadFileName)

def loadJSON_slow(directory, loadFileName):
	jsonData = []
	with open(os.path.join(directory, loadFileName)) as file:
		for line in file:
			try:
				jsonData.append(json.loads(str(line)))
			except:
				print('Error loading JSON line in file {:}/{:}'.format(directory, loadFileName))
	return jsonData

def loadJSON_fast(directory, loadFileName, minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf')):
	fileLines = loadJSONtoStringArray(directory, loadFileName)
	filteredFileLines = filterStringArrayByIndexAndExperiment(directory, fileLines, minIndex, maxIndex, minExperiment, maxExperiment, minRelativeIndex, maxRelativeIndex)
	jsonData = parseJSON(filteredFileLines)
	return jsonData

def loadJSONIndex(directory):
	indexData = {}
	try:
		with open(os.path.join(directory, 'index.json'), 'r') as file:
			indexData = json.loads(file.readline())
	except FileNotFoundError:	
		indexData = {'index':0, 'experimentNumber':0, 'timestamp':0}
	return indexData

def incrementJSONIndex(directory):
	indexData = loadJSONIndex(directory)
	with open(os.path.join(directory, 'index.json'), 'w') as file:
		indexData['index'] += 1
		indexData['timestamp'] = time.time()
		json.dump(indexData, file)
		file.write('\n')
	return indexData['index']

def incrementJSONExperimentNumber(directory):
	indexData = loadJSONIndex(directory)
	with open(os.path.join(directory, 'index.json'), 'w') as file:
		indexData['experimentNumber'] += 1
		indexData['timestamp'] = time.time()
		json.dump(indexData, file)
		file.write('\n')
	return indexData['experimentNumber']



# === Device History API ===
def getDeviceDirectory(parameters):
	return os.path.join(parameters['dataFolder'], parameters['Identifiers']['user'], parameters['Identifiers']['project'], parameters['Identifiers']['wafer'], parameters['Identifiers']['chip'], parameters['Identifiers']['device']) + os.sep

def loadSpecificDeviceHistory(directory, fileName, minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf')):
	filteredHistory = []
	for experimentSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and (name[0:2] == 'Ex' and name[2:].isdigit()) and (int(name[1:]) >= minExperiment) and (int(name[:1]) <= maxExperiment))]:
		filteredHistory += loadJSON_fast(os.path.join(directory, experimentSubdirectory), fileName, minIndex, maxIndex, minExperiment, maxExperiment, minRelativeIndex, maxRelativeIndex)
	return filteredHistory

def getDataFilesForExperiments(directory, minExperiment=0, maxExperiment=float('inf')):
	dataFileNames = []
	for experimentSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and (name[0:2] == 'Ex' and name[2:].isdigit()) and (int(name[1:]) >= minExperiment) and (int(name[:1]) <= maxExperiment))]:
		for filePath in glob.glob(os.path.join(directory, experimentSubdirectory) + '/*.json'):
			dataFileName = os.path.basename(filePath)
			if(dataFileName not in dataFileNames):
				dataFileNames.append(dataFileName)
	return dataFileNames

def getIndexesForExperiments(directory, minExperiment, maxExperiment):
	indexes = []
	for experimentSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and (name[0:2] == 'Ex' and name[2:].isdigit()) and (int(name[1:]) >= minExperiment) and (int(name[:1]) <= maxExperiment))]:	
		for filePath in glob.glob(os.path.join(directory, experimentSubdirectory) + '/*.json'):
			jsonData = loadJSON_fast('', filePath, minExperiment=minExperiment, maxExperiment=maxExperiment)
			for deviceRun in jsonData:
				if(deviceRun['experimentNumber'] >= minExperiment) and (deviceRun['experimentNumber'] <= maxExperiment):
					indexes.append(deviceRun['index'])
	indexes.sort()
	return indexes
		


# === Chip History API ===
def getChipDirectory(parameters):
	return os.path.join(parameters['dataFolder'], parameters['Identifiers']['user'], parameters['Identifiers']['project'], parameters['Identifiers']['wafer'], parameters['Identifiers']['chip'])

def loadChipIndexes(directory):
	chipIndexes = {}
	for deviceSubdirectory in [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]:
		indexData = loadJSONIndex(os.path.join(directory, deviceSubdirectory))
		chipIndexes[deviceSubdirectory] = indexData
	return chipIndexes

def loadFullChipHistory(directory, fileName):
	chipHistory = []
	for deviceSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and os.path.exists(os.path.join(directory, name, fileName)))]:
		jsonData = loadSpecificDeviceHistory(os.path.join(directory, deviceSubdirectory), fileName)
		for deviceRun in jsonData:
			chipHistory.append(deviceRun)
	return chipHistory

def loadFirstRunChipHistory(directory, fileName):
	fullChipHistory = loadFullChipHistory(directory, fileName)
	firstRunsOnly = []
	devicesLogged = []
	for i in range(len(fullChipHistory)):
		deviceRun = fullChipHistory[i]
		if(deviceRun['Identifiers']['device'] not in devicesLogged):
			firstRunsOnly.append(deviceRun)
			devicesLogged.append(deviceRun['Identifiers']['device'])
	return firstRunsOnly

def loadMostRecentRunChipHistory(directory, fileName):
	fullChipHistory = list(reversed(loadFullChipHistory(directory, fileName)))
	lastRunsOnly = []
	devicesLogged = []
	for i in range(len(fullChipHistory)):
		deviceRun = fullChipHistory[i]
		if(deviceRun['Identifiers']['device'] not in devicesLogged):
			lastRunsOnly.append(deviceRun)
			devicesLogged.append(deviceRun['Identifiers']['device'])
	return lastRunsOnly



# === Wafer History API ===
def getWaferDirectory(parameters):
	return os.path.join(parameters['dataFolder'], parameters['Identifiers']['user'], parameters['Identifiers']['project'], parameters['Identifiers']['wafer'])



# === Faster JSON Loading ===
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

	

