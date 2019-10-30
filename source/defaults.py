

default_parameters = {
	'runType': {'type': 'keyChoice', 'ChoiceFrom': 'runConfigs', 'default':''},
	'Identifiers':{
		'user':   {'type':'string', 'default':'', 'title':'User',    'description':''},
		'project':{'type':'string', 'default':'', 'title':'Project', 'description':''},
		'wafer':  {'type':'string', 'default':'', 'title':'Wafer',   'description':''},
		'chip':   {'type':'string', 'default':'', 'title':'Chip',    'description':''},
		'device': {'type':'string', 'default':'', 'title':'Device',  'description':''},
		'step':   {'type':'int',    'default': 0, 'title':'Step',    'description':''},
	},
	'runConfigs': {
		'GateSweep':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'GateSweep', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'gateVoltageMinimum': 		{'type':'float', 'essential':True, 'units':'V',  'default': -1,     'title':'Gate Voltage Start',           'description':'Gate voltage starting value.'},
			'gateVoltageMaximum': 		{'type':'float', 'essential':True, 'units':'V',  'default': 1,      'title':'Gate Voltage End',             'description':'Gate voltage final value.'}, 
			'drainVoltageSetPoint':		{'type':'float', 'essential':True, 'units':'V',  'default': 0.5,    'title':'Drain Voltage',                'description':'Drain voltage value.'},
			'complianceCurrent':		{'type':'float',                   'units':'A',  'default': 100e-6, 'title':'Compliance Current',           'description':'Maximum current limit for the SMU.'},
			'stepsInVGSPerDirection': 	{'type':'int',   'essential':True, 'units':'#',  'default': 100,    'title':'Steps In VGS (per direction)', 'description':'Number of unique gate voltage steps in the sweep.'},
			'pointsPerVGS': 			{'type':'int',                     'units':'#',  'default': 1,      'title':'Measurements per VGS',         'description':'Number of measurements taken at each gate voltage step.'},
			'gateVoltageRamps':			{'type':'int',                     'units':'#',  'default': 2,      'title':'Gate Voltage Ramps',           'description':'Number of times to loop through gate voltage values.'},
			'delayBetweenMeasurements': {'type':'float',                   'units':'s',  'default': 0,      'title':'Delay Between Measurements',   'description':'Duration of time to delay after taking a measurement.'},
			'isFastSweep': 				{'type':'bool',                                  'default': False,  'title':'Fast Sweep',                   'description':'Use internal SMU timer to measure a faster sweep.'},
			'fastSweepSpeed':			{'type':'int',                     'units':'Hz', 'default': 1000,   'title':'Fast Sweep Speed',             'description':'Frequency of SMU internal timer.'},
		},
		'DrainSweep':{
			'dependencies': 			{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default':'DrainSweep', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'drainVoltageMinimum': 		{'type':'float', 'essential':True, 'units':'V',  'default': 0,      'title':'Drain Voltage Start',          'description':'Drain voltage starting value.'},
			'drainVoltageMaximum': 		{'type':'float', 'essential':True, 'units':'V',  'default': 1,      'title':'Drain Voltage End',            'description':'Drain voltage final value.'}, 
			'gateVoltageSetPoint':		{'type':'float', 'essential':True, 'units':'V',  'default': 0,      'title':'Gate Voltage',                 'description':'Gate voltage value.'},
			'complianceCurrent':		{'type':'float',                   'units':'A',  'default': 100e-6, 'title':'Compliance Current',           'description':'Maximum current limit for the SMU.'},
			'stepsInVDSPerDirection': 	{'type':'int',   'essential':True, 'units':'#',  'default': 100,    'title':'Steps In VDS (per direction)', 'description':'Number of unique drain voltage steps in the sweep.'},
			'pointsPerVDS': 			{'type':'int',                     'units':'#',  'default': 1,      'title':'Measurements per VDS',         'description':'Number of measurements taken at each drain voltage step.'},
			'drainVoltageRamps':		{'type':'int',                     'units':'#',  'default': 2,      'title':'Drain Voltage Ramps',          'description':'Number of times to loop through drain voltage values.'},
			'delayBetweenMeasurements': {'type':'float',                   'units':'s',  'default': 0,      'title':'Delay Between Measurements',   'description':'Duration of time to delay after taking a measurement.'},
			'isFastSweep': 				{'type':'bool',                                  'default': False,  'title':'Fast Sweep',                   'description':'Use internal SMU timer to measure a faster sweep.'},
			'fastSweepSpeed':			{'type':'int',                     'units':'Hz', 'default': 1000,   'title':'Fast Sweep Speed',             'description':'Frequency of SMU internal timer.'},
		},
		'InverterSweep':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'InverterSweep', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'inputVoltageMinimum': 		{'type':'float', 'essential':True, 'units':'V', 'default': 0.0,    'title':'Input Voltage Minimum',        'description':'Input voltage starting value.'},
			'inputVoltageMaximum': 		{'type':'float', 'essential':True, 'units':'V', 'default': 1.0,    'title':'Input Voltage Maximum',        'description':'Input voltage final value.'},
			'vddSupplyVoltageSetPoint':	{'type':'float', 'essential':True, 'units':'V', 'default': 1.0,    'title':'Vdd Supply Voltage Set Point', 'description':'Inverter power supply voltage.'}, 
			'complianceCurrent':		{'type':'float',                   'units':'A', 'default': 100e-6, 'title':'Compliance Current',           'description':'Maximum current limit for the SMU.'},
			'stepsInVINPerDirection': 	{'type':'int',                     'units':'#', 'default': 100,    'title':'Steps In VIN (per Direction)', 'description':'Number of unique input voltage steps in the sweep.'},
			'pointsPerVIN': 			{'type':'int',                     'units':'#', 'default': 1,      'title':'Measurements Per VIN',         'description':'Number of measurements taken at each input voltage step.'},
			'inputVoltageRamps':		{'type':'int',                     'units':'#', 'default': 2,      'title':'Input Voltage Ramps',          'description':'Number of times to loop through input voltage values.'},
			'delayBetweenMeasurements': {'type':'float',                   'units':'s', 'default': 0,      'title':'Delay Between Measurements',   'description':'Duration of time to delay after taking a measurement.'},
		},
		'BurnOut':{
			'dependencies':					{'ignore':True, 'value':[]},
			'saveFileName': 				{'type':'constant', 'default': 'BurnOut', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'pointsPerRamp': 				{'type':'int',                     'units':'#', 'default': 50,   'title':'Points Per Ramp',               'description':''},
			'pointsPerHold': 				{'type':'int',                     'units':'#', 'default': 50,   'title':'Points Per Hold',               'description':''},
			'complianceCurrent':			{'type':'float',                   'units':'V', 'default': 2e-3, 'title':'Compliance Current',            'description':''},
			'thresholdProportion':			{'type':'float',                   'units':'',  'default': 0.92, 'title':'Threshold Proportion',          'description':''},
			'minimumAppliedDrainVoltage': 	{'type':'float',                   'units':'V', 'default': 1.1,  'title':'Minimum Applied Drain Voltage', 'description':''},
			'gateVoltageSetPoint':			{'type':'float', 'essential':True, 'units':'V', 'default': 15,   'title':'Gate Voltage',                  'description':''},
			'drainVoltageMaxPoint':			{'type':'float', 'essential':True, 'units':'V', 'default': 5,    'title':'Drain Voltage Max Point',       'description':''},
			'drainVoltagePlateaus': 		{'type':'int',                     'units':'#', 'default': 5,    'title':'Drain Voltage Plateaus',        'description':''}, 
		},
		'StaticBias':{
			'dependencies':					{'ignore':True, 'value':[]},
			'saveFileName': 				{'type':'constant', 'default':'StaticBias', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'gateVoltageSetPoint': 			{'type':'float', 'essential':True, 'units':'V', 'default': 0,      'title':'Gate Voltage Set Point',          'description':'Gate voltage value.'},
			'drainVoltageSetPoint':			{'type':'float', 'essential':True, 'units':'V', 'default': 0.5,    'title':'Drain Voltage Set Point',         'description':'Drain voltage value.'},
			'totalBiasTime': 				{'type':'float', 'essential':True, 'units':'s', 'default': 60,     'title':'Total Bias Time',                 'description':'Total time to apply voltages.'},
			'measurementTime': 				{'type':'float', 'essential':True, 'units':'s', 'default': 1,      'title':'Measurement Time',                'description':'Interval over which to average each measurement.'},
			'complianceCurrent': 			{'type':'float',                   'units':'A', 'default': 100e-6, 'title':'Compliance Current',              'description':'Maximum current limit for the SMU.'},
			'delayBeforeMeasurementsBegin': {'type':'float',                   'units':'s', 'default': 0,      'title':'Delay Before Measurements Begin', 'description':'Delay after applying voltages before taking the first measurement.'},
			'gateVoltageWhenDone':  		{'type':'float',                   'units':'V', 'default': 0,      'title':'Gate Voltage When Done',          'description':'When finished, ramp gate voltage to this value.'},
			'drainVoltageWhenDone': 		{'type':'float',                   'units':'V', 'default': 0,      'title':'Drain Voltage When Done',         'description':'When finished, ramp drain voltage to this value.'},
			'floatChannelsWhenDone': 		{'type':'bool',  			                    'default': False,  'title':'Float Channels When Done',        'description':'When finished, float the drain and gate voltages.'},
			'delayWhenDone': 				{'type':'float',                   'units':'s', 'default': 0,      'title':'Delay When Done',                 'description':'When finished, time to hold gate and drain voltages at their final value.'},
		},
		'FlowStaticBias':{
			'dependencies':					{'ignore':True, 'value':[]},
			'saveFileName': 				{'type':'constant', 'default':'FlowStaticBias', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'measurementTime': 				{'type':'float', 'essential':True, 'units':'s', 'default': 10,     'title':'Measurement Time',                'description':'Interval over which to average each measurement.'},
			'flowDurations':				{'type':'array', 'essential':True, 'units':'s', 'default': [],     'title':'Flow Durations',                  'description':'Duration of flow for each pump, in array format'},
			'subCycleDurations':			{'type':'array', 'essential':True, 'units':'s', 'default': [],     'title':'Subcycle Durations',              'description':'Duration of submersion, in array format'},
			'pumpPins':						{'type':'array',                   'units':'#', 'default': [],     'title':'Forward Digital Pins',            'description':'forward flow digital pins'},
			'reversePumpPins':				{'type':'array', 				   'units':'#', 'default': [],     'title':'Reverse Digital Pins', 			  'description':'reverse flow digital pins corresponding to pumpPins; reverse pumps have hard-set flush times'},
			'flushPins':					{'type':'array', 				   'units':'#', 'default': [],     'title':'Flush Pins', 					  'description':'digital pin for flushing pin: [forward pin, reverse pin]'},
			'cycleCount':					{'type':'int',   'essential':True, 'units':'#', 'default': 3,      'title':'Cycle Count',                     'description':'number of times all environments are exchanged (i.e: period of experiment)'},
			'solutions':					{'type':'array', 'essential':True, 'units':'',  'default': [],     'title':'Solution Environments',           'description':''},
			'complianceCurrent': 			{'type':'float',                   'units':'A', 'default': 100e-6, 'title':'Compliance Current',              'description':'Maximum current limit for the SMU.'},
			'gateVoltageSetPoint': 			{'type':'float', 'essential':True, 'units':'V', 'default': 0,      'title':'Gate Voltage Set Point',          'description':'Gate voltage value.'},
			'drainVoltageSetPoint':			{'type':'float', 'essential':True, 'units':'V', 'default': 0.5,    'title':'Drain Voltage Set Point',         'description':'Drain voltage value.'},
			'gateVoltageWhenDone':  		{'type':'float',                   'units':'V', 'default': 0,      'title':'Gate Voltage When Done',          'description':'When finished, ramp gate voltage to this value.'},
			'drainVoltageWhenDone': 		{'type':'float',                   'units':'V', 'default': 0,      'title':'Drain Voltage When Done',         'description':'When finished, ramp drain voltage to this value.'},
			'floatChannelsWhenDone': 		{'type':'bool',                                 'default': False,  'title':'Float Channels When Done',        'description':'When finished, float the drain and gate voltages.'},
			'delayWhenDone': 				{'type':'float',                   'units':'s', 'default': 0,      'title':'Delay When Done',                 'description':'When finished, time to hold gate and drain voltages at their final value.'}, 
		},
		'AutoBurnOut':{
			'dependencies':					{'ignore':True, 'value':['BurnOut']},
			'targetOnOffRatio': 			{'type':'float', 'essential':True, 'units':'',  'default': 80,  'title':'Target On Off Ratio',            'description':'Stop burn out when the device on-off ratio increases above this absolute value.'},
			'limitOnOffRatioDegradation': 	{'type':'float',                   'units':'',  'default': 0.7, 'title':'Limit On Off Ratio Degradation', 'description':'Stop burn out if device on-off ratio decreases by this factor.'}, 
			'limitBurnOutsAllowed': 		{'type':'int',   'essential':True, 'units':'#', 'default': 8,   'title':'Limit Burn Outs Allowed',        'description':'Stop burn out after this many tries.'},
		},
		'AutoGateSweep':{
			'dependencies':					{'ignore':True, 'value':['GateSweep']},
			'sweepsPerVDS': 				{'type':'int',   'essential':True, 'units':'#', 'default': 3,     'title':'Sweeps Per VDS',           'description':'Number of gate sweeps to take at each value of drain voltage.'},
			'drainVoltageSetPoints': 		{'type':'array', 'essential':True, 'units':'V', 'default': [],    'title':'Drain Voltage Set Points', 'description':'List of drain voltage values to do sweeps at.'},
			'delayBetweenSweeps': 			{'type':'float',                   'units':'s', 'default': 2,     'title':'Delay Between Sweeps',     'description':'Delay between each sweep.'},
			'timedSweepStarts': 			{'type':'bool',                                 'default': False, 'title':'Timed Sweeps',       	  'description':'When enabled, the delay between sweeps is dynamically reduced by the amount of time the sweep took.'}, 
		},
		'AutoDrainSweep':{
			'dependencies': 				{'ignore':True, 'value':['DrainSweep']},
			'sweepsPerVGS': 				{'type':'int',   'essential':True, 'units':'#', 'default': 1,          'title':'Sweeps Per VGS',          'description':'Number of drain sweeps to take at each value of gate voltage.'},
			'gateVoltageSetPoints':			{'type':'array', 'essential':True, 'units':'V', 'default': [-1, 0, 1], 'title':'Gate Voltage Set Points', 'description':'List of gate voltage values to do sweeps at.'},
			'delayBetweenSweeps': 			{'type':'float',                   'units':'s', 'default': 2,          'title':'Delay Between Sweeps',    'description':'Delay between each sweep.'},
			'timedSweepStarts': 			{'type':'bool',                                 'default': False,      'title':'Timed Sweep Starts',      'description':'When enabled, the delay between sweeps is dynamically reduced by the amount of time the sweep took.'}, 
		},
		'AutoStaticBias':{
			'dependencies': 						{'ignore':True, 'value':['StaticBias','GateSweep']},
			'numberOfStaticBiases': 				{'type':'int',   'essential':True, 'units':'#', 'default': 1,     'title':'Number Of Static Biases',          'description':'Number of successive static bias trials.'},
			'doInitialGateSweep': 					{'type':'bool',  'essential':True,              'default': True,  'title':'Initial Gate Sweep',               'description':'When enabled, begin the experiment with a gate sweep.'},
			'applyGateSweepBetweenBiases': 			{'type':'bool',  'essential':True,              'default': False, 'title':'Gate Sweep Between Biases',        'description':'When enabled, perform one gate sweep between each static bias.'},
			'applyGateSweepBothBeforeAndAfter':		{'type':'bool',                                 'default': False, 'title':'Gate Sweep Both Before And After', 'description':'When enabled, perform two gate sweeps between each static bias.'},
			'delayBetweenBiases':					{'type':'float',                   'units':'s', 'default': 0,     'title':'Delay Between Biases',             'description':'Length of time to delay between each static bias.'},
			'biasTimeList':							{'type':'array', 'essential':True, 'units':'s', 'default': [],    'title':'Bias Time List',                   'description':'List of total bias times for each static bias.'},
			'gateVoltageSetPointList': 				{'type':'array', 'essential':True, 'units':'V', 'default': [],    'title':'Gate Voltage List',                'description':'List of gate voltages for each static bias.'},
			'drainVoltageSetPointList': 			{'type':'array', 'essential':True, 'units':'V', 'default': [],    'title':'Drain Voltage List',               'description':'List of drain voltages for each static bias.'},
			'gateVoltageWhenDoneList': 				{'type':'array',                   'units':'V', 'default': [],    'title':'Gate Voltage When Done List',      'description':'List of ending gate voltages for each static bias.'},
			'drainVoltageWhenDoneList':				{'type':'array',                   'units':'V', 'default': [],    'title':'Drain Voltage When Done List',     'description':'List of ending drain voltages for each static bias.'},
			'delayWhenDoneList':					{'type':'array',                   'units':'s', 'default': [],    'title':'Delay When Done List',             'description':'List of ending hold times for each static bias.'},
			'firstDelayBeforeMeasurementsBegin':	{'type':'float',                   'units':'s', 'default': 0,     'title':'Delay Before Measurements Begin',  'description':'Initial delay after first applying voltages before measurements begin.'},
		},
		'AutoFlowStaticBias':{
			'dependencies': 						{'ignore':True, 'value':['FlowStaticBias','GateSweep']},
			'numberOfFlowStaticBiases': 			{'type':'int',   'essential':True, 'units':'#', 'default': 1,     'title':'Number Of Flow Static Biases',              'description':''},
			'doInitialGateSweep': 					{'type':'bool',  'essential':True,              'default': True,  'title':'Do Initial Gate Sweep',                     'description':''},
			'applyGateSweepBetweenBiases': 			{'type':'bool',  'essential':True,              'default': False, 'title':'Apply Gate Sweep Between Biases',           'description':''},
			'applyGateSweepBothBeforeAndAfter':		{'type':'bool',                                 'default': False, 'title':'Apply Gate Sweep Both Before And After',    'description':''},
			'delayBetweenBiases':					{'type':'float',                   'units':'s', 'default': 0,     'title':'Delay Between Biases',                      'description':''},
			'firstDelayBeforeMeasurementsBegin':	{'type':'float',                   'units':'s', 'default': 0,     'title':'First Delay Before Measurements Begin',     'description':''},
			'numberOfBiasesBetweenIncrements': 		{'type':'int',   'essential':True, 'units':'#', 'default': 1,     'title':'Number Of Biases Between Increments',       'description':''},
			'biasTimeList':							{'type':'array', 'essential':True, 'units':'s', 'default': [],    'title':'Bias Time List',                            'description':''},
			'incrementStaticGateVoltage': 			{'type':'float', 'essential':True, 'units':'V', 'default': 0,     'title':'Increment Static Gate Voltage',             'description':''},
			'incrementStaticDrainVoltage': 			{'type':'float', 'essential':True, 'units':'V', 'default': 0,     'title':'Increment Static Drain Voltage',            'description':''},
			'incrementGateVoltageWhenDone': 		{'type':'float',                   'units':'V', 'default': 0,     'title':'Increment Gate Voltage When Done',          'description':''},
			'incrementDrainVoltageWhenDone':		{'type':'float',                   'units':'V', 'default': 0,     'title':'Increment Drain Voltage When Done',         'description':''},
			'incrementDelayBeforeReapplyingVoltage':{'type':'float',                   'units':'s', 'default': 0,     'title':'Increment Delay Before Reapplying Voltage', 'description':''},
		},
		'AFMControl':{
			'dependencies': 			{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default':'AFMControl', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'lines': 					{'type':'int',   'essential':True, 'units':'#',  'default': 3,     'title':'Lines',                    'description':''},
			'scanRate': 				{'type':'int',   'essential':True, 'units':'#',  'default': 1,     'title':'Scan Rate',                'description':''},
			'napOn': 					{'type':'bool',  'essential':True,               'default': True,  'title':'Nap On',                   'description':''},
			'startOnFrameSwitch': 		{'type':'bool',                                  'default': False, 'title':'Start On Frame Switch',    'description':''},
			'drainVoltageSetPoint': 	{'type':'float', 'essential':True, 'units':'V',  'default': 0.01,  'title':'Drain Voltage Set Point',  'description':''},
			'gateVoltageSetPoint': 		{'type':'float', 'essential':True, 'units':'V',  'default': 0,     'title':'Gate Voltage Set Point',   'description':''},
			'complianceCurrent': 		{'type':'float',                   'units':'A',  'default': 1e-6,  'title':'Compliance Current',       'description':''},
			'complianceVoltage': 		{'type':'float',                   'units':'V',  'default': 10,    'title':'Compliance Voltage',       'description':''},
			'deviceMeasurementSpeed': 	{'type':'float',                   'units':'Hz', 'default': 60,    'title':'Device Measurement Speed', 'description':''},
			'XYCableSwap':				{'type':'bool',                                  'default': False, 'title':'XYCable Swap',             'description':''}, 
		},
		'SGMControl':{
			'dependencies': 				{'ignore':True, 'value':[]},
			'saveFileName': 				{'type':'constant', 'default':'AFMControl', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'lines': 						{'type':'int',   'essential':True, 'units':'#',  'default': 3,     'title':'Lines',                          'description':''},
			'scanRate': 					{'type':'int',   'essential':True, 'units':'#',  'default': 1,     'title':'Scan Rate',                      'description':''},
			'napOn': 						{'type':'bool',  'essential':True,               'default': True,  'title':'Nap On',                         'description':''},
			'startOnFrameSwitch': 			{'type':'bool',                                  'default': False, 'title':'Start On Frame Switch',          'description':''},
			'drainVoltageSetPoint': 		{'type':'float', 'essential':True, 'units':'V',  'default': 0.01,  'title':'Drain Voltage Set Point',        'description':''},
			'gateVoltageSetPoint': 			{'type':'float', 'essential':True, 'units':'V',  'default': 0,     'title':'Gate Voltage Set Point',         'description':''},
			'complianceCurrent': 			{'type':'float',                   'units':'A',  'default': 1e-6,  'title':'Compliance Current',             'description':''},
			'complianceVoltage': 			{'type':'float',                   'units':'V',  'default': 10,    'title':'Compliance Voltage',             'description':''},
			'deviceMeasurementSpeed': 		{'type':'float',                   'units':'Hz', 'default': 60,    'title':'Device Measurement Speed',       'description':''},
			'XYCableSwap':					{'type':'bool',                                  'default': False, 'title':'XYCable Swap',                   'description':''},
			'tracesToMeasure':				{'type':'int',                     'units':'#',  'default': 1,     'title':'Traces To Measure',              'description':''},
			'scans':						{'type':'int',                     'units':'#',  'default': 1,     'title':'Scans',                          'description':''},
			'delayBeforeApplyingVoltages':	{'type':'float',                   'units':'s',  'default': 0,     'title':'Delay Before Applying Voltages', 'description':''}, 
		},
		'Delay':{
			'dependencies': 			{'ignore':True, 'value':[]},
			'delayTime':				{'type':'int',    'essential':True, 'units':'s', 'default': 60,                       'title':'Delay Time', 'description':'Duration of delay.'}, 
			'message':					{'type':'string',                                'default': "Delaying next test...",  'title':'Message',    'description':'Message to print at the start of delay.'},
		},
		'RapidBias':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'RapidBias', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'waveform': 				{'type':'choice', 'essential':True,              'default': 'square',         'title':'Waveform',                 'choices':['square', 'triangle', 'sine'], 'description':'Type of waveform of voltages to apply.'},
			'drainVoltageSetPoints':	{'type':'array',  'essential':True, 'units':'V', 'default': [0.1],   		  'title':'Drain Voltage Key Points', 'description':'List of drain voltages that the generated VDS waveform must include.'},
			'gateVoltageSetPoints':		{'type':'array',  'essential':True, 'units':'V', 'default': [0,  1, 0, 1, 0], 'title':'Gate Voltage Key Points',  'description':'List of gate voltages that the generated VGS waveform must include.'},
			'measurementPoints':		{'type':'array',  'essential':True, 'units':'#', 'default': [50,50,50,50,50], 'title':'Measurement Points',       'description':'List of the number of measurements to take in each segment of the waveform. The size of this list should match the size of the longest key point list.'},
			'complianceCurrent':		{'type':'float',                    'units':'A', 'default': 100e-6,           'title':'Compliance Current',       'description':'Maximum current limit for the SMU.'},
			'averageOverPoints': 		{'type':'int',                      'units':'#', 'default': 1,                'title':'Average Over Points',      'description':'When greater than one, consecutive measurements are averaged together to reduce size of saved data.'},
			'maxStepInVDS': 			{'type':'float',                    'units':'V', 'default': 0.025,            'title':'Max Step In VDS',          'description':'Maximum allowable step used in generating the drain voltage waveform.'},
			'maxStepInVGS': 			{'type':'float',                    'units':'V', 'default': 0.4,              'title':'Max Step In VGS',          'description':'Maximum allowable step used in generating the gate voltage waveform.'},
			'startGrounded': 			{'type':'bool',                                  'default': False,            'title':'Start Grounded',           'description':'When enabled, terminals start as grounded so that you can see all of the starting transients and miss nothing.'}, 
		},
		'StaticCurrent':{
			'dependencies':					{'ignore':True, 'value':[]},
			'saveFileName': 				{'type':'constant', 'default':'StaticCurrent', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'gateCurrentSetPoint': 			{'type':'float', 'essential':True, 'units':'A', 'default': 0,      'title':'Gate Current Set Point',          'description':'Gate current value.'},
			'drainCurrentSetPoint':			{'type':'float', 'essential':True, 'units':'A', 'default': 0,      'title':'Drain Current Set Point',         'description':'Drain current value.'},
			'totalBiasTime': 				{'type':'float', 'essential':True, 'units':'s', 'default': 60,     'title':'Total Bias Time',                 'description':'Total time to flow current through the device.'},
			'measurementTime': 				{'type':'float', 'essential':True, 'units':'s', 'default': 1,      'title':'Measurement Time',                'description':'Interval over which to average each measurement.'},
			'complianceVoltage': 			{'type':'float',                   'units':'V', 'default': 5, 	   'title':'Compliance Voltage',              'description':'Maximum voltage limit for the SMU.'},
			'delayBeforeMeasurementsBegin': {'type':'float',                   'units':'s', 'default': 0,      'title':'Delay Before Measurements Begin', 'description':'Delay after applying voltages before taking the first measurement.'},
			'gateCurrentWhenDone':  		{'type':'float',                   'units':'A', 'default': 0,      'title':'Gate Current When Done',          'description':'When finished, ramp gate current to this value.'},
			'drainCurrentWhenDone': 		{'type':'float',                   'units':'A', 'default': 0,      'title':'Drain Current When Done',         'description':'When finished, ramp drain current to this value.'},
			'floatChannelsWhenDone': 		{'type':'bool',  			                    'default': False,  'title':'Float Channels When Done',        'description':'When finished, float the drain and gate terminals.'},
			'delayWhenDone': 				{'type':'float',                   'units':'s', 'default': 0,      'title':'Delay When Done',                 'description':'When finished, time to hold gate and drain current at their final value.'},
		},
		'NoiseCollection':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'NoiseCollection', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'measurementSpeed':	 		{'type':'float', 'essential':True, 'units':'Hz', 'default': 10e3,   'title':'Measurement Speed',  'description':''},
			'points':			 		{'type':'int',   'essential':True, 'units':'#',  'default': 10e3,   'title':'Points',             'description':''},
			'complianceCurrent':		{'type':'float',                   'units':'A',  'default': 100e-6, 'title':'Compliance Current', 'description':'Maximum current limit for the SMU.'},
			'gateVoltage':				{'type':'float', 'essential':True, 'units':'V',  'default': 0,      'title':'Gate Voltage',       'description':'Gate voltage value.'},
			'drainVoltage':				{'type':'float', 'essential':True, 'units':'V',  'default': 0.5,    'title':'Drain Voltage',      'description':'Drain voltage value.'}, 
		},
		'NoiseGrid':{
			'dependencies':				{'ignore':True, 'value':['NoiseCollection']},
			'saveFileName': 			{'type':'constant', 'default': 'NoiseGrid', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'gateVoltages':				{'type':'array', 'essential':True, 'units':'V', 'default': [-1,0,1],         'title':'Gate Voltages',  'description':''},
			'drainVoltages':			{'type':'array', 'essential':True, 'units':'V', 'default': [0.05,0.10,0.15], 'title':'Drain Voltages', 'description':''},
			'groundingTime':			{'type':'float',                   'units':'s', 'default': 1,                'title':'Grounding Time', 'description':''}, 
		}
	},
	'Results':{
		
	},
	'Computed':{
		
	},
	'SensorData':{
		
	},
	'MeasurementSystem':{
		'systemType': {'type':'choice', 'choices':['single', 'standalone', 'bluetooth', 'inverter', 'double', 'emulator'], 'default':['single', 'standalone', 'bluetooth', 'inverter', 'double', 'emulator'][0], 'title':'System Type', 'description':''},
		'systems': {},
		'deviceRange': {'type':'array', 'choices':["1-2", "2-3", "3-4", "5-6", "6-7", "7-8", "9-10", "10-11", "11-12", "13-14", "14-15", "15-16", "19-20", "21-22", "27-28", "29-30", "30-31", "31-32", "33-34", "34-35", "35-36", "37-38", "38-39", "39-40", "41-42", "42-43", "43-44", "45-46", "46-47", "47-48", "51-52", "53-54", "59-60", "61-62", "62-63", "63-64"], 'default':[], 'title':'Device Range', 'description':''} 
	},
	'dataFolder': {'type':'string', 'default':'../../AutexysData/', 'title':'Data Folder', 'description':''},
	'ParametersFormatVersion': {'default': 4}	
}



import copy

# --- Get default values of all parameters ---
def get():
	return extractDefaults(copy.deepcopy(default_parameters))

# --- Get default values of all parameters, with some modifications ---
def with_added(additional_parameters):
	default = get()
	combined = merge(default, additional_parameters)
	return combined

# --- private method: merge the changes specified by "b" into "a" ---
def merge(a, b):
	for key in b:
		if( (key in a) and (isinstance(a[key], dict)) and (isinstance(b[key], dict)) ):
			merge(a[key], b[key])
		else:
			a[key] = b[key]
	return a

# --- private method: get all of the subdictionaries of "a" that include the "keyword" as one of their keys ---	
def mustInclude(a, keyword):
	def eventuallyIncludes(dictionary, keyword):
		if(not isinstance(dictionary, dict)):
			return False
		if(keyword in dictionary.keys()):
			return True
		for key in dictionary.keys():
			if(isinstance(dictionary[key], dict)):
				if(eventuallyIncludes(dictionary[key], keyword)):
					return True
		return False
		
	reduced = {}
	for key in a.keys():
		if(isinstance(a[key], dict) and (keyword in a[key])):
			reduced[key] = a[key]
		elif(isinstance(a[key], dict) and eventuallyIncludes(a[key], keyword)):
			reduced[key] = mustInclude(a[key], keyword)
	return reduced

# --- private method: get the actual values out of the data structure defined in this file ---
def extractDefaults(d):
	if not isinstance(d, dict):
		return d
	if 'default' in d:
		return d['default']
	return {k:extractDefaults(v) for (k,v) in d.items() if not isinstance(v, dict) or 'ignore' not in v}

# --- private method: merge changes specified by "b" (a normal dict) into "a" (a dict with the structure defined in this file) ---
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

# --- private method: convert "a" into the structure defined in this file ("b" is already in the structure defined in this file) ---
def intersectionDefaults(a, b):
	reduced = {}
	for key in a.keys():
		if( (key in b) and (isinstance(a[key], dict)) and (isinstance(b[key], dict)) ):
			reduced[key] = intersectionDefaults(a[key], b[key])
		elif( (key in b) and not (isinstance(a[key], dict)) and (isinstance(b[key], dict)) ):
			reduced[key] = b[key]
			if('default' in reduced[key]):
				reduced[key]['default'] = a[key]
		else:
			reduced[key] = a[key]
	return reduced

# --- Get all default parameters (with the structure defined in this file), with some modified values ---
def full_with_added(additional_parameters):
	full_defaults = copy.deepcopy(default_parameters)
	combined = mergeDefaults(full_defaults, additional_parameters)
	return combined
	
# --- Convert "additional_parameters" into the structure defined in this file ---
def full_with_only(additional_parameters):
	full_defaults = copy.deepcopy(default_parameters)
	reduced_defaults = intersectionDefaults(additional_parameters, full_defaults)
	return reduced_defaults

# --- Get all default parameters (with the structure defined in this file) that are tagged as 'essential: True' ---
def full_essentials():
	full_defaults = copy.deepcopy(default_parameters)
	reduced = mustInclude(full_defaults, keyword='essential')
	return reduced

	

if __name__ == '__main__':
	import pprint
	import deepdiff
	#pprint.pprint(deepdiff.DeepDiff(default_parameters, get()))
	
	pprint.pprint(full_essentials())

