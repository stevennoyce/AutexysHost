import glob
import io
import json
import os
import re
import time
from functools import lru_cache

import numpy as np



# === File System ===
def makeFolder(folderPath):
	"""Create all of the folders in folderPath if they do not already exist."""
	try:
		if (not os.path.exists(folderPath)):
			print('New Folder: ' + str(folderPath))
			os.makedirs(folderPath)
	except Exception as e:
		print('Cannot make folder: "' + folderPath + '"')

def makeEmptyJSONFile(folderPath, fileName):
	"""Make an empty file called fileName.json in the folderPath directory."""
	makeFolder(folderPath)

	if('.json' not in fileName):
		fileName += '.json'

	with open(os.path.join(folderPath, fileName), 'w') as file:
		file.write('')

def deleteJSONFile(folderPath, fileName):
	"""Delete the file called fileName.json in the folderPath directory."""
	if '.json' not in fileName:
		fileName += '.json'

	fullPath = os.path.join(folderPath, fileName)
	if os.path.exists(folderPath):
		os.remove(fullPath)
	else:
		print('Warning - ' + fullPath + ' not found, so no file was deleted')

# === CSV ===
def loadCSV(directory, loadFileName, dataNamesLabel=None, dataValuesLabel=None):
	"""Load a specified CSV file in directory. If the CSV file has a row that names every data column and the data rows are labeled,
	then the data columns can be extracted to arrays in a dictionary. For the B1500A, these labels are 'DataName' and 'DataValue'. """

	# Load generic CSV data
	csv_data = []
	with open(os.path.join(directory, loadFileName), encoding='utf-8') as file:
		for line in file:
			row = line.strip().split(',')
			csv_data.append(row)

	# By default, just return the entire 2D array of CSV data
	if((dataNamesLabel is None) or (dataValuesLabel is None)):
		return csv_data

	# Locate the names of each data column
	column_index = {}
	formatted_data = {}
	for row in csv_data:
		if(row[0] == dataNamesLabel):
			for i in range(1, len(row)):
				column_index[i] = row[i].strip()
				formatted_data[row[i].strip()] = []
			break

	# Extract data values to the appropriate array for their column
	for row in csv_data:
		if(row[0] == dataValuesLabel):
			for i in range(1, len(row)):
				try:
					formatted_data[column_index[i]].append(float(row[i]))
				except:
					formatted_data[column_index[i]].append(row[i])

	return formatted_data

def saveCSV(deviceHistory, saveFileName, directory=''):
	makeFolder(directory)

	if(len(deviceHistory) <= 0):
		return
	
	# Handle saving multiple types of data (eg GateSweeps and StaticBias to the same CSV file)
	if(isinstance(deviceHistory[0], list)):
		# Split the data into the blocks separate blocks if each entry of deviceHistory is a list of data
		blocks = {}
		for data_segment in deviceHistory:
			data_type = data_segment[0]['runType']
			blocks[data_type] = {}
			blocks[data_type]['lines'] = formatAsCSV(data_segment)
			blocks[data_type]['filler_line'] = ','.join(['']*(blocks[data_type]['lines'][0].count(',')+1))
		
		# Combine the lines of each block with spacers used as needed so that each block is a group of columns in the final file
		max_length = max([len(blocks[key]['lines']) for key in blocks.keys()])
		lines = []
		for i in range(max_length):
			line = ''
			for key in blocks.keys():
				if(i < len(blocks[key]['lines'])):
					line += blocks[key]['lines'][i].replace('\n','')
				else:
					line += blocks[key]['filler_line']
				line += ', ,'
			lines.append(line + '\n')
	else:
		lines = formatAsCSV(deviceHistory)
	
	# Write all lines to the CSV file
	if(isinstance(saveFileName, io.StringIO)):
		file = saveFileName
		for line in lines:
			file.write(line)
	else:
		savePath = os.path.join(directory, saveFileName)
		with open(savePath, 'w') as file:
			for line in lines:
				file.write(line)

def formatAsCSV(deviceHistory, separateDataByEmptyRows=True):
	if(len(deviceHistory) <= 0):
		return []
	
	# Look at the first line in the data and extract the data lists to save
	data_columns = {}
	if(len(deviceHistory) >= 1):
		for key in deviceHistory[0]['Results'].keys():
			data_columns[key] = []

	# Flatten the data from multiple experiments into one array per column in the file, with different experiments separated by empty rows
	for jsonData in deviceHistory:
		for key in jsonData['Results']:
			if(key in data_columns.keys()):
				data_columns[key].extend(np.hstack(jsonData['Results'][key]).flatten())
				if(separateDataByEmptyRows):
					data_columns[key].append('')

	# Try to collect identifying info from the first entry in the data
	data_type = ''
	data_location = ''
	try:
		data_type = deviceHistory[0]['runType']
		data_location = getExperimentDirectory(getDeviceDirectory(deviceHistory[0]), deviceHistory[0]['experimentNumber'])
	except:
		pass

	lines = []

	# Write all of the variable names in the first line of the CSV
	header_line2 = ','.join(data_columns.keys()) + '\n'
	header_line1 = data_type + ',' + data_location +  ','.join(['']*(header_line2.count(','))) + '\n'
	lines.append(header_line1)
	lines.append(header_line2)

	# Write all of the data row-by-row to an array of CSV lines
	index = 0
	isDone = False
	while(not isDone):
		isDone = True
		values = []
		for key in data_columns.keys():
			if(index < len(data_columns[key])):
				values.append(str(data_columns[key][index]))
				isDone = False
			else:
				values.append('')

		row = ','.join(values) + '\n'
		lines.append(row)
		index += 1
	
	return lines

# === TXT ===
def saveText(directory, saveFileName, text, mode='a', appendNewLine=True):
	makeFolder(directory)
	with open(os.path.join(directory, saveFileName), mode) as file:
		file.write(text)
		if(appendNewLine):
			file.write('\n')

def appendText(directory, saveFileName, text):
	saveText(directory, saveFileName, text, mode='a', appendNewLine=True)

def overwriteText(directory, saveFileName, text):
	saveText(directory, saveFileName, text, mode='w', appendNewLine=False)

def loadText(directory, loadFileName):
	textData = ''
	try:
		with open(os.path.join(directory, loadFileName), 'r') as file:
			textData = file.read()
	except FileNotFoundError:
		textData = ''
	return textData

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
				jsonData.append(parseLine(line))
			except Exception as e:
				print('Error loading JSON line in file {:}/{:}'.format(directory, loadFileName))
				print(e)
	return jsonData

def loadJSON_fast(directory, loadFileName, minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf'), looseFiltering=False):
	"""Private method. Given filters of min/max index, experimentNumber, and relativeIndex this loads individual file lines much faster."""
	fileLines = loadJSONtoStringArray(directory, loadFileName)
	filteredFileLines = filterStringArrayByIndexAndExperiment(directory, fileLines, minIndex, maxIndex, minExperiment, maxExperiment, minRelativeIndex, maxRelativeIndex, looseFiltering=looseFiltering)
	jsonData = parseLines(filteredFileLines)
	return jsonData



# === Device History API ===
"""These are the public methods used specifically to load device data."""

def getDeviceDirectory(parameters):
	"""Given the typical parameters used to run an experiment, return the path to the directory where data will be saved for this device."""
	return os.path.join(parameters['dataFolder'], parameters['Identifiers']['user'], parameters['Identifiers']['project'], parameters['Identifiers']['wafer'], parameters['Identifiers']['chip'], parameters['Identifiers']['device']) + os.sep

def getExperimentDirectory(device_directory, experimentNumber):
	"""Given the typical parameters used to run an experiment, return the path to the directory where data will be saved for this device."""
	return os.path.join(device_directory, 'Ex'+str(experimentNumber)) + os.sep

def loadSpecificDeviceHistory(directory, fileName, minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf'), looseFiltering=False):
	"""Given a folder path and fileName, load data for a device over a range of indices or experiments.
	If minIndex/maxIndex or minExperiment/maxExperiment are negative, then index backwards (-1 == the most recent index/experiment)"""
	
	# Handle negative indexing (loads data starting from the end of the file)
	indexData = loadJSONIndex(directory)
	if(minExperiment < 0):
		minExperiment = indexData['experimentNumber'] + (minExperiment+1)
	if(maxExperiment < 0):
		maxExperiment = indexData['experimentNumber'] + (maxExperiment+1)
	if(minIndex < 0):
		minIndex = indexData['index'] + minIndex
	if(maxIndex < 0):
		maxIndex = indexData['index'] + maxIndex

	filteredHistory = []

	string_to_int = lambda text: int(text) if text.isdigit() else text
	natural_keys = lambda text: [string_to_int(c) for c in re.split('(\d+)', text)]

	for experimentSubdirectory in sorted([name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and os.path.exists(os.path.join(directory, name, fileName)) and (name[0:2] == 'Ex' and name[2:].isdigit()) and (int(name[2:]) >= minExperiment) and (int(name[2:]) <= maxExperiment))], key=natural_keys):
		filteredHistory += loadJSON_fast(os.path.join(directory, experimentSubdirectory), fileName, minIndex, maxIndex, minExperiment, maxExperiment, minRelativeIndex, maxRelativeIndex, looseFiltering=looseFiltering)

	return filteredHistory

@lru_cache(maxsize=32)
def loadSpecificDeviceHistoryWithCaching(cacheBust, *args, **kwargs):
	return loadSpecificDeviceHistory(*args, **kwargs)

def loadOldestDeviceHistory(directory, fileName, numberOfOldestExperiments=1, numberOfOldestIndexes=1):
	"""Given a folder path and fileName, load oldest data for a device. Can specify the number of oldest experiments to include, and the number of data entries within each old experiment to include."""
	mostRecentExperimentNumber = loadJSONIndex(directory)['experimentNumber']
	oldDeviceExperimentNumber = 1
	while(not os.path.exists(os.path.join(directory, 'Ex' + str(oldDeviceExperimentNumber), fileName)) and (oldDeviceExperimentNumber < mostRecentExperimentNumber)):
		oldDeviceExperimentNumber += 1
	oldestExperiments = loadSpecificDeviceHistory(directory, fileName, minExperiment=oldDeviceExperimentNumber, maxExperiment=oldDeviceExperimentNumber+(numberOfOldestExperiments-1))
	if(len(oldestExperiments) <= numberOfOldestIndexes):
		return oldestExperiments
	return oldestExperiments[-numberOfOldestIndexes:]

def loadMostRecentDeviceHistory(directory, fileName, numberOfRecentExperiments=1, numberOfRecentIndexes=1):
	"""Given a folder path and fileName, load most recent data for a device. Can specify the number of recent experiments to include, and the number of data entries within each recent experiment to include."""
	mostRecentExperimentNumber = loadJSONIndex(directory)['experimentNumber']
	recentDeviceExperimentNumber = mostRecentExperimentNumber
	while(not os.path.exists(os.path.join(directory, 'Ex' + str(recentDeviceExperimentNumber), fileName)) and (recentDeviceExperimentNumber > 0)):
		recentDeviceExperimentNumber -= 1
	recentExperiments = loadSpecificDeviceHistory(directory, fileName, minExperiment=recentDeviceExperimentNumber-(numberOfRecentExperiments-1), maxExperiment=recentDeviceExperimentNumber)
	if(len(recentExperiments) <= numberOfRecentIndexes):
		return recentExperiments
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

def getLinkedFileNamesForDeviceExperiments(directory, linkingFile, minExperiment=0, maxExperiment=float('inf')):
	"""Given a folder path, the name of a linking file, and range of experiments, get all of the unique .json file names that are pointed to by the linking file."""
	dataFileNames = []
	for experimentSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and (name[0:2] == 'Ex' and name[2:].isdigit()) and (int(name[2:]) >= minExperiment) and (int(name[2:]) <= maxExperiment))]:
		if(os.path.exists(os.path.join(directory, experimentSubdirectory, linkingFile))):
			jsonData = loadJSON(os.path.join(directory, experimentSubdirectory), linkingFile)
			for deviceRun in jsonData:
				for device,deviceIndex in deviceRun['DeviceCycling']['deviceIndexes'].items():
					deviceDataFileNames = getDataFileNamesForDeviceExperiments(os.path.join(getChipDirectory(deviceRun), device), minExperiment=deviceIndex['experimentNumber'], maxExperiment=deviceIndex['experimentNumber'])
					for dataFileName in deviceDataFileNames:
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
		deviceHistory = loadSpecificDeviceHistory(os.path.join(directory, deviceSubdirectory), fileName, minIndex=minIndex, maxIndex=maxIndex, minExperiment=minExperiment, maxExperiment=maxExperiment, minRelativeIndex=minRelativeIndex, maxRelativeIndex=maxRelativeIndex)
		chipHistory.extend(deviceHistory)
	return chipHistory

def loadChipHistoryByIndex(directory, fileName, deviceIndexes={}, specificDeviceList=None):
	"""Given a chip's folder path and a data fileName, load data from devices with specific individual experiments listed in the 'deviceIndexes' dictionary.
	The default loads all devices with an index but specific devices can also be specified."""
	linkedDevices = list(sorted(deviceIndexes.keys()))
	chipHistory = []
	for device in [device for device in linkedDevices if(os.path.isdir(os.path.join(directory, device)) and (specificDeviceList is None or device in specificDeviceList))]:
		indexData = deviceIndexes[device]
		deviceHistory = loadSpecificDeviceHistory(os.path.join(directory, device), fileName, minExperiment=indexData['experimentNumber'], maxExperiment=indexData['experimentNumber'])
		chipHistory.extend(deviceHistory)
	return chipHistory

def loadOldestChipHistory(directory, fileName, numberOfOldestExperiments=1, numberOfOldestIndexes=1, specificDeviceList=None):
	"""Given a chip's folder path and a data fileName, load the oldest saved jsonData for devices on that chip.
	The default loads all devices on the chip but specific devices can also be specified."""
	chipHistory = []
	for deviceSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and (specificDeviceList is None or name in specificDeviceList))]:
		deviceHistory = loadOldestDeviceHistory(os.path.join(directory, deviceSubdirectory), fileName, numberOfOldestExperiments=numberOfOldestExperiments, numberOfOldestIndexes=numberOfOldestIndexes)
		chipHistory.extend(deviceHistory)
	return chipHistory

def loadMostRecentChipHistory(directory, fileName, numberOfRecentExperiments=1, numberOfRecentIndexes=1, specificDeviceList=None):
	"""Given a chip's folder path and a data fileName, load the most recently saved jsonData for devices on that chip.
	The default loads all devices on the chip but specific devices can also be specified."""
	chipHistory = []
	for deviceSubdirectory in [name for name in os.listdir(directory) if(os.path.isdir(os.path.join(directory, name)) and (specificDeviceList is None or name in specificDeviceList))]:
		deviceHistory = loadMostRecentDeviceHistory(os.path.join(directory, deviceSubdirectory), fileName, numberOfRecentExperiments=numberOfRecentExperiments, numberOfRecentIndexes=numberOfRecentIndexes)
		chipHistory.extend(deviceHistory)
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

def filterStringArrayByIndexAndExperiment(directory, fileLines, minIndex=0, maxIndex=float('inf'), minExperiment=0, maxExperiment=float('inf'), minRelativeIndex=0, maxRelativeIndex=float('inf'), looseFiltering=False):
	filteredFileLines = fileLines

	if(minExperiment == maxExperiment):
		filteredFileLines = filterFileLines(filteredFileLines, 'experimentNumber', minExperiment, looseFiltering=looseFiltering)
	else:
		if(minExperiment > 0):
			filteredFileLines = filterFileLinesGreaterThan(filteredFileLines, 'experimentNumber', minExperiment, looseFiltering=looseFiltering)
		if(maxExperiment < float('inf')):
			filteredFileLines = filterFileLinesLessThan(filteredFileLines, 'experimentNumber', maxExperiment, looseFiltering=looseFiltering)

	if(minIndex == maxIndex):
		filteredFileLines = filterFileLines(filteredFileLines, 'index', minIndex, looseFiltering=looseFiltering)
	else:
		if(minIndex > 0):
			filteredFileLines = filterFileLinesGreaterThan(filteredFileLines, 'index', minIndex, looseFiltering=looseFiltering)
		if(maxIndex < float('inf')):
			filteredFileLines = filterFileLinesLessThan(filteredFileLines, 'index', maxIndex, looseFiltering=looseFiltering)

	if(minRelativeIndex > 0 or maxRelativeIndex < 1e10):
		experimentBaseIndex = min(getIndexesForExperiments(os.path.join(directory, '../'), minExperiment, maxExperiment))
		if(minRelativeIndex > 0):
			filteredFileLines = filterFileLinesGreaterThan(filteredFileLines, 'index', experimentBaseIndex + minRelativeIndex, looseFiltering=looseFiltering)
		if(maxRelativeIndex < float('inf')):
			filteredFileLines = filterFileLinesLessThan(filteredFileLines, 'index', experimentBaseIndex + maxRelativeIndex, looseFiltering=looseFiltering)

	return filteredFileLines

def parseLines(fileLines):
	jsonData = []
	for line in fileLines:
		try:
			jsonData.append(parseLine(line))
		except Exception as e:
			print('Error loading JSON line')
			print(e)
	return jsonData

def parseLine(line, correctLengths=True):
	data = json.loads(str(line))
	
	if correctLengths and ('Results' in data):
		equalLengthNames = ['id_data', 'ig_data', 'vds_data', 'vgs_data', 'smu2_i1_data', 'smu2_i2_data', 'smu2_v1_data', 'smu2_v2_data', 'timestamps', 'timestamps_smu2']
		lengths = [len(data['Results'][n]) for n in equalLengthNames if n in data['Results']]
		
		if len(lengths) > 0:
			if max(lengths) - min(lengths) == 1:
				print('Unequal Lengths, altering data length by 1! Beware!')
				for n in equalLengthNames:
					if n in data['Results']:
						if len(data['Results'][n]) == min(lengths):
							data['Results'][n].append(data['Results'][n][-1])
	
	return data



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

def filterFileLines(fileLines, property, value, looseFiltering=False):
	filteredFileLines = []
	for line in fileLines:
		if(looseFiltering):
			matches = re.findall(' "' + str(property) + '": ([^,}]*)' , line)
			if(str(value) in matches):
				filteredFileLines.append(line)
		else:
			match = re.search(' "' + str(property) + '": ([^,}]*)' , line)
			if(match and (match.group(1) == str(value))):
				filteredFileLines.append(line)
	return filteredFileLines

def filterFileLinesGreaterThan(fileLines, property, value, looseFiltering=False):
	filteredFileLines = []
	for line in fileLines:
		if(looseFiltering):
			matches = re.findall(' "' + str(property) + '": ([^,}]*)' , line)
			if(str(value) in matches):
				filteredFileLines.append(line)
		else:
			match = re.search(' "' + str(property) + '": ([^,}]*)' , line)
			if(match and (float(match.group(1)) >= value)):
				filteredFileLines.append(line)
	return filteredFileLines

def filterFileLinesLessThan(fileLines, property, value, looseFiltering=False):
	filteredFileLines = []
	for line in fileLines:
		if(looseFiltering):
			matches = re.findall(' "' + str(property) + '": ([^,}]*)' , line)
			if(str(value) in matches):
				filteredFileLines.append(line)
		else:
			match = re.search(' "' + str(property) + '": ([^,}]*)' , line)
			if(match and (float(match.group(1)) <= value)):
				filteredFileLines.append(line)
	return filteredFileLines


