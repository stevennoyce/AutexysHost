
default_parameters = {
	'runType': '', # Select from keys of runConfigs
	'runConfigs':{
		'GateSweep':{
			'saveFileName': 'GateSweep',
			'isFastSweep': False,
			'isAlternatingSweep': False,
			'pulsedMeasurementOnTime': 0,
			'pulsedMeasurementOffTime': 0,
			'stepsInVGSPerDirection': 100,
			'pointsPerVGS': 1,
			'complianceCurrent':	100e-6,
			'drainVoltageSetPoint':	-0.5,
			'gateVoltageMinimum': 	-15,
			'gateVoltageMaximum': 	15
		},
		'DrainSweep':{
			'saveFileName': 'DrainSweep',
			'isFastSweep': False,
			'stepsInVDSPerDirection': 100,
			'pointsPerVDS': 1,
			'complianceCurrent':	100e-6,
			'gateVoltageSetPoint':	0,
			'drainVoltageMinimum': 	0,
			'drainVoltageMaximum': 	0.5
		},
		'BurnOut':{
			'saveFileName': 'BurnOut',
			'pointsPerRamp': 50,
			'pointsPerHold': 50,
			'complianceCurrent':	2e-3,
			'thresholdProportion':	0.92,
			'minimumAppliedDrainVoltage': 1.1,
			'gateVoltageSetPoint':	15.0,
			'drainVoltageMaxPoint':	5,
			'drainVoltagePlateaus': 5
		},
		'StaticBias':{
			'saveFileName': 'StaticBias',
			'totalBiasTime': 60,
			'measurementTime': 10,
			'complianceCurrent': 100e-6,
			'delayBeforeMeasurementsBegin': 0,
			'gateVoltageSetPoint': 	-15,
			'drainVoltageSetPoint':	-0.5,
			'gateVoltageWhenDone':  0,
			'drainVoltageWhenDone': 0,
			'floatChannelsWhenDone': False,
			'delayWhenDone': 0
		},
		'AutoBurnOut':{
			'targetOnOffRatio': 80,
			'limitBurnOutsAllowed': 8,
			'limitOnOffRatioDegradation': 0.7
		},
		'AutoGateSweep':{
			'drainVoltageSetPoints': [-0.100, -0.010],
			'sweepsPerVDS': 1,
			'delayBetweenSweeps': 0,
			'timedSweepStarts': False
		},
		'AutoDrainSweep':{
			'gateVoltageSetPoints': [-10.0, -5.0, 0],
			'sweepsPerVGS': 1,
			'delayBetweenSweeps': 0
		},
		'AutoStaticBias':{
			'numberOfStaticBiases': 1,
			'doInitialGateSweep': True,
			'applyGateSweepBetweenBiases': False,
			'firstDelayBeforeMeasurementsBegin': 0,
			'numberOfBiasesBetweenIncrements': 1,
			'incrementStaticGateVoltage': 0,
			'incrementStaticDrainVoltage': 0,
			'incrementGateVoltageWhenDone': 0,
			'incrementDrainVoltageWhenDone': 0,
			'incrementDelayBeforeReapplyingVoltage': 0,
			'shuffleDelaysBeforeReapplyingVoltage': False
		},
		'AFMControl':{
			'saveFileName': 'AFMControl',
			'lines': 3,
			'scanRate': 1,
			'napOn': True,
			'drainVoltageSetPoint': 0.01,
			'gateVoltageSetPoint': 0,
			'complianceCurrent': 1e-6,
			'complianceVoltage': 10,
			'deviceMeasurementSpeed': 60
		},
		'Delay':{
			'message': "",
			'delayTime': 240,
		}
	},
	'Results':{
		
	},
	'Computed':{
		
	},
	'SensorData':{
		
	},
	'Identifiers':{
		
	},
	'MeasurementSystem':{
		'systemType': ['single', 'standalone', 'double'][1],
		'systems': {
			
		},
		'deviceRange': []
	},
	'dataFolder': '../../AutexysData/',
	'ParametersFormatVersion': 4
}


default_parameters_combined = {
	'runConfigs': {
		'GateSweep':{
			'dependencies':[],
			'saveFileName': {'type':'constant', 'default': 'GateSweep'},
			'isFastSweep': {'type':'bool', 'default': 'False'},
			'isAlternatingSweep': {'type':'bool', 'default': 'False'},
			'pulsedMeasurementOnTime': {'type':'float', 'units':'s', 'default': 0},
			'pulsedMeasurementOffTime': {'type':'float', 'units':'s', 'default': 0},
			'stepsInVGSPerDirection': {'type':'int', 'units':'#', 'default': 100},
			'pointsPerVGS': {'type':'int', 'units':'#', 'default': 1},
			'complianceCurrent':	{'type':'float', 'units':'A', 'default': 100e-6},
			'drainVoltageSetPoint':	{'type':'float', 'units':'V', 'default': -0.5},
			'gateVoltageMinimum': 	{'type':'float', 'units':'V', 'default': -15},
			'gateVoltageMaximum': 	{'type':'float', 'units':'V', 'default': 15}
		},
		'DrainSweep':{
			'saveFileName': 'DrainSweep',
			'isFastSweep': {'type':'bool', 'default':False},
			'stepsInVDSPerDirection': {'type':'int', 'units':'#', 'default':100},
			'pointsPerVDS': {'type':'int', 'units':'#', 'default':1},
			'complianceCurrent':	{'type':'float', 'units':'A', 'default':100e-6},
			'gateVoltageSetPoint':	{'type':'float', 'units':'V', 'default':0},
			'drainVoltageMinimum': 	{'type':'float', 'units':'V', 'default':0},
			'drainVoltageMaximum': 	{'type':'float', 'units':'V', 'default':0.5}
		},
		'BurnOut':{
			'dependencies':[],
			'saveFileName': {'type:': 'constant', 'default': 'BurnOut'},
			'pointsPerRamp': {'type:': 'int', 'units':'#', 'default':50},
			'pointsPerHold': {'type':'int', 'units':'#', 'default': 50},
			'complianceCurrent':	{'type':'float', 'units':'V', 'default': 2e-3},
			'thresholdProportion':	{'type':'float', 'units':'', 'default': 0.92},
			'minimumAppliedDrainVoltage': {'type':'float', 'units':'V', 'default': 1.1},
			'gateVoltageSetPoint':	{'type':'float', 'units':'V', 'default': 15.0},
			'drainVoltageMaxPoint':	{'type':'float', 'units':'V', 'default': 5},
			'drainVoltagePlateaus': {'type':'int', 'units':'#', 'default': 5}
		},
		'StaticBias':{
			'dependencies':[],
			'saveFileName': {'type':'constant', 'default':'StaticBias'},
			'totalBiasTime': {'type':'float', 'units':'s', 'default': 60},
			'measurementTime': {'type':'float', 'units':'s', 'default': 10},
			'complianceCurrent': {'type':'float', 'units':'A', 'default': 100e-6},
			'delayBeforeMeasurementsBegin': {'type':'float', 'units':'s', 'default': 0},
			'gateVoltageSetPoint': 	{'type':'float', 'units':'V', 'default': -15},
			'drainVoltageSetPoint':	{'type':'float', 'units':'V', 'default': -0.5},
			'gateVoltageWhenDone':  {'type':'float', 'units':'V', 'default': 0},
			'drainVoltageWhenDone': {'type':'float', 'units':'V', 'default': 0},
			'floatChannelsWhenDone': {'type':'bool', 'default': False},
			'delayWhenDone': {'default': 0}
		},
		'AutoBurnOut':{
			'dependencies':['BurnOut'],
			'targetOnOffRatio': {'type':'float', 'units':'', 'default': 80},
			'limitBurnOutsAllowed': {'type':'int', 'units':'#', 'default': 8},
			'limitOnOffRatioDegradation': {'type':'float', 'units':'V', 'default': 0.7}
		},
		'AutoGateSweep':{
			'dependencies':['GateSweep'],
			'sweepsPerVDS': {'type':'int', 'units':'#', 'default': 1},
			'drainVoltageSetPoints': {'default': [-0.100, -0.010]},
			'applyStaticBiasBetweenSweeps': {'type':'bool'},
			'delayBetweenSweeps': {'type':'float', 'units':'s', 'default': 0},
			'timedSweepStarts': {'type':'bool', 'default': False}
		},
		'AutoDrainSweep':{
			'gateVoltageSetPoint':	{'type':'float', 'units':'V', 'default':[-10.0, -5.0, 0]},
			'sweepsPerVGS': {'type':'int', 'units':'#', 'default': 1},
			'delayBetweenSweeps': {'type':'float', 'units':'s', 'default': 0}
		},
		'AutoStaticBias':{
			'dependencies':['StaticBias','GateSweep'],
			'numberOfStaticBiases': {'type':'int', 'units':'#', 'default': 1},
			'doInitialGateSweep': {'type':'bool', 'default': True},
			'applyGateSweepBetweenBiases': {'type':'bool', 'default': False},
			'turnChannelsOffBetweenBiases': {'type':'bool'},
			'channelsOffTime': {'type':'float', 'units':'V'},
			'firstDelayBeforeMeasurementsBegin': {'type':'float', 'units':'s', 'default': 0},
			'numberOfBiasesBetweenIncrements': {'type':'int', 'units':'#', 'default': 1},
			'incrementStaticGateVoltage': {'type':'float', 'units':'V', 'default': 0},
			'incrementStaticDrainVoltage': {'type':'float', 'units':'V', 'default': 0},
			'incrementGateVoltageWhenDone': {'type':'float', 'units':'V', 'default': 0},
			'incrementDrainVoltageWhenDone': {'type':'float', 'units':'V', 'default': 0},
			'incrementDelayBeforeReapplyingVoltage': {'type':'float', 'units':'s', 'default': 0},
			'shuffleDelaysBeforeReapplyingVoltage': {'type':'bool', 'default': False}
		},
		'AFMControl':{
			'saveFileName': {'type':'constant', 'default':'AFMControl'},
			'lines': {'type':'int', 'units':'#', 'default':3},
			'scanRate': {'type':'int', 'units':'#', 'default':1},
			'napOn': {'type':'bool', 'default':True},
			'drainVoltageSetPoint': {'type':'float', 'units':'V', 'default': 0.01},
			'gateVoltageSetPoint': {'type':'float', 'units':'V', 'default': 0},
			'complianceCurrent': {'type':'float', 'units':'A', 'default': 1e-6},
			'complianceVoltage': {'type':'float', 'units':'V', 'default': 10},
			'deviceMeasurementSpeed': {'type':'float', 'units':'Hz', 'default': 60},  # what are the units for this?
		},
		'Delay':{
			'dependencies':[],
			'message':{'type':'string', 'default': ""},
			'delayTime':{'type':'int', 'units':'s', 'default': 240}
		}

	},
	'Results':{
		'default':{}
	},
	'Computed':{
		'default':{}
	},
	'SensorData':{
		'default':{}
	},
	'Identifiers':{
		'user':{'type':'string', 'default':'unknown'},
		'project':{'type':'string', 'default':'unknown'},
		'wafer':{'type':'string', 'default':'unknown'},
		'chip':{'type':'string', 'default':'unknown'},
		'device':{'type':'string', 'default':'unknown'},
		'step':{'type':'int'},
	},
	'MeasurementSystem':{
		'system': {'type':'choice','choices':['B2912A','PCB2v14'], 'default':['single', 'standalone', 'double'][1]},
		'NPLC': {'type':'float', 'units':'V'},
		'deviceRange': {'type':'array', 'default':[]}
	},
	'dataFolder': {'type':'string', 'default':'../../AutexysData'},
	'ParametersFormatVersion': {'default': 4}	
}



default_parameters_description = {
	'runConfigs': {
		'GateSweep':{
			'dependencies':[],
			'saveFileName': {'type':'constant'},
			'isFastSweep': {'type':'bool'},
			'isAlternatingSweep': {'type':'bool'},
			'pulsedMeasurementOnTime': {'type':'float', 'units':'s'},
			'pulsedMeasurementOffTime': {'type':'float', 'units':'s'},
			'stepsInVGSPerDirection': {'type':'int', 'units':'#'},
			'pointsPerVGS': {'type':'int', 'units':'#'},
			'complianceCurrent':	{'type':'float', 'units':'A'},
			'drainVoltageSetPoint':	{'type':'float', 'units':'V'},
			'gateVoltageMinimum': 	{'type':'float', 'units':'V'},
			'gateVoltageMaximum': 	{'type':'float', 'units':'V'}
		},
		'BurnOut':{
			'dependencies':[],
			'saveFileName': 'BurnOut',
			'pointsPerRamp': {'type':'int', 'units':'#'},
			'pointsPerHold': {'type':'int', 'units':'#'},
			'complianceCurrent':	{'type':'float', 'units':'V'},
			'thresholdProportion':	{'type':'float', 'units':''},
			'minimumAppliedDrainVoltage': {'type':'float', 'units':'V'},
			'gateVoltageSetPoint':	{'type':'float', 'units':'V'},
			'drainVoltageMaxPoint':	{'type':'float', 'units':'V'},
			'drainVoltagePlateaus': {'type':'int', 'units':'#'}
		},
		'AutoBurnOut':{
			'dependencies':['BurnOut'],
			'targetOnOffRatio': {'type':'float', 'units':''},
			'limitBurnOutsAllowed': {'type':'int', 'units':'#'},
			'limitOnOffRatioDegradation': {'type':'float', 'units':'V'}
		},
		'StaticBias':{
			'dependencies':[],
			'saveFileName': 'StaticBias',
			'totalBiasTime': {'type':'float', 'units':'s'},
			'measurementTime': {'type':'float', 'units':'s'},
			'complianceCurrent': {'type':'float', 'units':'A'},
			'delayBeforeMeasurementsBegin': {'type':'float', 'units':'s'},
			'gateVoltageSetPoint': 	{'type':'float', 'units':'V'},
			'drainVoltageSetPoint':	{'type':'float', 'units':'V'},
			'gateVoltageWhenDone':  {'type':'float', 'units':'V'},
			'drainVoltageWhenDone': {'type':'float', 'units':'V'}
		},
		'AutoGateSweep':{
			'dependencies':['GateSweep'],
			'sweepsPerVDS': {'type':'int', 'units':'#'},
			'applyStaticBiasBetweenSweeps': {'type':'bool'},
			'delayBetweenSweeps': {'type':'float', 'units':'s'},
			'timedSweepStarts': {'type':'bool'}
		},
		'AutoStaticBias':{
			'dependencies':['StaticBias','GateSweep'],
			'numberOfStaticBiases': {'type':'int', 'units':'#'},
			'doInitialGateSweep': {'type':'bool'},
			'applyGateSweepBetweenBiases': {'type':'bool'},
			'turnChannelsOffBetweenBiases': {'type':'bool'},
			'channelsOffTime': {'type':'float', 'units':'V'},
			'firstDelayBeforeMeasurementsBegin': {'type':'float', 'units':'s'},
			'numberOfBiasesBetweenIncrements': {'type':'int', 'units':'#'},
			'incrementStaticGateVoltage': {'type':'float', 'units':'V'},
			'incrementStaticDrainVoltage': {'type':'float', 'units':'V'},
			'incrementGateVoltageWhenDone': {'type':'float', 'units':'V'},
			'incrementDrainVoltageWhenDone': {'type':'float', 'units':'V'},
			'incrementDelayBeforeReapplyingVoltage': {'type':'float', 'units':'s'},
			'shuffleDelaysBeforeReapplyingVoltage': {'type':'bool'}
		},
		'Delay':{
			'dependencies':[],
			'message':{'type':'string'},
			'delayTime':{'type':'int', 'units':'s'}
		}
	},
	'Identifiers':{
		'user':{'type':'string'},
		'project':{'type':'string'},
		'wafer':{'type':'string'},
		'chip':{'type':'string'},
		'device':{'type':'string'},
		'step':{'type':'int'}
	},
	'MeasurementSystem':{
		'system': {'type':'choice','choices':['B2912A','PCB2v14']},
		'NPLC': {'type':'float', 'units':'V'},
		'deviceRange': {'type':'array'}
	},
	'dataFolder': {'type':'string'}
}


import copy

def get():
	return copy.deepcopy(default_parameters)

def getDefaults():
	return extractDefaults(default_parameters_combined)

def extractDefaults(d):
	if not isinstance(d, dict):
		return d
	if 'default' in d:
		return d['default']
	return {k:extractDefaults(v) for (k,v) in d.items()}

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


if __name__ == '__main__':
	print(getDefaults())



