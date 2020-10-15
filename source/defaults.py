INCLUDE_EVERYTHING = True
ALWAYS_INCLUDE_PROCEDURES = ["GateSweep", "DrainSweep", "StaticBias", "AutoGateSweep", "AutoDrainSweep", "AutoStaticBias", "RapidBias", "SmallSignal"]
ALWAYS_INCLUDE_MEASUREMENT_SYSTEMS = ["automatic"]

# --- Default Parameters ---

default_parameters = {
	'runType': {'type': 'keyChoice', 'ChoiceFrom': 'runConfigs', 'default':''},
	'Identifiers':{
		'user':   {'type':'string', 'default':'', 'title':'User',      'description':'User for this experiment.'},
		'project':{'type':'string', 'default':'', 'title':'Project',   'description':'Project for this experiment.'},
		'wafer':  {'type':'string', 'default':'', 'title':'Wafer',     'description':'Wafer for this experiment.'},
		'chip':   {'type':'string', 'default':'', 'title':'Chip',      'description':'Chip for this experiment.'},
		'device': {'type':'string', 'default':'', 'title':'Device',    'description':'Device for this experiment.'},
		'step':   {'type':'string', 'default':'', 'title':'Step/Note', 'description':'Personal note for this experiment.'},
	},
	'runConfigs': {
		'GateSweep':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'GateSweep', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'gateVoltageMinimum': 		{'type':'float', 'essential':True, 'units':'V',  'default': -1,     'title':'Gate Voltage Start',           'description':'Gate voltage starting value.'},
			'gateVoltageMaximum': 		{'type':'float', 'essential':True, 'units':'V',  'default': 1,      'title':'Gate Voltage End',             'description':'Gate voltage final value.'}, 
			'drainVoltageSetPoint':		{'type':'float', 'essential':True, 'units':'V',  'default': 0.5,    'title':'Drain Voltage',                'description':'Drain voltage value.'},
			'stepsInVGSPerDirection': 	{'type':'int',   'essential':True, 'units':'#',  'default': 100,    'title':'Steps In VGS (per direction)', 'description':'Number of unique gate voltage steps in the sweep.'},
			'complianceCurrent':		{'type':'float',                   'units':'A',  'default': 100e-6, 'title':'Compliance Current',           'description':'Maximum current limit for the SMU.'},
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
			'stepsInVDSPerDirection': 	{'type':'int',   'essential':True, 'units':'#',  'default': 100,    'title':'Steps In VDS (per direction)', 'description':'Number of unique drain voltage steps in the sweep.'},
			'complianceCurrent':		{'type':'float',                   'units':'A',  'default': 100e-6, 'title':'Compliance Current',           'description':'Maximum current limit for the SMU.'},
			'pointsPerVDS': 			{'type':'int',                     'units':'#',  'default': 1,      'title':'Measurements per VDS',         'description':'Number of measurements taken at each drain voltage step.'},
			'drainVoltageRamps':		{'type':'int',                     'units':'#',  'default': 2,      'title':'Drain Voltage Ramps',          'description':'Number of times to loop through drain voltage values.'},
			'delayBetweenMeasurements': {'type':'float',                   'units':'s',  'default': 0,      'title':'Delay Between Measurements',   'description':'Duration of time to delay after taking a measurement.'},
			'isFastSweep': 				{'type':'bool',                                  'default': False,  'title':'Fast Sweep',                   'description':'Use internal SMU timer to measure a faster sweep.'},
			'fastSweepSpeed':			{'type':'int',                     'units':'Hz', 'default': 1000,   'title':'Fast Sweep Speed',             'description':'Frequency of SMU internal timer.'},
		},
		'StaticBias':{
			'dependencies':					{'ignore':True, 'value':[]},
			'saveFileName': 				{'type':'constant', 'default':'StaticBias', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'secondaryFileName': 			{'type':'constant', 'default':'StaticCurrent', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
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
			'supplyGateVoltage': 			{'type':'bool',  			                    'default': True,   'title':'Supply Gate Voltage',        	  'description':'When disabled, gate channel enters a high-resistance state to measure the gate voltage.'},
			'supplyDrainVoltage': 			{'type':'bool',  			                    'default': True,   'title':'Supply Drain Voltage',       	  'description':'When disabled, drain channel enters a high-resistance state to measure the drain voltage.'},
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
			'supplyGateVoltage': 		{'type':'bool',                                  'default': True,             'title':'Supply Gate Voltage',      'description':'When disabled, gate channel enters a high-resistance state to measure the gate voltage.'},
			'supplyDrainVoltage': 		{'type':'bool',                                  'default': True,             'title':'Supply Drain Voltage',     'description':'When disabled, drain channel enters a high-resistance state to measure the drain voltage.'},
		},
		'SmallSignal':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default':'SmallSignal', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'gateVoltageSetPoint': 		{'type':'float', 'essential':True, 'units':'V',  'default': 0,      'title':'Gate Voltage Set Point',         'description':'Gate voltage DC offset value.'},
			'drainVoltageSetPoint':		{'type':'float', 'essential':True, 'units':'V',  'default': 0,      'title':'Drain Voltage Set Point',        'description':'Drain voltage DC offset value.'},
			'gateVoltageAmplitude': 	{'type':'float', 'essential':True, 'units':'V',  'default': 0.1,    'title':'Gate Voltage Amplitude',         'description':'Gate voltage small-signal sinusoidal AC amplitude.'},
			'drainVoltageAmplitude': 	{'type':'float', 'essential':True, 'units':'V',  'default': 0.1,    'title':'Drain Voltage Amplitude',        'description':'Drain voltage small-signal sinusoidal AC amplitude.'},
			'frequencies': 				{'type':'array', 'essential':True, 'units':'Hz', 'default': [1],    'title':'Frequency List',                 'description':'List of frequencies to measure small-signal response at.'},
			'stepsPerPeriod': 			{'type':'int',                     'units':'#',  'default': 50,     'title':'Measurements per Period',        'description':'Number of measurements to take per period of the small-signal waveforms.'},
			'complianceCurrent': 		{'type':'float',                   'units':'A',  'default': 100e-6, 'title':'Compliance Current',             'description':'Maximum current limit for the SMU.'},
			'supplyGateVoltage': 		{'type':'bool',  			                     'default': True,   'title':'Supply Gate Voltage',        	  'description':'When disabled, gate channel enters a high-resistance state to measure the gate voltage.'},
			'supplyDrainVoltage': 		{'type':'bool',  			                     'default': True,   'title':'Supply Drain Voltage',       	  'description':'When disabled, drain channel enters a high-resistance state to measure the drain voltage.'},
		},
		'FreeRun':{
			'dependencies':				{'ignore':True, 'value':[]},
			'gateVoltageMinimum': 		{'type':'float', 'essential':True, 'units':'V', 'default': -1,       'title':'Gate Voltage Min',                     'description':'Gate voltage minimum value.'},
			'gateVoltageMaximum': 		{'type':'float', 'essential':True, 'units':'V', 'default': 1,        'title':'Gate Voltage Max',                     'description':'Gate voltage maximum value.'}, 
			'drainVoltageMinimum': 		{'type':'float', 'essential':True, 'units':'V', 'default': 0.5,      'title':'Drain Voltage Min',                    'description':'Drain voltage minimum value.'},
			'drainVoltageMaximum': 		{'type':'float', 'essential':True, 'units':'V', 'default': 0.5,      'title':'Drain Voltage Max',                    'description':'Drain voltage maximum value.'}, 
			'pointLimit':				{'type':'float',                                'default': None,     'title':'Point Limit',                          'description':'Limit on the number of points to collect in this free run.'},
			'complianceCurrent':		{'type':'float',                   'units':'A', 'default': 100e-6,   'title':'Compliance Current',                   'description':'Maximum current limit for the SMU.'},
			'delayBetweenMeasurements': {'type':'float',                   'units':'s', 'default': 0,        'title':'Delay Between Measurements',           'description':'Duration of time to delay after taking a measurement.'},
			'stepsBetweenMeasurements': {'type':'float',                                'default': 10,       'title':'Steps Between Measurements',           'description':'Number of intermediate steps to take between applied voltages (in order to soften the transition).'},
			'gateVoltageDistribution':  {'type':'choice',                               'default': 'random', 'title':'Gate Voltage Distribution',            'description':'Distribution of gate voltages to apply.',  'choices':['random', 'striped', 'looped']},
			'drainVoltageDistribution': {'type':'choice',                               'default': 'random', 'title':'Drain Voltage Distribution',           'description':'Distribution of drain voltages to apply.', 'choices':['random', 'striped', 'looped']},
			'gateVoltageDistributionParameter':  {'type':'float',                       'default': 2,        'title':'Gate Voltage Distribution Parameter',  'description':'Additional parameter used to define the more complex distributions.'},
			'drainVoltageDistributionParameter': {'type':'float',                       'default': 2,        'title':'Drain Voltage Distribution Parameter', 'description':'Additional parameter used to define the more complex distributions.'},
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
		},
		'InverterSweep':{
			'dependencies':				{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'InverterSweep', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'inputVoltageMinimum': 		{'type':'float', 'essential':True, 'units':'V', 'default': 0.0,    'title':'Input Voltage Minimum',        'description':'Input voltage starting value.'},
			'inputVoltageMaximum': 		{'type':'float', 'essential':True, 'units':'V', 'default': 1.0,    'title':'Input Voltage Maximum',        'description':'Input voltage final value.'},
			'vddSupplyVoltageSetPoint':	{'type':'float', 'essential':True, 'units':'V', 'default': 1.0,    'title':'Vdd Supply Voltage Set Point', 'description':'Inverter power supply voltage.'}, 
			'stepsInVINPerDirection': 	{'type':'int',   'essential':True, 'units':'#', 'default': 100,    'title':'Steps In VIN (per Direction)', 'description':'Number of unique input voltage steps in the sweep.'},
			'complianceCurrent':		{'type':'float',                   'units':'A', 'default': 100e-6, 'title':'Compliance Current',           'description':'Maximum current limit for the SMU.'},
			'pointsPerVIN': 			{'type':'int',                     'units':'#', 'default': 1,      'title':'Measurements Per VIN',         'description':'Number of measurements taken at each input voltage step.'},
			'inputVoltageRamps':		{'type':'int',                     'units':'#', 'default': 2,      'title':'Input Voltage Ramps',          'description':'Number of times to loop through input voltage values.'},
			'delayBetweenMeasurements': {'type':'float',                   'units':'s', 'default': 0,      'title':'Delay Between Measurements',   'description':'Duration of time to delay after taking a measurement.'},
		},
		'InverterBias':{
			'dependencies':					{'ignore':True, 'value':[]},
			'saveFileName': 				{'type':'constant', 'default':'InverterBias', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'inputVoltageSetPoint': 		{'type':'float', 'essential':True, 'units':'V', 'default': 0,      'title':'Input Voltage Set Point',         'description':'Input voltage value.'},
			'vddSupplyVoltageSetPoint':		{'type':'float', 'essential':True, 'units':'V', 'default': 1.0,    'title':'Vdd Supply Voltage Set Point',    'description':'Inverter power supply voltage.'}, 
			'totalBiasTime': 				{'type':'float', 'essential':True, 'units':'s', 'default': 60,     'title':'Total Bias Time',                 'description':'Total time to apply voltages.'},
			'measurementTime': 				{'type':'float', 'essential':True, 'units':'s', 'default': 1,      'title':'Measurement Time',                'description':'Interval over which to average each measurement.'},
			'complianceCurrent': 			{'type':'float',                   'units':'A', 'default': 100e-6, 'title':'Compliance Current',              'description':'Maximum current limit for the SMU.'},
			'delayBeforeMeasurementsBegin': {'type':'float',                   'units':'s', 'default': 0,      'title':'Delay Before Measurements Begin', 'description':'Delay after applying voltages before taking the first measurement.'},
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
		'AutoBurnOut':{
			'dependencies':					{'ignore':True, 'value':['BurnOut']},
			'targetOnOffRatio': 			{'type':'float', 'essential':True, 'units':'',  'default': 80,  'title':'Target On Off Ratio',            'description':'Stop burn out when the device on-off ratio increases above this absolute value.'},
			'limitOnOffRatioDegradation': 	{'type':'float',                   'units':'',  'default': 0.7, 'title':'Limit On Off Ratio Degradation', 'description':'Stop burn out if device on-off ratio decreases by this factor.'}, 
			'limitBurnOutsAllowed': 		{'type':'int',   'essential':True, 'units':'#', 'default': 8,   'title':'Limit Burn Outs Allowed',        'description':'Stop burn out after this many tries.'},
		},
		'Delay':{
			'dependencies': 			{'ignore':True, 'value':[]},
			'delayTime':				{'type':'int',    'essential':True, 'units':'s', 'default': 60,                       'title':'Delay Time', 'description':'Duration of delay.'}, 
			'message':					{'type':'string',                                'default': "Delaying next test...",  'title':'Message',    'description':'Message to print at the start of delay.'},
		},
		'PTSensor':{
			'dependencies': 			{'ignore':True, 'value':[]},
			'saveFileName': 			{'type':'constant', 'default': 'PTSensor', 'title':'Save File Name', 'description':'The name of the file that will be saved with the data from this experiment. This name should typically not be changed.'},
			'totalSensingTime':         {'type':'float',                   'units':'s', 'default': 60, 'title':'Total Sensing Time',         'description':'Total time to record measurements.'},
			'delayBetweenMeasurements': {'type':'float',                   'units':'s', 'default': 0,  'title':'Delay Between Measurements', 'description':'Duration of time to delay after taking a measurement.'},
		},
	},
	'Results':{
		
	},
	'Computed':{
		
	},
	'SensorData':{
		
	},
	'MeasurementSystem':{
		'systemType':				{'type':'choice',             'default':'automatic', 'title':'System Type',    'description':'The type of system used to capture measurements for this procedure.', 'choices':['automatic', 'single', 'standalone', 'Bluetooth', 'B2900A + PCB', 'B2900A (double)', 'B2900A (inverter)', 'Arduino', 'Emulator']},
		'systems': {},
		'deviceCycling':			{'type':'bool',               'default': False,      'title':'Device Cycling', 'description':'When enabled, this procedure will run repeatedly across multiple devices.'},
	},
	'DeviceCycling':{
		'numberOfCycles':		{'type':'int',   'units':'#', 'default': 1,       'title':'Number Of Cycles',      'description':'Number of times to repeat the measurement procedure on each device.'},
		'specificDeviceRange':	{'type':'array',              'default': [],      'title':'Specific Device Range', 'description':'', 'choices':["1-2", "2-3", "3-4", "5-6", "6-7", "7-8", "9-10", "10-11", "11-12", "13-14", "14-15", "15-16", "19-20", "21-22", "27-28", "29-30", "30-31", "31-32", "33-34", "34-35", "35-36", "37-38", "38-39", "39-40", "41-42", "42-43", "43-44", "45-46", "46-47", "47-48", "51-52", "53-54", "59-60", "61-62", "62-63", "63-64"]}, 
		'delayBetweenDevices': 	{'type':'float', 'units':'s', 'default': 0,       'title':'Delay Between Devices', 'description':'Delay between switching from one device to the next.'},
		'delayBetweenCycles': 	{'type':'float', 'units':'s', 'default': 0,       'title':'Delay Between Cycles',  'description':'Delay between each cycle of devices.'},
		'timedCycles': 			{'type':'bool',               'default': False,   'title':'Timed Cycles',          'description':'When enabled, the delay between cycles is dynamically reduced by the amount of time the last cycle took.'}, 
		'deviceIndexes': {},
	},
	'dataFolder': {'type':'string', 'default':'../../AutexysData/', 'title':'Data Folder', 'description':''},
	'ParametersFormatVersion': {'default': 4},	
	'Deployment': {'default': 'Development' if(INCLUDE_EVERYTHING) else 'Production'}
}

# --- Default Identifiers ---

default_identifiers = {
	'user':   {'type':'string', 'default':'guest',   'title':'User',    'description':'Default User whenever left unspecified.'},
	'project':{'type':'string', 'default':'Project', 'title':'Project', 'description':'Default Project whenever left unspecified.'},
	'wafer':  {'type':'string', 'default':'Wafer',   'title':'Wafer',   'description':'Default Wafer whenever left unspecified.'},
	'chip':   {'type':'string', 'default':'Chip',    'title':'Chip',    'description':'Default Chip whenever left unspecified.'},
	'device': {'type':'string', 'default':'Device',  'title':'Device',  'description':'Default Device whenever left unspecified.'},
}

# --- Default Schedules ---

default_schedules = {
	'Gate Sweep':             {"runType": "GateSweep",      "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"GateSweep": {"gateVoltageMinimum": -1, "gateVoltageMaximum": 1, "drainVoltageSetPoint": 0.5, "stepsInVGSPerDirection": 100}}},
	'Drain Sweep':            {"runType": "DrainSweep",     "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"DrainSweep": {"drainVoltageMinimum": 0, "drainVoltageMaximum": 1, "gateVoltageSetPoint": 0, "stepsInVDSPerDirection": 100}}},
	'Static Bias':            {"runType": "StaticBias",     "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"StaticBias": {"gateVoltageSetPoint": 0, "drainVoltageSetPoint": 0.5, "totalBiasTime": 60, "measurementTime": 1}}},
	'Multiple Gate Sweeps':   {"runType": "AutoGateSweep",  "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"AutoGateSweep": {"sweepsPerVDS": 3, "drainVoltageSetPoints": []}, "GateSweep": {"gateVoltageMinimum": -1, "gateVoltageMaximum": 1, "drainVoltageSetPoint": 0.5, "stepsInVGSPerDirection": 100}}},
	'Multiple Drain Sweeps':  {"runType": "AutoDrainSweep", "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"AutoDrainSweep": {"sweepsPerVGS": 1, "gateVoltageSetPoints": [-1, 0, 1]}, "DrainSweep": {"drainVoltageMinimum": 0, "drainVoltageMaximum": 1, "gateVoltageSetPoint": 0, "stepsInVDSPerDirection": 100}}},
	'Multiple Static Biases': {"runType": "AutoStaticBias", "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"AutoStaticBias": {"numberOfStaticBiases": 1, "doInitialGateSweep": True, "applyGateSweepBetweenBiases": False, "biasTimeList": [], "gateVoltageSetPointList": [], "drainVoltageSetPointList": []}, "StaticBias": {"gateVoltageSetPoint": 0, "drainVoltageSetPoint": 0.5, "totalBiasTime": 60, "measurementTime": 1}, "GateSweep": {"gateVoltageMinimum": -1, "gateVoltageMaximum": 1, "drainVoltageSetPoint": 0.5, "stepsInVGSPerDirection": 100}}},
	'Rapid Bias':             {"runType": "RapidBias",      "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"RapidBias": {"waveform": "square", "drainVoltageSetPoints": [0.1], "gateVoltageSetPoints": [0, 1, 0, 1, 0], "measurementPoints": [50, 50, 50, 50, 50]}}},
	'Small Signal':           {"runType": "SmallSignal",    "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"SmallSignal": {"gateVoltageSetPoint": 0, "drainVoltageSetPoint": 0, "gateVoltageAmplitude": 0.1, "drainVoltageAmplitude": 0.1, "frequencies":[1]}}},
	'Free Run':               {"runType": "FreeRun",        "Identifiers": {"device": ""}, "runConfigs": {"FreeRun": {"gateVoltageMinimum": -1, "gateVoltageMaximum": 1, "drainVoltageMinimum": 0.5, "drainVoltageMaximum": 0.5}}},
	'Noise Collection':       {"runType": "NoiseCollection","Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"NoiseCollection": {"measurementSpeed": 10000, "points": 10000, "gateVoltage": 0, "drainVoltage": 0.5}}},
	'Noise Grid':             {"runType": "NoiseGrid",      "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"NoiseGrid": {"gateVoltages":[], "drainVoltages":[], "groundingTime":0}, "NoiseCollection": {"measurementSpeed": 10000, "points": 10000, "gateVoltage": 0, "drainVoltage": 0.5}}},
	'Inverter Sweep':         {"runType": "InverterSweep",  "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"InverterSweep": {"inputVoltageMinimum": 0, "inputVoltageMaximum": 1, "vddSupplyVoltageSetPoint": 1, "stepsInVINPerDirection": 100}}, "MeasurementSystem": {"systemType": "B2900A (inverter)"}},
	'Inverter Bias':          {"runType": "InverterBias",   "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"InverterBias": {"inputVoltageSetPoint": 0, "vddSupplyVoltageSetPoint": 1.0, "totalBiasTime": 60, "measurementTime":1}}, "MeasurementSystem": {"systemType": "B2900A (inverter)"}},
	'AFM Control':            {"runType": "AFMControl",     "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"AFMControl": {"lines": 3, "scanRate": 1, "napOn": True, "drainVoltageSetPoint": 0.01, "gateVoltageSetPoint": 0, "startOnFrameSwitch": False, "deviceMeasurementSpeed": 60, "XYCableSwap": False}}, "MeasurementSystem": {"systemType": "B2900A (double)"}},
	'SGM Control':            {"runType": "SGMControl",     "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"SGMControl": {"lines": 3, "scanRate": 1, "napOn": True, "drainVoltageSetPoint": 0.01, "gateVoltageSetPoint": 0, "startOnFrameSwitch": False, "complianceCurrent": 0.000001, "deviceMeasurementSpeed": 60, "XYCableSwap": False, "tracesToMeasure": 1, "scans": 1}}, "MeasurementSystem": {"systemType": "B2900A (double)"}},
	'Flow Static Bias':       {"runType": "FlowStaticBias", "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"FlowStaticBias": {"flowDurations": [], "subCycleDurations": [], "cycleCount": 3, "solutions": [], "gateVoltageSetPoint": 0, "drainVoltageSetPoint": 0.5, "measurementTime": 1}}},
	'Multiple Flow Static Biases': {"runType": "AutoFlowStaticBias", "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"AutoFlowStaticBias": {"numberOfFlowStaticBiases": 1, "doInitialGateSweep": True, "applyGateSweepBetweenBiases": False, "numberOfBiasesBetweenIncrements": 1, "biasTimeList": [], "incrementStaticGateVoltage": 0, "incrementStaticDrainVoltage": 0}, "FlowStaticBias": {"flowDurations": [], "subCycleDurations": [], "cycleCount": 3, "solutions": [], "gateVoltageSetPoint": 0, "drainVoltageSetPoint": 0.5, "measurementTime": 1}, "GateSweep": {"gateVoltageMinimum": -1, "gateVoltageMaximum": 1, "drainVoltageSetPoint": 0.5, "stepsInVGSPerDirection": 100}}},
	'CNT Burn Out':           {"runType": "BurnOut",        "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"BurnOut": {"gateVoltageSetPoint": 15, "drainVoltageMaxPoint": 5, "minimumAppliedDrainVoltage": 1.1}}},
	'Multiple CNT Burn Outs': {"runType": "AutoBurnOut",    "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"AutoBurnOut": {"targetOnOffRatio": 80, "limitBurnOutsAllowed": 8}, "BurnOut": {"gateVoltageSetPoint": 15, "drainVoltageMaxPoint": 5, "minimumAppliedDrainVoltage": 1.1}}},
	'Delay':                  {"runType": "Delay",          "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"Delay": {"delayTime": 60}}},
	'PT Sensor':              {"runType": "PTSensor",       "Identifiers": {"user": "", "project": "", "wafer": "", "chip": "", "device": "", "step": 0}, "runConfigs": {"PTSensor": {"totalSensingTime": 60}}},
}

# --- Measurement System Configurations ---

measurement_system_configurations = {
	'automatic': {
		'SMU': { 'type': 'AUTO', },
	},
	'single': {
		'SMU': { 'type': 'B2900A', },
	},
	'standalone': {
		'SMU': { 'type': 'PCB_SYSTEM', },
	},
	'Bluetooth': {
		'SMU': {
			'type': 'PCB_SYSTEM',
			'uniqueID': '/dev/tty.HC-05-DevB',
		},
	},
	'B2900A + PCB': {
		'B2900A': { 'type': 'B2900A', },
		'PCB': {
			'type': 'PCB_SYSTEM',
			'settings': {
				'channel':2,
			},
		},
	},
	'B2900A (double)': {
		'deviceSMU':{
			'type': 'B2900A',
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141244::INSTR',
			'settings': {
				'reset': False,
				'turnChannelsOn': False,
				'channel1SourceMode': 'voltage',
				'channel2SourceMode': 'voltage',
			},
		},
		'secondarySMU':{
			'type': 'B2900A',
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141241::INSTR',
			'settings': {
				'reset': False,
				'turnChannelsOn': False,
				'channel1SourceMode': 'current',
				'channel2SourceMode': 'current',
			},
		},
	},
	'B2900A (inverter)': {
		'logicSignalSMU':{
			'type': 'B2900A',
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141241::INSTR',
			'settings': {
				'channel1SourceMode': 'current',
				'channel2SourceMode': 'voltage',
			},
		},
		'powerSupplySMU':{
			'type': 'B2900A',
			'uniqueID': 'USB0::0x0957::0x8C18::MY51142879::INSTR',
			'settings': {
				'channel1SourceMode': 'voltage',
				'channel2SourceMode': 'voltage',
			},
		},
	},
	'Arduino':{
		'MCU': {
			'type': 'ARDUINO_SYSTEM',
			'uniqueID': 'any',
		},
	},
	'Emulator':{
		'SMU': 			  { 'type': 'EMULATOR_SYSTEM', },
		'logicSignalSMU': { 'type': 'EMULATOR_SYSTEM', },
		'powerSupplySMU': { 'type': 'EMULATOR_SYSTEM', },
		'deviceSMU':	  { 'type': 'EMULATOR_SYSTEM', },
		'secondarySMU':	  { 'type': 'EMULATOR_SYSTEM', },
	},
	'slowSMU1': {
		'SMU': {
			'type': 'B2900A',
			'uniqueID': 'USB0::0x0957::0x8C18::MY51142879::INSTR',
		},
	},
	'fastSMU1': {
		'SMU': {
			'type': 'B2900A',
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141244::INSTR',
		},
	},
	'fastSMU2': {
		'SMU': {
			'type': 'B2900A',
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141241::INSTR',
		},
	},
}

# --- Enable/Disable Specialized Procedures ---

if(not INCLUDE_EVERYTHING):	
	# Remove extra entries from 'runConfig'
	runConfigs_list = list(default_parameters['runConfigs'].keys())
	for runConfig in runConfigs_list:
		if(runConfig not in ALWAYS_INCLUDE_PROCEDURES):
			del default_parameters['runConfigs'][runConfig]
	
	# Remove extra entries from 'default_schedules'
	schedules_list = list(default_schedules.keys())
	for schedule in schedules_list:
		if(default_schedules[schedule]['runType'] not in ALWAYS_INCLUDE_PROCEDURES):
			del default_schedules[schedule]
	
	# Remove extra entries from 'MeasurementSystem'
	measurement_systems_list = list(default_parameters['MeasurementSystem']['systemType']['choices'])
	for measurement_system in measurement_systems_list:
		if(measurement_system not in ALWAYS_INCLUDE_MEASUREMENT_SYSTEMS):
			default_parameters['MeasurementSystem']['systemType']['choices'].remove(measurement_system)
	if(len(ALWAYS_INCLUDE_MEASUREMENT_SYSTEMS) > 0):
		default_parameters['MeasurementSystem']['systemType']['default'] = ALWAYS_INCLUDE_MEASUREMENT_SYSTEMS[0]



import copy

# --- Get default values of all parameters ---
def get():
	return extractDefaults(copy.deepcopy(default_parameters))

# --- Get default values of all parameters, with some modifications ---
def with_added(additional_parameters):
	default = get()
	combined = merge(default, additional_parameters)
	return combined

# --- Get all default parameters (with the structure defined in this file) ---
def full():
	return copy.deepcopy(default_parameters)

# --- Get all default parameters (with the structure defined in this file), with some modified values ---
def full_with_added(additional_parameters):
	full_defaults = full()
	combined = mergeDefaults(full_defaults, additional_parameters)
	return combined
	
# --- Convert "additional_parameters" into the structure defined in this file ---
def full_with_only(additional_parameters):
	full_defaults = full()
	reduced_defaults = intersectionDefaults(additional_parameters, full_defaults)
	return reduced_defaults

# --- Get all default parameters (with the structure defined in this file) that are tagged as 'essential: True' ---
def full_essentials():
	full_defaults = full()
	essential_defaults = mustInclude(full_defaults, keyword='essential')
	return essential_defaults

# --- Get a list of placeholders used whenever identifiers are left unspecified ---
def identifiers():
	return extractDefaults(copy.deepcopy(default_identifiers))

# --- Get a list of placeholders used whenever identifiers are left unspecified (with the structure defined in this file) ---
def full_identifiers():
	return copy.deepcopy(default_identifiers)

# --- Get a list of standard schedule files ---
def full_schedules():
	return copy.deepcopy(default_schedules)

# --- Get one of the standard schedule files, merged with all other default parameters (with the structure defined in this file)  ---
def full_schedule(scheduleName):
	return full_with_added(full_schedules()[scheduleName])

# --- Get one of the standard schedule files (with the structure defined in this file)  ---
def full_brief_schedule(scheduleName):
	return full_with_only(full_schedules()[scheduleName])

# --- Get the configuration info for a given measurement system choice ---
def system_configuration(systemChoice):
	return copy.deepcopy(measurement_system_configurations[systemChoice])



# --- private method: merge the changes specified by "b" into "a" ---
def merge(a, b):
	for key in b:
		if( (key in a) and (isinstance(a[key], dict)) and (isinstance(b[key], dict)) ):
			merge(a[key], b[key])
		else:
			a[key] = b[key]
	return a

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
	

if __name__ == '__main__':
	import pprint
	import deepdiff
	#pprint.pprint(deepdiff.DeepDiff(default_parameters, get()))
	
	pprint.pprint(full_brief_schedule('Gate Sweep'))

