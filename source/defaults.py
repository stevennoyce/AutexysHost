
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
		'systemType': ['single', 'standalone', 'double'][0],
		'systems': {
			
		},
		'deviceRange': []
	},
	'dataFolder': '../../AutexysData/',
	'ParametersFormatVersion': 4
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

