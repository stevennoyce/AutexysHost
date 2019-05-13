

default_parameters = {
	'runType': {'type': 'keyChoice', 'ChoiceFrom': 'runConfigs', 'default':''},
	'runConfigs': {
		'GateSweep':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'GateSweep'},
			'isFastSweep': 				{'type':'bool', 'default': False},
			'fastSweepSpeed':			{'type':'int', 'units':'Hz', 'default': 1000},
			'isAlternatingSweep': 		{'type':'bool', 'default': False},
			'pulsedMeasurementOnTime': 	{'type':'float', 'units':'s', 'default': 0},
			'pulsedMeasurementOffTime': {'type':'float', 'units':'s', 'default': 0},
			'stepsInVGSPerDirection': 	{'type':'int', 'units':'#', 'default': 100},
			'pointsPerVGS': 			{'type':'int', 'units':'#', 'default': 1},
			'gateVoltageRamps':			{'type':'int', 'units':'#', 'default': 2},
			'complianceCurrent':		{'type':'float', 'units':'A', 'default': 100e-6},
			'drainVoltageSetPoint':		{'type':'float', 'units':'V', 'default': 0.5},
			'gateVoltageMinimum': 		{'type':'float', 'units':'V', 'default': -1},
			'gateVoltageMaximum': 		{'type':'float', 'units':'V', 'default': 1}
		},
		'DrainSweep':{
			'dependencies': 			{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default':'DrainSweep'},
			'isFastSweep': 				{'type':'bool', 'default':False},
			'fastSweepSpeed':			{'type':'int', 'units':'Hz', 'default': 1000},
			'stepsInVDSPerDirection': 	{'type':'int', 'units':'#', 'default':100},
			'pointsPerVDS': 			{'type':'int', 'units':'#', 'default':1},
			'drainVoltageRamps':		{'type':'int', 'units':'#', 'default': 2},
			'complianceCurrent':		{'type':'float', 'units':'A', 'default':100e-6},
			'gateVoltageSetPoint':		{'type':'float', 'units':'V', 'default':0},
			'drainVoltageMinimum': 		{'type':'float', 'units':'V', 'default':0},
			'drainVoltageMaximum': 		{'type':'float', 'units':'V', 'default':0.5}
		},
		'BurnOut':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type:': 'constant', 'default': 'BurnOut'},
			'pointsPerRamp': 			{'type:': 'int', 'units':'#', 'default':50},
			'pointsPerHold': 			{'type':'int', 'units':'#', 'default': 50},
			'complianceCurrent':		{'type':'float', 'units':'V', 'default': 2e-3},
			'thresholdProportion':		{'type':'float', 'units':'', 'default': 0.92},
			'minimumAppliedDrainVoltage': {'type':'float', 'units':'V', 'default': 1.1},
			'gateVoltageSetPoint':		{'type':'float', 'units':'V', 'default': 15.0},
			'drainVoltageMaxPoint':		{'type':'float', 'units':'V', 'default': 5},
			'drainVoltagePlateaus': 	{'type':'int', 'units':'#', 'default': 5}
		},
		'StaticBias':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default':'StaticBias'},
			'totalBiasTime': 			{'type':'float', 'units':'s', 'default': 60},
			'measurementTime': 			{'type':'float', 'units':'s', 'default': 10},
			'complianceCurrent': 		{'type':'float', 'units':'A', 'default': 100e-6},
			'delayBeforeMeasurementsBegin': {'type':'float', 'units':'s', 'default': 0},
			'gateVoltageSetPoint': 		{'type':'float', 'units':'V', 'default': 0},
			'drainVoltageSetPoint':		{'type':'float', 'units':'V', 'default': 0.5},
			'gateVoltageWhenDone':  	{'type':'float', 'units':'V', 'default': 0},
			'drainVoltageWhenDone': 	{'type':'float', 'units':'V', 'default': 0},
			'floatChannelsWhenDone': 	{'type':'bool', 'default': False},
			'delayWhenDone': 			{'type':'float', 'units':'s', 'default': 0}
		},
		'AutoBurnOut':{
			'dependencies':				{'ignore':True, 'value':['BurnOut']},
			'targetOnOffRatio': 		{'type':'float', 'units':'', 'default': 80},
			'limitBurnOutsAllowed': 	{'type':'int', 'units':'#', 'default': 8},
			'limitOnOffRatioDegradation': {'type':'float', 'units':'V', 'default': 0.7}
		},
		'AutoGateSweep':{
			'dependencies':				{'ignore':True, 'value':['GateSweep']},
			'sweepsPerVDS': 			{'type':'int', 'units':'#', 'default': 5},
			'drainVoltageSetPoints': 	{'type':'array', 'units':'V', 'default': []},
			'delayBetweenSweeps': 		{'type':'float', 'units':'s', 'default': 2},
			'timedSweepStarts': 		{'type':'bool', 'default': False}
		},
		'AutoDrainSweep':{
			'dependencies': 			{'ignore':True, 'value':['DrainSweep']},
			'sweepsPerVGS': 			{'type':'int', 'units':'#', 'default': 1},
			'gateVoltageSetPoints':		{'type':'array', 'units':'V', 'default':[-0.5, 0, 0.5]},
			'delayBetweenSweeps': 		{'type':'float', 'units':'s', 'default': 0},
			'timedSweepStarts': 		{'type':'bool', 'default': False}
		},
		'AutoStaticBias':{
			'dependencies': 						{'ignore':True, 'value':['StaticBias','GateSweep']},
			'numberOfStaticBiases': 				{'type':'int', 'units':'#', 'default': 1},
			'doInitialGateSweep': 					{'type':'bool', 'default': True},
			'applyGateSweepBetweenBiases': 			{'type':'bool', 'default': False},
			'firstDelayBeforeMeasurementsBegin':	{'type':'float', 'units':'s', 'default': 0},
			'numberOfBiasesBetweenIncrements': 		{'type':'int', 'units':'#', 'default': 1},
			'biasTimeList':							{'type':'array', 'units':'s', 'default': [0]}
			'incrementStaticGateVoltage': 			{'type':'float', 'units':'V', 'default': 0},
			'incrementStaticDrainVoltage': 			{'type':'float', 'units':'V', 'default': 0},
			'incrementGateVoltageWhenDone': 		{'type':'float', 'units':'V', 'default': 0},
			'incrementDrainVoltageWhenDone':		{'type':'float', 'units':'V', 'default': 0},
			'incrementDelayBeforeReapplyingVoltage':{'type':'float', 'units':'s', 'default': 0},
			'shuffleDelaysBeforeReapplyingVoltage': {'type':'bool', 'default': False}
		},
		'AFMControl':{
			'dependencies': 			{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default':'AFMControl'},
			'lines': 					{'type':'int', 'units':'#', 'default':3},
			'scanRate': 				{'type':'int', 'units':'#', 'default':1},
			'napOn': 					{'type':'bool', 'default':True},
			'startOnFrameSwitch': 		{'type':'bool', 'default':False},
			'drainVoltageSetPoint': 	{'type':'float', 'units':'V', 'default': 0.01},
			'gateVoltageSetPoint': 		{'type':'float', 'units':'V', 'default': 0},
			'complianceCurrent': 		{'type':'float', 'units':'A', 'default': 1e-6},
			'complianceVoltage': 		{'type':'float', 'units':'V', 'default': 10},
			'deviceMeasurementSpeed': 	{'type':'float', 'units':'Hz', 'default': 60},  # what are the units for this?
			'XYCableSwap':				{'type':'bool', 'default':False}
		},
		'SGMControl':{
			'dependencies': 				{'ignore':True, 'value':[]},
			'saveFileName': 				{'type':'constant', 'default':'AFMControl'},
			'lines': 						{'type':'int', 'units':'#', 'default':3},
			'scanRate': 					{'type':'int', 'units':'#', 'default':1},
			'napOn': 						{'type':'bool', 'default':True},
			'startOnFrameSwitch': 			{'type':'bool', 'default':False},
			'drainVoltageSetPoint': 		{'type':'float', 'units':'V', 'default': 0.01},
			'gateVoltageSetPoint': 			{'type':'float', 'units':'V', 'default': 0},
			'complianceCurrent': 			{'type':'float', 'units':'A', 'default': 1e-6},
			'complianceVoltage': 			{'type':'float', 'units':'V', 'default': 10},
			'deviceMeasurementSpeed': 		{'type':'float', 'units':'Hz', 'default': 60},
			'XYCableSwap':					{'type':'bool', 'default':False},
			'tracesToMeasure':				{'type':'int', 'units':'#', 'default': 1},
			'scans':						{'type':'int', 'units':'#', 'default':1},
			'delayBeforeApplyingVoltages':	{'type':'float', 'units':'s', 'default': 0}
		},
		'Delay':{
			'dependencies': 			{'ignore':True, 'value':[]},
			'message':					{'type':'string', 'default': ""},
			'delayTime':				{'type':'int', 'units':'s', 'default': 240}
		},
		'InverterSweep':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'InverterSweep'},
			'stepsInVINPerDirection': 	{'type':'int', 'units':'#', 'default': 100},
			'pointsPerVIN': 			{'type':'int', 'units':'#', 'default': 1},
			'inputVoltageRamps':		{'type':'int', 'units':'#', 'default': 2},
			'complianceCurrent':		{'type':'float', 'units':'A', 'default': 100e-6},
			'vddSupplyVoltageSetPoint':	{'type':'float', 'units':'V', 'default': 1.0},
			'inputVoltageMinimum': 		{'type':'float', 'units':'V', 'default': 0.0},
			'inputVoltageMaximum': 		{'type':'float', 'units':'V', 'default': 1.0}
		},
		'RapidBias':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'RapidBias'},
			'complianceCurrent':		{'type':'float', 'units':'A', 'default': 100e-6},
			'waveform': 				{'type':'constant', 'default': 'square'},
			'drainVoltageSetPoints':	{'type':'array', 'units':'V', 'default': [0.05]},
			'gateVoltageSetPoints':		{'type':'array', 'units':'V', 'default': [0.0]},
			'measurementPoints':		{'type':'array', 'units':'#', 'default': [50]},
			'averageOverPoints': 		{'type':'int', 'units':'#', 'default': 1},
			'maxStepInVDS': 			{'type':'float', 'units':'V', 'default': 0.025},
			'maxStepInVGS': 			{'type':'float', 'units':'V', 'default': 0.4},
			'startGrounded': 			{'type':'bool', 'default': False}
		},
		'NoiseCollection':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'NoiseCollection'},
			'measurementSpeed':	 		{'type':'float', 'units':'Hz', 'default': 10e3},
			'points':			 		{'type':'int', 'units':'#', 'default': 10e3},
			'complianceCurrent':		{'type':'float', 'units':'A', 'default': 100e-6},
			'gateVoltage':				{'type':'float', 'units':'V', 'default': 0},
			'drainVoltage':				{'type':'float', 'units':'V', 'default': 0.1}
		},
		'NoiseGrid':{
			'dependencies':				{'ignore':True, 'value':['NoiseCollection']},
			'saveFileName': 			{'type':'constant', 'default': 'NoiseGrid'},
			'gateVoltages':				{'type':'array', 'units':'V', 'default': [-0.5,0,0.5]},
			'drainVoltages':			{'type':'array', 'units':'V', 'default': [0.05,0.10,0.15]},
			'groundingTime':			{'type':'float', 'units':'s', 'default': 1}
		}
	},
	'Results':{
		
	},
	'Computed':{
		
	},
	'SensorData':{
		
	},
	'Identifiers':{
		'user':{'type':'string', 'default':'unknown'},
		'project':{'type':'string', 'default':'unknown'},
		'wafer':{'type':'string', 'default':'unknown'},
		'chip':{'type':'string', 'default':'unknown'},
		'device':{'type':'string', 'default':'unknown'},
		'step':{'type':'int', 'default': 0},
	},
	'MeasurementSystem':{
		'systemType': {'type':'choice', 'choices':['single', 'standalone', 'double'], 'default':['single', 'standalone', 'double'][1]},
		'systems': {},
		'deviceRange': {'type':'array', 'choices':["1-2", "2-3", "3-4", "5-6", "6-7", "7-8", "9-10", "10-11", "11-12", "13-14", "14-15", "15-16", "19-20", "21-22", "27-28", "29-30", "30-31", "31-32", "33-34", "34-35", "35-36", "37-38", "38-39", "39-40", "41-42", "42-43", "43-44", "45-46", "46-47", "47-48", "51-52", "53-54", "59-60", "61-62", "62-63", "63-64"], 'default':[]}
	},
	'dataFolder': {'type':'string', 'default':'../../AutexysData/'},
	'ParametersFormatVersion': {'default': 4}	
}



import copy

def get():
	return extractDefaults(copy.deepcopy(default_parameters))

def with_added(additional_parameters):
	default = get()
	combined = merge(default, additional_parameters)
	return combined

def merge(a, b):
	for key in b:
		if( (key in a) and (isinstance(a[key], dict)) and (isinstance(b[key], dict)) ):
			merge(a[key], b[key])
		else:
			a[key] = b[key]
	return a

def extractDefaults(d):
	if not isinstance(d, dict):
		return d
	if 'default' in d:
		return d['default']
	return {k:extractDefaults(v) for (k,v) in d.items() if not isinstance(v, dict) or 'ignore' not in v}

def mergeDefaults(a, b):
	for key in b:
		if( (key in a) and (isinstance(a[key], dict)) and (isinstance(b[key], dict)) ):
			mergeDefaults(a[key], b[key])
		elif( (key in a) and (isinstance(a[key], dict)) and not (isinstance(b[key], dict)) ): 
			if('default' in a[key]):
				a[key]['default'] = b[key]
		else:
			a[key] = b[key]
	return a

def full_with_added(additional_parameters):
	full_defaults = copy.deepcopy(default_parameters)
	combined = mergeDefaults(full_defaults, additional_parameters)
	return combined
	


if __name__ == '__main__':
	import pprint
	import deepdiff
	pprint.pprint(deepdiff.DeepDiff(default_parameters, get()))



