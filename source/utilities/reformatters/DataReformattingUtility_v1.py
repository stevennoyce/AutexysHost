import glob
import os
import sys
import numpy as np

if(__name__ == '__main__'):
	sys.path.append(sys.path[0] + '/..')
import DataLoggerUtility as dlu

load_directory = '../../data_to_reformat/C127'
save_directory = '../../data_reformatted/C127'

def reformat_wafer(load_directory, save_directory):
	for chipSubdirectory in [name for name in os.listdir(load_directory) if os.path.isdir(os.path.join(load_directory, name))]:
		chipLoadDirectory = os.path.join(load_directory, chipSubdirectory)
		chipSaveDirectory = os.path.join(save_directory, chipSubdirectory)
		reformat_chip(chipLoadDirectory, chipSaveDirectory)

	# Copy wafer.json
	try:
		waferData = dlu.loadJSON(load_directory, 'wafer.json')[0]
		dlu.saveJSON(save_directory, 'wafer', waferData, incrementIndex=False)
	except:
		print('no wafer.json')
	


def reformat_chip(load_directory, save_directory):
	for deviceSubdirectory in [name for name in os.listdir(load_directory) if os.path.isdir(os.path.join(load_directory, name))]:
		deviceLoadDirectory = os.path.join(load_directory, deviceSubdirectory)
		deviceSaveDirectory = os.path.join(save_directory, deviceSubdirectory)
		reformat_device(deviceLoadDirectory, deviceSaveDirectory)

def reformat_device(load_directory, save_directory):
		device = load_directory.split('/')[-1]

		# Load device history for GateSweep, BurnOut, and StaticBias
		gateSweepHistory = dlu.loadJSON(load_directory, 'GateSweep.json')
		try:
			burnOutHistory = dlu.loadJSON(load_directory, 'BurnOut.json')
			burnedout = True
		except:
			print('Device: ' + device + ' no burn-out')
			burnedout = False
		try:
			staticBiasHistory = dlu.loadJSON(load_directory, 'StaticBias.json')
			staticed = True
		except:
			print('Device: ' + device + ' no static bias')
			staticed = False
		try:
			parametersHistory = dlu.loadJSON(load_directory, 'ParametersHistory.json')
			paramhist = True
		except:
			print('Device: ' + device + ' no ParametersHistory.json')
			paramhist = False
		# *************************************************************


		

		# *************************************************************
		# ****************** BEGIN DATA MODIFICATION ******************
		# *************************************************************

		# GATE SWEEP
		for deviceRun in gateSweepHistory:
			if(deviceRun['ParametersFormatVersion'] > 4):
				continue

			deviceRun['Identifiers'] = {}
			deviceRun['Identifiers']['user'] = 'stevenjay'
			deviceRun['Identifiers']['project'] = 'BiasStress1'
			deviceRun['Identifiers']['wafer'] = deviceRun['waferID']
			deviceRun['Identifiers']['chip'] = deviceRun['chipID']
			deviceRun['Identifiers']['device'] = deviceRun['deviceID']
			deviceRun['Identifiers']['step'] = 0
			del deviceRun['waferID']
			del deviceRun['chipID']
			del deviceRun['deviceID']
			if('deviceDirectory' in deviceRun):
				del deviceRun['deviceDirectory']
			if('DeviceHistory' in deviceRun):
					del deviceRun['DeviceHistory']
			if('postFigures' in deviceRun):
				del deviceRun['postFigures']
			if('plotsFolder' in deviceRun):
				del deviceRun['plotsFolder']

			system = deviceRun['MeasurementSystem'] if('MeasurementSystem' in deviceRun) else 'B2912A'
			deviceRun['MeasurementSystem'] = {}
			deviceRun['MeasurementSystem']['system'] = system
			deviceRun['MeasurementSystem']['NPLC'] = deviceRun['NPLC'] if('NPLC' in deviceRun) else 1
			deviceRun['MeasurementSystem']['deviceRange'] = deviceRun['deviceRange'] if('deviceRange' in deviceRun) else []
			if('NPLC' in deviceRun):
				del deviceRun['NPLC']
			if('deviceRange' in deviceRun):
				del deviceRun['deviceRange']

		# BURN OUT
		if(burnedout):
			for deviceRun in burnOutHistory:
				if(deviceRun['ParametersFormatVersion'] > 4):
					continue

				deviceRun['Identifiers'] = {}
				deviceRun['Identifiers']['user'] = 'stevenjay'
				deviceRun['Identifiers']['project'] = 'BiasStress1'
				deviceRun['Identifiers']['wafer'] = deviceRun['waferID']
				deviceRun['Identifiers']['chip'] = deviceRun['chipID']
				deviceRun['Identifiers']['device'] = deviceRun['deviceID']
				deviceRun['Identifiers']['step'] = 0
				del deviceRun['waferID']
				del deviceRun['chipID']
				del deviceRun['deviceID']
				if('deviceDirectory' in deviceRun):
					del deviceRun['deviceDirectory']
				if('DeviceHistory' in deviceRun):
					del deviceRun['DeviceHistory']
				if('postFigures' in deviceRun):
					del deviceRun['postFigures']
				if('plotsFolder' in deviceRun):
					del deviceRun['plotsFolder']

				system = deviceRun['MeasurementSystem'] if('MeasurementSystem' in deviceRun) else 'B2912A'
				deviceRun['MeasurementSystem'] = {}
				deviceRun['MeasurementSystem']['system'] = system
				deviceRun['MeasurementSystem']['NPLC'] = deviceRun['NPLC'] if('NPLC' in deviceRun) else 1
				deviceRun['MeasurementSystem']['deviceRange'] = deviceRun['deviceRange'] if('deviceRange' in deviceRun) else []
				if('NPLC' in deviceRun):
					del deviceRun['NPLC']
				if('deviceRange' in deviceRun):
					del deviceRun['deviceRange']

		# STATIC BIAS
		if(staticed):			
			for deviceRun in staticBiasHistory:
				if(deviceRun['ParametersFormatVersion'] > 4):
					continue

				deviceRun['Identifiers'] = {}
				deviceRun['Identifiers']['user'] = 'stevenjay'
				deviceRun['Identifiers']['project'] = 'BiasStress1'
				deviceRun['Identifiers']['wafer'] = deviceRun['waferID']
				deviceRun['Identifiers']['chip'] = deviceRun['chipID']
				deviceRun['Identifiers']['device'] = deviceRun['deviceID']
				deviceRun['Identifiers']['step'] = 0
				del deviceRun['waferID']
				del deviceRun['chipID']
				del deviceRun['deviceID']
				if('deviceDirectory' in deviceRun):
					del deviceRun['deviceDirectory']
				if('DeviceHistory' in deviceRun):
					del deviceRun['DeviceHistory']
				if('postFigures' in deviceRun):
					del deviceRun['postFigures']
				if('plotsFolder' in deviceRun):
					del deviceRun['plotsFolder']

				system = deviceRun['MeasurementSystem'] if('MeasurementSystem' in deviceRun) else 'B2912A'
				deviceRun['MeasurementSystem'] = {}
				deviceRun['MeasurementSystem']['system'] = system
				deviceRun['MeasurementSystem']['NPLC'] = deviceRun['NPLC'] if('NPLC' in deviceRun) else 1
				deviceRun['MeasurementSystem']['deviceRange'] = deviceRun['deviceRange'] if('deviceRange' in deviceRun) else []
				if('NPLC' in deviceRun):
					del deviceRun['NPLC']
				if('deviceRange' in deviceRun):
					del deviceRun['deviceRange']

		# PARAMETERS HISTORY
		if(paramhist):
			for deviceRun in parametersHistory:
				if('runFastSweep' in deviceRun['GateSweep']):
					deviceRun['GateSweep']['isFastSweep'] = deviceRun['GateSweep']['runFastSweep']
					del deviceRun['GateSweep']['runFastSweep']
				if('isAlternatingSweep' not in deviceRun['GateSweep']):
					deviceRun['GateSweep']['isAlternatingSweep'] = False
				if('pulsedMeasurementOnTime' not in deviceRun['GateSweep']):
					deviceRun['GateSweep']['pulsedMeasurementOnTime'] = 0
				if('pulsedMeasurementOffTime' not in deviceRun['GateSweep']):
					deviceRun['GateSweep']['pulsedMeasurementOffTime'] = 0

				if('DeviceHistory' in deviceRun):
					del deviceRun['DeviceHistory']

				deviceRun['Identifiers'] = {}
				deviceRun['Identifiers']['user'] = 'stevenjay'
				deviceRun['Identifiers']['project'] = 'BiasStress1'

				if(len(deviceRun['chipID']) == 1):
					deviceRun['Identifiers']['wafer'] = deviceRun['waferID']
					deviceRun['Identifiers']['chip'] = deviceRun['chipID']
					deviceRun['Identifiers']['device'] = deviceRun['deviceID']
					del deviceRun['waferID']
					del deviceRun['chipID']
					del deviceRun['deviceID']
				else:
					deviceRun['Identifiers']['wafer'] = deviceRun['chipID'][0:4]
					deviceRun['Identifiers']['chip'] = deviceRun['chipID'][4]
					deviceRun['Identifiers']['device'] = deviceRun['deviceID']
					del deviceRun['chipID']
					del deviceRun['deviceID']

				deviceRun['Identifiers']['step'] = None

				if('deviceDirectory' in deviceRun):
					del deviceRun['deviceDirectory']
				if('postFigures' in deviceRun):
					del deviceRun['postFigures']
				if('plotsFolder' in deviceRun):
					del deviceRun['plotsFolder']

				system = deviceRun['MeasurementSystem'] if('MeasurementSystem' in deviceRun) else 'B2912A'
				deviceRun['MeasurementSystem'] = {}
				deviceRun['MeasurementSystem']['system'] = system
				deviceRun['MeasurementSystem']['NPLC'] = deviceRun['NPLC'] if('NPLC' in deviceRun) else 1
				deviceRun['MeasurementSystem']['deviceRange'] = deviceRun['deviceRange'] if('deviceRange' in deviceRun) else []
				if('NPLC' in deviceRun):
					del deviceRun['NPLC']
				if('deviceRange' in deviceRun):
					del deviceRun['deviceRange']



		# *************************************************************
		# ******************  END DATA MODIFICATION  ******************
		# *************************************************************



		# Save device history for GateSweep, BurnOut, and StaticBias
		for deviceRun in gateSweepHistory:
			dlu.saveJSON(save_directory, 'GateSweep', deviceRun, incrementIndex=False)
		if(burnedout):
			for deviceRun in burnOutHistory:
				dlu.saveJSON(save_directory, 'BurnOut', deviceRun, incrementIndex=False)
		if(staticed):
			for deviceRun in staticBiasHistory:
				dlu.saveJSON(save_directory, 'StaticBias', deviceRun, incrementIndex=False)
		if(paramhist):
			for deviceRun in parametersHistory:
				dlu.saveJSON(save_directory, 'ParametersHistory', deviceRun, incrementIndex=False)

		# Copy index.json
		try:
			indexData = dlu.loadJSON(load_directory, 'index.json')[0]
			dlu.saveJSON(save_directory, 'index', indexData, incrementIndex=False)
		except:
			print('Device: ' + device + ' no index.json')
		# *************************************************************



if(__name__ == '__main__'):
	reformat_wafer(load_directory, save_directory)




