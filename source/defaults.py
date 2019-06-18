

default_parameters = {
	'runType': {'type': 'keyChoice', 'ChoiceFrom': 'runConfigs', 'default':''},
	'runConfigs': {
		'GateSweep':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'GateSweep', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'gateVoltageMinimum': 		{'type':'float', 'units':'V',  'default': -1,     'title':'Gate Voltage Start',           'description':'Gate voltage starting value.'},
			'gateVoltageMaximum': 		{'type':'float', 'units':'V',  'default': 1,      'title':'Gate Voltage End',             'description':'Gate voltage final value.'}, 
			'drainVoltageSetPoint':		{'type':'float', 'units':'V',  'default': 0.5,    'title':'Drain Voltage',                'description':'Drain voltage value.'},
			'complianceCurrent':		{'type':'float', 'units':'A',  'default': 100e-6, 'title':'Compliance Current',           'description':'Maximum current limit for the SMU.'},
			'stepsInVGSPerDirection': 	{'type':'int',   'units':'#',  'default': 100,    'title':'Steps In VGS (per direction)', 'description':'Number of unique gate voltage steps in the sweep.'},
			'pointsPerVGS': 			{'type':'int',   'units':'#',  'default': 1,      'title':'Points Per VGS',               'description':'Number of measurements taken at each gate voltage step.'},
			'gateVoltageRamps':			{'type':'int',   'units':'#',  'default': 2,      'title':'Gate Voltage Ramps',           'description':'Number of times to loop through gate voltage values.'},
			'isFastSweep': 				{'type':'bool',                'default': False,  'title':'Fast Sweep',                   'description':'Use internal SMU timer to measure a faster sweep.'},
			'fastSweepSpeed':			{'type':'int',   'units':'Hz', 'default': 1000,   'title':'Fast Sweep Speed',             'description':'Frequency of SMU internal timer.'},
			'isAlternatingSweep': 		{'type':'bool',                'default': False,  'title':'Alternating Sweep',            'description':''},
			'pulsedMeasurementOnTime': 	{'type':'float', 'units':'s',  'default': 0,      'title':'Pulsed Measurement On Time',   'description':''},
			'pulsedMeasurementOffTime': {'type':'float', 'units':'s',  'default': 0,      'title':'Pulsed Measurement Off Time',  'description':''},
		},
		'DrainSweep':{
			'dependencies': 			{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default':'DrainSweep', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'drainVoltageMinimum': 		{'type':'float', 'units':'V',  'default': 0,      'title':'Drain Voltage Start',          'description':'Drain voltage starting value.'},
			'drainVoltageMaximum': 		{'type':'float', 'units':'V',  'default': 0.5,    'title':'Drain Voltage End',            'description':'Drain voltage final value.'}, 
			'gateVoltageSetPoint':		{'type':'float', 'units':'V',  'default': 0,      'title':'Gate Voltage',                 'description':'Gate voltage value.'},
			'complianceCurrent':		{'type':'float', 'units':'A',  'default': 100e-6, 'title':'Compliance Current',           'description':'Maximum current limit for the SMU.'},
			'stepsInVDSPerDirection': 	{'type':'int',   'units':'#',  'default': 100,    'title':'Steps In VDS (per direction)', 'description':'Number of unique drain voltage steps in the sweep.'},
			'pointsPerVDS': 			{'type':'int',   'units':'#',  'default': 1,      'title':'Points Per VDS',               'description':'Number of measurements taken at each drain voltage step.'},
			'drainVoltageRamps':		{'type':'int',   'units':'#',  'default': 2,      'title':'Drain Voltage Ramps',          'description':'Number of times to loop through drain voltage values.'},
			'isFastSweep': 				{'type':'bool',                'default': False,  'title':'Fast Sweep',                   'description':'Use internal SMU timer to measure a faster sweep.'},
			'fastSweepSpeed':			{'type':'int',   'units':'Hz', 'default': 1000,   'title':'Fast Sweep Speed',             'description':'Frequency of SMU internal timer.'},
		},
		'BurnOut':{
			'dependencies':					{'ignore':True, 'value':[]},
			'saveFileName': 				{'type':'constant', 'default': 'BurnOut', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'pointsPerRamp': 				{'type':'int',   'units':'#', 'default': 50,   'title':'Points Per Ramp',               'description':''},
			'pointsPerHold': 				{'type':'int',   'units':'#', 'default': 50,   'title':'Points Per Hold',               'description':''},
			'complianceCurrent':			{'type':'float', 'units':'V', 'default': 2e-3, 'title':'Compliance Current',            'description':''},
			'thresholdProportion':			{'type':'float', 'units':'',  'default': 0.92, 'title':'Threshold Proportion',          'description':''},
			'minimumAppliedDrainVoltage': 	{'type':'float', 'units':'V', 'default': 1.1,  'title':'Minimum Applied Drain Voltage', 'description':''},
			'gateVoltageSetPoint':			{'type':'float', 'units':'V', 'default': 15.0, 'title':'Gate Voltage',                  'description':''},
			'drainVoltageMaxPoint':			{'type':'float', 'units':'V', 'default': 5,    'title':'Drain Voltage Max Point',       'description':''},
			'drainVoltagePlateaus': 		{'type':'int',   'units':'#', 'default': 5,    'title':'Drain Voltage Plateaus',        'description':''}, 
		},
		'StaticBias':{
			'dependencies':					{'ignore':True, 'value':[]},
			'saveFileName': 				{'type':'constant', 'default':'StaticBias', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'gateVoltageSetPoint': 			{'type':'float', 'units':'V', 'default': 0,      'title':'Gate Voltage Set Point',          'description':'Gate voltage value.'},
			'drainVoltageSetPoint':			{'type':'float', 'units':'V', 'default': 0.5,    'title':'Drain Voltage Set Point',         'description':'Drain voltage value.'},
			'totalBiasTime': 				{'type':'float', 'units':'s', 'default': 60,     'title':'Total Bias Time',                 'description':'Total time to apply voltages.'},
			'measurementTime': 				{'type':'float', 'units':'s', 'default': 10,     'title':'Measurement Time',                'description':'Time between measurements.'},
			'complianceCurrent': 			{'type':'float', 'units':'A', 'default': 100e-6, 'title':'Compliance Current',              'description':'Maximum current limit for the SMU.'},
			'delayBeforeMeasurementsBegin': {'type':'float', 'units':'s', 'default': 0,      'title':'Delay Before Measurements Begin', 'description':'Delay after applying voltages before taking the first measurement.'},
			'gateVoltageWhenDone':  		{'type':'float', 'units':'V', 'default': 0,      'title':'Gate Voltage When Done',          'description':'When finished, ramp gate voltage to this value.'},
			'drainVoltageWhenDone': 		{'type':'float', 'units':'V', 'default': 0,      'title':'Drain Voltage When Done',         'description':'When finished, ramp drain voltage to this value.'},
			'floatChannelsWhenDone': 		{'type':'bool',  			  'default': False,  'title':'Float Channels When Done',        'description':'When finished, float the drain and gate voltages.'},
			'delayWhenDone': 				{'type':'float', 'units':'s', 'default': 0,      'title':'Delay When Done',                 'description':'When finished, time to hold gate and drain voltages at their final value.'},
		},
		'FlowStaticBias':{
			'dependencies':					{'ignore':True, 'value':[]},
			'saveFileName': 				{'type':'constant', 'default':'FlowStaticBias', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'measurementTime': 				{'type':'float', 'units':'s', 'default': 10,     'title':'Measurement Time',                'description':''},
			'flowDurations':				{'type':'array', 'units':'s', 'default': [],     'title':'Flow Durations',                  'description':'Duration of flow for each pump, in array format'},
			'subCycleDurations':			{'type':'array', 'units':'s', 'default': [],     'title':'Subcycle Durations',              'description':'Duration of submersion, in array format'},
			'pumpPins':						{'type':'array', 'units':'#', 'default': [],     'title':'Digital Pins',                    'description':'digital pins, in array format'},
			'cycleCount':					{'type':'int',   'units':'#', 'default': 3,      'title':'Cycle Count',                     'description':'number of times all environments are exchanged (i.e: period of experiment)'},
			'solutions':					{'type':'array', 'units':'',  'default': [],     'title':'Solution Environments',           'description':''},
			'complianceCurrent': 			{'type':'float', 'units':'A', 'default': 100e-6, 'title':'Compliance Current',              'description':''},
			'delayBeforeMeasurementsBegin': {'type':'float', 'units':'s', 'default': 0,      'title':'Delay Before Measurements Begin', 'description':''},
			'gateVoltageSetPoint': 			{'type':'float', 'units':'V', 'default': 0,      'title':'Gate Voltage Set Point',          'description':''},
			'drainVoltageSetPoint':			{'type':'float', 'units':'V', 'default': 0.5,    'title':'Drain Voltage Set Point',         'description':''},
			'gateVoltageWhenDone':  		{'type':'float', 'units':'V', 'default': 0,      'title':'Gate Voltage When Done',          'description':''},
			'drainVoltageWhenDone': 		{'type':'float', 'units':'V', 'default': 0,      'title':'Drain Voltage When Done',         'description':''},
			'floatChannelsWhenDone': 		{'type':'bool',               'default': False,  'title':'Float Channels When Done',        'description':''},
			'delayWhenDone': 				{'type':'float', 'units':'s', 'default': 0,      'title':'Delay When Done',                 'description':''} 
		},
		'AutoBurnOut':{
			'dependencies':					{'ignore':True, 'value':['BurnOut']},
			'targetOnOffRatio': 			{'type':'float', 'units':'',  'default': 80,  'title':'Target On Off Ratio',            'description':''},
			'limitBurnOutsAllowed': 		{'type':'int',   'units':'#', 'default': 8,   'title':'Limit Burn Outs Allowed',        'description':''},
			'limitOnOffRatioDegradation': 	{'type':'float', 'units':'V', 'default': 0.7, 'title':'Limit On Off Ratio Degradation', 'description':''} 
		},
		'AutoGateSweep':{
			'dependencies':					{'ignore':True, 'value':['GateSweep']},
			'sweepsPerVDS': 				{'type':'int',   'units':'#', 'default': 3,     'title':'Sweeps Per VDS',           'description':''},
			'drainVoltageSetPoints': 		{'type':'array', 'units':'V', 'default': [],    'title':'Drain Voltage Set Points', 'description':''},
			'delayBetweenSweeps': 			{'type':'float', 'units':'s', 'default': 2,     'title':'Delay Between Sweeps',     'description':''},
			'timedSweepStarts': 			{'type':'bool',               'default': False, 'title':'Timed Sweep Starts',       'description':''} 
		},
		'AutoDrainSweep':{
			'dependencies': 				{'ignore':True, 'value':['DrainSweep']},
			'sweepsPerVGS': 				{'type':'int',   'units':'#', 'default': 1,              'title':'Sweeps Per VGS',          'description':''},
			'gateVoltageSetPoints':			{'type':'array', 'units':'V', 'default': [-0.5, 0, 0.5], 'title':'Gate Voltage Set Points', 'description':''},
			'delayBetweenSweeps': 			{'type':'float', 'units':'s', 'default': 0,              'title':'Delay Between Sweeps',    'description':''},
			'timedSweepStarts': 			{'type':'bool',               'default': False,          'title':'Timed Sweep Starts',      'description':''} 
		},
		'AutoStaticBias':{
			'dependencies': 						{'ignore':True, 'value':['StaticBias','GateSweep']},
			'numberOfStaticBiases': 				{'type':'int',   'units':'#', 'default': 1,     'title':'Number Of Static Biases',                   'description':''},
			'doInitialGateSweep': 					{'type':'bool',               'default': True,  'title':'Do Initial Gate Sweep',                     'description':''},
			'applyGateSweepBetweenBiases': 			{'type':'bool',               'default': False, 'title':'Apply Gate Sweep Between Biases',           'description':''},
			'applyGateSweepBothBeforeAndAfter':		{'type':'bool',               'default': False, 'title':'Apply Gate Sweep Both Before And After',    'description':''},
			'delayBetweenBiases':					{'type':'float', 'units':'s', 'default': 0,     'title':'Delay Between Biases',                      'description':''},
			'firstDelayBeforeMeasurementsBegin':	{'type':'float', 'units':'s', 'default': 0,     'title':'First Delay Before Measurements Begin',     'description':''},
			'numberOfBiasesBetweenIncrements': 		{'type':'int',   'units':'#', 'default': 1,     'title':'Number Of Biases Between Increments',       'description':''},
			'biasTimeList':							{'type':'array', 'units':'s', 'default': [],    'title':'Bias Time List',                            'description':''},
			'incrementStaticGateVoltage': 			{'type':'float', 'units':'V', 'default': 0,     'title':'Increment Static Gate Voltage',             'description':''},
			'incrementStaticDrainVoltage': 			{'type':'float', 'units':'V', 'default': 0,     'title':'Increment Static Drain Voltage',            'description':''},
			'incrementGateVoltageWhenDone': 		{'type':'float', 'units':'V', 'default': 0,     'title':'Increment Gate Voltage When Done',          'description':''},
			'incrementDrainVoltageWhenDone':		{'type':'float', 'units':'V', 'default': 0,     'title':'Increment Drain Voltage When Done',         'description':''},
			'incrementDelayBeforeReapplyingVoltage':{'type':'float', 'units':'s', 'default': 0,     'title':'Increment Delay Before Reapplying Voltage', 'description':''},
			'shuffleDelaysBeforeReapplyingVoltage': {'type':'bool',               'default': False, 'title':'Shuffle Delays Before Reapplying Voltage',  'description':''} 
		},
		'AutoFlowStaticBias':{
			'dependencies': 						{'ignore':True, 'value':['FlowStaticBias','GateSweep']},
			'numberOfFlowStaticBiases': 			{'type':'int',   'units':'#', 'default': 1,     'title':'Number Of Flow Static Biases',              'description':''},
			'doInitialGateSweep': 					{'type':'bool',               'default': True,  'title':'Do Initial Gate Sweep',                     'description':''},
			'applyGateSweepBetweenBiases': 			{'type':'bool',               'default': False, 'title':'Apply Gate Sweep Between Biases',           'description':''},
			'applyGateSweepBothBeforeAndAfter':		{'type':'bool',               'default': False, 'title':'Apply Gate Sweep Both Before And After',    'description':''},
			'delayBetweenBiases':					{'type':'float', 'units':'s', 'default': 0,     'title':'Delay Between Biases',                      'description':''},
			'firstDelayBeforeMeasurementsBegin':	{'type':'float', 'units':'s', 'default': 0,     'title':'First Delay Before Measurements Begin',     'description':''},
			'numberOfBiasesBetweenIncrements': 		{'type':'int',   'units':'#', 'default': 1,     'title':'Number Of Biases Between Increments',       'description':''},
			'biasTimeList':							{'type':'array', 'units':'s', 'default': [],    'title':'Bias Time List',                            'description':''},
			'incrementStaticGateVoltage': 			{'type':'float', 'units':'V', 'default': 0,     'title':'Increment Static Gate Voltage',             'description':''},
			'incrementStaticDrainVoltage': 			{'type':'float', 'units':'V', 'default': 0,     'title':'Increment Static Drain Voltage',            'description':''},
			'incrementGateVoltageWhenDone': 		{'type':'float', 'units':'V', 'default': 0,     'title':'Increment Gate Voltage When Done',          'description':''},
			'incrementDrainVoltageWhenDone':		{'type':'float', 'units':'V', 'default': 0,     'title':'Increment Drain Voltage When Done',         'description':''},
			'incrementDelayBeforeReapplyingVoltage':{'type':'float', 'units':'s', 'default': 0,     'title':'Increment Delay Before Reapplying Voltage', 'description':''},
			'shuffleDelaysBeforeReapplyingVoltage': {'type':'bool',               'default': False, 'title':'Shuffle Delays Before Reapplying Voltage',  'description':''} 
		},
		'AFMControl':{
			'dependencies': 			{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default':'AFMControl', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'lines': 					{'type':'int',   'units':'#',  'default': 3,     'title':'Lines',                    'description':''},
			'scanRate': 				{'type':'int',   'units':'#',  'default': 1,     'title':'Scan Rate',                'description':''},
			'napOn': 					{'type':'bool',                'default': True,  'title':'Nap On',                   'description':''},
			'startOnFrameSwitch': 		{'type':'bool',                'default': False, 'title':'Start On Frame Switch',    'description':''},
			'drainVoltageSetPoint': 	{'type':'float', 'units':'V',  'default': 0.01,  'title':'Drain Voltage Set Point',  'description':''},
			'gateVoltageSetPoint': 		{'type':'float', 'units':'V',  'default': 0,     'title':'Gate Voltage Set Point',   'description':''},
			'complianceCurrent': 		{'type':'float', 'units':'A',  'default': 1e-6,  'title':'Compliance Current',       'description':''},
			'complianceVoltage': 		{'type':'float', 'units':'V',  'default': 10,    'title':'Compliance Voltage',       'description':''},
			'deviceMeasurementSpeed': 	{'type':'float', 'units':'Hz', 'default': 60,    'title':'Device Measurement Speed', 'description':''},
			'XYCableSwap':				{'type':'bool',                'default': False, 'title':'XYCable Swap',             'description':''} 
		},
		'SGMControl':{
			'dependencies': 				{'ignore':True, 'value':[]},
			'saveFileName': 				{'type':'constant', 'default':'AFMControl', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'lines': 						{'type':'int',   'units':'#',  'default': 3,     'title':'Lines',                          'description':''},
			'scanRate': 					{'type':'int',   'units':'#',  'default': 1,     'title':'Scan Rate',                      'description':''},
			'napOn': 						{'type':'bool',                'default': True,  'title':'Nap On',                         'description':''},
			'startOnFrameSwitch': 			{'type':'bool',                'default': False, 'title':'Start On Frame Switch',          'description':''},
			'drainVoltageSetPoint': 		{'type':'float', 'units':'V',  'default': 0.01,  'title':'Drain Voltage Set Point',        'description':''},
			'gateVoltageSetPoint': 			{'type':'float', 'units':'V',  'default': 0,     'title':'Gate Voltage Set Point',         'description':''},
			'complianceCurrent': 			{'type':'float', 'units':'A',  'default': 1e-6,  'title':'Compliance Current',             'description':''},
			'complianceVoltage': 			{'type':'float', 'units':'V',  'default': 10,    'title':'Compliance Voltage',             'description':''},
			'deviceMeasurementSpeed': 		{'type':'float', 'units':'Hz', 'default': 60,    'title':'Device Measurement Speed',       'description':''},
			'XYCableSwap':					{'type':'bool',                'default': False, 'title':'XYCable Swap',                   'description':''},
			'tracesToMeasure':				{'type':'int',   'units':'#',  'default': 1,     'title':'Traces To Measure',              'description':''},
			'scans':						{'type':'int',   'units':'#',  'default': 1,     'title':'Scans',                          'description':''},
			'delayBeforeApplyingVoltages':	{'type':'float', 'units':'s',  'default': 0,     'title':'Delay Before Applying Voltages', 'description':''} 
		},
		'Delay':{
			'dependencies': 			{'ignore':True, 'value':[]},
			'message':					{'type':'string',              'default': "",  'title':'Message',    'description':''},
			'delayTime':				{'type':'int',    'units':'s', 'default': 300, 'title':'Delay Time', 'description':''} 
		},
		'InverterSweep':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'InverterSweep', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'stepsInVINPerDirection': 	{'type':'int',   'units':'#', 'default': 100,    'title':'Steps In VINPer Direction',    'description':''},
			'pointsPerVIN': 			{'type':'int',   'units':'#', 'default': 1,      'title':'Points Per VIN',               'description':''},
			'inputVoltageRamps':		{'type':'int',   'units':'#', 'default': 2,      'title':'Input Voltage Ramps',          'description':''},
			'complianceCurrent':		{'type':'float', 'units':'A', 'default': 100e-6, 'title':'Compliance Current',           'description':''},
			'vddSupplyVoltageSetPoint':	{'type':'float', 'units':'V', 'default': 1.0,    'title':'Vdd Supply Voltage Set Point', 'description':''},
			'inputVoltageMinimum': 		{'type':'float', 'units':'V', 'default': 0.0,    'title':'Input Voltage Minimum',        'description':''},
			'inputVoltageMaximum': 		{'type':'float', 'units':'V', 'default': 1.0,    'title':'Input Voltage Maximum',        'description':''} 
		},
		'RapidBias':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'RapidBias', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'complianceCurrent':		{'type':'float',   'units':'A', 'default': 100e-6,   'title':'Compliance Current',       'description':''},
			'waveform': 				{'type':'string',               'default': 'square', 'title':'Waveform',                 'description':''},
			'drainVoltageSetPoints':	{'type':'array',   'units':'V', 'default': [0.05],   'title':'Drain Voltage Set Points', 'description':''},
			'gateVoltageSetPoints':		{'type':'array',   'units':'V', 'default': [0.0],    'title':'Gate Voltage Set Points',  'description':''},
			'measurementPoints':		{'type':'array',   'units':'#', 'default': [50],     'title':'Measurement Points',       'description':''},
			'averageOverPoints': 		{'type':'int',     'units':'#', 'default': 1,        'title':'Average Over Points',      'description':''},
			'maxStepInVDS': 			{'type':'float',   'units':'V', 'default': 0.025,    'title':'Max Step In VDS',          'description':''},
			'maxStepInVGS': 			{'type':'float',   'units':'V', 'default': 0.4,      'title':'Max Step In VGS',          'description':''},
			'startGrounded': 			{'type':'bool',                 'default': False,    'title':'Start Grounded',           'description':''} 
		},
		'NoiseCollection':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'NoiseCollection', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'measurementSpeed':	 		{'type':'float', 'units':'Hz', 'default': 10e3,   'title':'Measurement Speed',  'description':''},
			'points':			 		{'type':'int',   'units':'#',  'default': 10e3,   'title':'Points',             'description':''},
			'complianceCurrent':		{'type':'float', 'units':'A',  'default': 100e-6, 'title':'Compliance Current', 'description':''},
			'gateVoltage':				{'type':'float', 'units':'V',  'default': 0,      'title':'Gate Voltage',       'description':''},
			'drainVoltage':				{'type':'float', 'units':'V',  'default': 0.1,    'title':'Drain Voltage',      'description':''} 
		},
		'NoiseGrid':{
			'dependencies':				{'ignore':True, 'value':['NoiseCollection']},
			'saveFileName': 			{'type':'constant', 'default': 'NoiseGrid', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'gateVoltages':				{'type':'array', 'units':'V', 'default': [-0.5,0,0.5],     'title':'Gate Voltages',  'description':''},
			'drainVoltages':			{'type':'array', 'units':'V', 'default': [0.05,0.10,0.15], 'title':'Drain Voltages', 'description':''},
			'groundingTime':			{'type':'float', 'units':'s', 'default': 1,                'title':'Grounding Time', 'description':''} 
		}
	},
	'Results':{
		
	},
	'Computed':{
		
	},
	'SensorData':{
		
	},
	'Identifiers':{
		'user':   {'type':'string', 'default':'', 'title':'User',    'description':''},
		'project':{'type':'string', 'default':'', 'title':'Project', 'description':''},
		'wafer':  {'type':'string', 'default':'', 'title':'Wafer',   'description':''},
		'chip':   {'type':'string', 'default':'', 'title':'Chip',    'description':''},
		'device': {'type':'string', 'default':'', 'title':'Device',  'description':''},
		'step':   {'type':'int',    'default': 0, 'title':'Step',    'description':''},
	},
	'MeasurementSystem':{
		'systemType': {'type':'choice', 'choices':['single', 'standalone', 'double'], 'default':['single', 'standalone', 'double'][1], 'title':'System Type', 'description':''},
		'systems': {},
		'deviceRange': {'type':'array', 'choices':["1-2", "2-3", "3-4", "5-6", "6-7", "7-8", "9-10", "10-11", "11-12", "13-14", "14-15", "15-16", "19-20", "21-22", "27-28", "29-30", "30-31", "31-32", "33-34", "34-35", "35-36", "37-38", "38-39", "39-40", "41-42", "42-43", "43-44", "45-46", "46-47", "47-48", "51-52", "53-54", "59-60", "61-62", "62-63", "63-64"], 'default':[], 'title':'Device Range', 'description':''} 
	},
	'dataFolder': {'type':'string', 'default':'../../AutexysData/', 'title':'Data Folder', 'description':''},
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



