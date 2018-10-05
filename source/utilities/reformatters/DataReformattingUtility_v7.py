import glob
import os
import sys
import numpy as np

import os
pathParents = os.getcwd().split('/')
if('AutexysHost' in pathParents):
	rootPath = os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source')
	os.chdir(rootPath)
	sys.path.append(rootPath)

from utilities import DataLoggerUtility as dlu

load_directory = '../../AutexysData/stevenjay/BiasStress1/C127'
save_directory = '../../AutexysDataReformatted/stevenjay/BiasStress1/C127'

load_directory = '../../AutexysData/'
save_directory = '../../AutexysDataReformatted/'

dataFileNames = ['DrainSweep.json', 'StaticBias.json', 'GateSweep.json', 'AFMControl.json', 'BurnOut.json']

# for dataFileName in dataFileNames:
# 	dataFiles = glob.glob(load_directory + '/**/' + dataFileName, recursive=True)
	
# 	for dataFile in dataFiles:
# 		dataLines = dlu.loadJSON(os.path.dirname(dataFile), os.path.basename(dataFile))
		
# 		for dataLine in dataLines:
# 			experimentNumber = dataLine['startIndexes']['experimentNumber']
			
# 			print(dataFile)
			
# 			# dlu.saveJSON(directory, saveFileName, jsonData, incrementIndex=False)

def getSubDirectories(directory):
	return [os.path.basename(os.path.dirname(g)) for g in glob.glob(directory + '/*/')]

for userName in getSubDirectories(load_directory):
	userDirectory = userName
	for projectName in getSubDirectories(os.path.join(load_directory, userDirectory)):
		projectDirectory = os.path.join(userDirectory, projectName)
		for waferName in getSubDirectories(os.path.join(load_directory, projectDirectory)):
			waferDirectory = os.path.join(projectDirectory, waferName)
			for chipName in getSubDirectories(os.path.join(load_directory, waferDirectory)):
				chipDirectory = os.path.join(waferDirectory, chipName)
				for deviceName in getSubDirectories(os.path.join(load_directory, chipDirectory)):
					deviceDirectory = os.path.join(chipDirectory, deviceName)
					
					for dataFileName in dataFileNames:
						dataFile = os.path.join(load_directory, deviceDirectory, dataFileName)
						
						if not os.path.exists(dataFile):
							continue
						
						dataLines = dlu.loadJSON(os.path.join(load_directory, deviceDirectory), dataFileName)
						
						for dataLine in dataLines:
							experimentNumber = dataLine['startIndexes']['experimentNumber']
							
							print(experimentNumber)
							
							experimentSaveDirectory = os.path.join(save_directory, deviceDirectory, 'E' + str(experimentNumber))
							dlu.saveJSON(experimentSaveDirectory, dataFileName, dataLine, incrementIndex=False)


