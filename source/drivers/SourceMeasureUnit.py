"""This module defines a common Python interface for communicating to SMU systems. It also defines the possible sets of SMUs that can be
connected to and the ports/MAC addresses need to connect."""

# === Imports ===

import ast
import random

import serial as pySerial
import serial.tools.list_ports as pySerialPorts
import glob
import time
import re
import random as rand
import numpy as np
import json
import copy



# === Measurement System Configurations ===

smu_system_configurations = {
	'single': {
		'SMU': {
			'uniqueID': '',
			'type': 'B2912A',
			'settings': {},
		}
	},
	'standalone': {
		'PCB': {
			'uniqueID': '',
			'type': 'PCB_System',
			'settings': {},
		}
	},
	'Bluetooth': {
		'PCB': {
			'uniqueID': '/dev/tty.HC-05-DevB',
			'type': 'PCB_System',
			'settings': {},
		}
	},
	'B2900A + PCB': {
		'SMU': {
			'uniqueID': '',
			'type': 'B2912A',
			'settings': {},
		},
		'PCB': {
			'uniqueID': '',
			'type': 'PCB_System',
			'settings': {
				'channel':2,
			},
		}
	},
	'B2900A (double)': {
		'deviceSMU':{
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141244::INSTR',
			'type': 'B2912A',
			'settings': {
				'reset': False,
				'turnChannelsOn': False,
				'channel1SourceMode': 'voltage',
				'channel2SourceMode': 'voltage'
			},
		},
		'secondarySMU':{
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141241::INSTR',
			'type': 'B2912A',
			'settings': {
				'reset': False,
				'turnChannelsOn': False,
				'channel1SourceMode': 'current',
				'channel2SourceMode': 'current'
			},
		}
	},
	'B2900A (inverter)': {
		'logicSignalSMU':{
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141241::INSTR',
			'type': 'B2912A',
			'settings': {
				'channel1SourceMode': 'current',
				'channel2SourceMode': 'voltage'
			},
		},
		'powerSupplySMU':{
			'uniqueID': 'USB0::0x0957::0x8C18::MY51142879::INSTR',
			'type': 'B2912A',
			'settings': {
				'channel1SourceMode': 'voltage',
				'channel2SourceMode': 'voltage'
			},
		}
	},
	'Arduino':{
		'MCU': {
			'uniqueID': 'any',
			'type': 'Arduino_System',
			'settings': {},
		}
	},
	'Emulator':{
		'SMU': {
			'uniqueID': '',
			'type': 'Emulator_System',
			'settings': {},
		},
		'logicSignalSMU':{
			'uniqueID': '',
			'type': 'Emulator_System',
			'settings': {},
		},
		'powerSupplySMU':{
			'uniqueID': '',
			'type': 'Emulator_System',
			'settings': {},
		},
		'deviceSMU':{
			'uniqueID': '',
			'type': 'Emulator_System',
			'settings': {},
		},
		'secondarySMU':{
			'uniqueID': '',
			'type': 'Emulator_System',
			'settings': {},
		}
	},
	'slowSMU1': {
		'SMU': {
			'uniqueID': 'USB0::0x0957::0x8C18::MY51142879::INSTR',
			'type': 'B2912A',
			'settings': {},
		}
	},
	'fastSMU1': {
		'SMU': {
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141244::INSTR',
			'type': 'B2912A',
			'settings': {},
		}
	},
	'fastSMU2': {
		'SMU': {
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141241::INSTR',
			'type': 'B2912A',
			'settings': {},
		}
	},
}



# === Connection API ===

def getSystemConfiguration(systemType):
	return copy.deepcopy(smu_system_configurations[systemType])

def getConnectionToVisaResource(uniqueIdentifier='', system_settings=None, defaultComplianceCurrent=100e-6, smuTimeout=60000):
	import visa
	
	# Try forming connection over National Instruments backend (or Python backend if that fails)
	try:
		rm = visa.ResourceManager()
		if(uniqueIdentifier == ''):
			uniqueIdentifier = rm.list_resources()[0]
		visa_system = rm.open_resource(uniqueIdentifier)
		print('Opened VISA connection through NI-VISA backend.')
	except:
		rm = visa.ResourceManager('@py')
		if(uniqueIdentifier == ''):
			uniqueIdentifier = rm.list_resources()[0]
		visa_system = rm.open_resource(uniqueIdentifier)
		print('Opened VISA connection through PyVISA-py backend.')
	
	# Query Visa ID and set timeout
	print(visa_system.query('*IDN?'))
	visa_system.timeout = smuTimeout
	
	# Print connection beginning message
	print('Beginning connection to visa resource: ' + str(uniqueIdentifier)) 
	
	return B2912A(visa_system, uniqueIdentifier, defaultComplianceCurrent, system_settings)

def getConnectionToPCB(port='', baud=115200, system_settings=None):
	# Iterate over possible USB connections
	if(port == ''):
		active_ports = [serial_port for serial_port in pySerialPorts.comports() if(serial_port.description != 'n/a')]
		if(len(active_ports) == 0):
			raise Exception('Unable to find any active serial ports to connect to PCB.')
		else:
			port = active_ports[0].device
			
	# Connect to PCB over pyserial
	ser = pySerial.Serial(port, baud)
	
	# Print connection beginning message
	print('Beginning connection to PCB on serial port: ' + str(port))
		
	return PCB_System(ser, port, system_settings)

def getConnectionToEmulator():
	return Emulator()



# === SMU Base Class Definition ===

class SourceMeasureUnit:
	# === Generic instance variables ===
	system_id = ''
	stepsPerRamp = 15
	measurementsPerSecond = None
	measurementRateVariabilityFactor = None
	nplc = 1
	
	# --- Communication ---
	def setParameter(self, parameter):
		raise NotImplementedError("Please implement SourceMeasureUnit.setParameter()")
	
	def setDevice(self, deviceID):
		raise NotImplementedError("Please implement SourceMeasureUnit.setDevice()")
	
	def disconnect(self):
		raise NotImplementedError("Please implement SourceMeasureUnit.disconnect()")
	
	# --- Measurement Channels ---
	def setComplianceCurrent(self, complianceCurrent):
		raise NotImplementedError("Please implement SourceMeasureUnit.setComplianceCurrent()")
	
	def turnChannelsOn(self):
		raise NotImplementedError("Please implement SourceMeasureUnit.turnChannelsOn()")
	
	def turnChannelsOff(self):
		raise NotImplementedError("Please implement SourceMeasureUnit.turnChannelsOff()")

	def getDrainSourceMode(self):
		raise NotImplementedError("Please implement SourceMeasureUnit.getDrainSourceMode()")
	
	def getGateSourceMode(self):
		raise NotImplementedError("Please implement SourceMeasureUnit.getGateSourceMode()")

	# --- Source ---
	def setVds(self, voltage):
		raise NotImplementedError("Please implement SourceMeasureUnit.setVds()")

	def setVgs(self, voltage):
		raise NotImplementedError("Please implement SourceMeasureUnit.setVgs()")

	def setId(self, current):
		raise NotImplementedError("Please implement SourceMeasureUnit.setId()")
	
	def setIg(self, current):
		raise NotImplementedError("Please implement SourceMeasureUnit.setIg()")

	# --- Measure ---
	def takeMeasurement(self):
		raise NotImplementedError("Please implement SourceMeasureUnit.takeMeasurement()")

	# --- Sweep ---
	def takeSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None, src2vals=None):
		raise NotImplementedError("Please implement SourceMeasureUnit.takeSweep()")
	
	# --- Specific Channel Measurement ---
	def getVds(self):
		return self.takeMeasurement()['V_ds']

	def getVgs(self):
		return self.takeMeasurement()['V_gs']
	
	def getId(self):
		return self.takeMeasurement()['I_d']

	def getIg(self):
		return self.takeMeasurement()['I_g']

	# --- Voltage Ramps ---
	def rampGateVoltage(self, voltageStart, voltageSetPoint, steps=None):
		if(steps == None):
			steps = abs(voltageStart - voltageSetPoint)//1e-6
			steps = min(steps, self.stepsPerRamp)
		
		if(steps <= 1):
			self.setVgs(voltageSetPoint)
			return
				
		gateVoltages = np.linspace(voltageStart, voltageSetPoint, steps).tolist()
		for gateVoltage in gateVoltages:
			self.setVgs(gateVoltage)

	def rampGateVoltageTo(self, voltageSetPoint, steps=None):
		voltageStart = self.getVgs()
		self.rampGateVoltage(voltageStart, voltageSetPoint, steps)

	def rampGateVoltageDown(self, steps=None):
		print('Ramping down SMU gate voltage.')
		self.rampGateVoltageTo(0, steps)

	def rampDrainVoltage(self, voltageStart, voltageSetPoint, steps=None):
		if(steps == None):
			steps = abs(voltageStart - voltageSetPoint)//1e-6
			steps = min(steps, self.stepsPerRamp)
		
		if(steps <= 1):
			self.setVds(voltageSetPoint)	
			return
			
		drainVoltages = np.linspace(voltageStart, voltageSetPoint, steps).tolist()
		for drainVoltage in drainVoltages:
			self.setVds(drainVoltage)

	def rampDrainVoltageTo(self, voltageSetPoint, steps=None):
		voltageStart = self.getVds()
		self.rampDrainVoltage(voltageStart, voltageSetPoint, steps)

	def rampDrainVoltageDown(self, steps=None):
		print('Ramping down SMU drain voltage.')
		self.rampDrainVoltageTo(0, steps)

	def rampDownVoltages(self, steps=None):
		print('Ramping down SMU channels.')
		self.rampDrainVoltageDown(steps)
		self.rampGateVoltageDown(steps)
	
	# --- Current Ramps ---
	def rampGateCurrent(self, currentStart, currentSetPoint, steps=None):
		if(steps == None):
			steps = abs(currentStart - currentSetPoint)//1e-9
			steps = min(steps, self.stepsPerRamp)
		
		if(steps <= 1):
			self.setIg(currentSetPoint)
			return
				
		gateCurrents = np.linspace(currentStart, currentSetPoint, steps).tolist()
		for gateCurrent in gateCurrents:
			self.setIg(gateCurrent)

	def rampGateCurrentTo(self, currentSetPoint, steps=None):
		currentStart = self.getIg()
		self.rampGateCurrent(currentStart, currentSetPoint, steps)

	def rampGateCurrentDown(self, steps=None):
		print('Ramping down SMU gate current.')
		self.rampGateCurrentTo(0, steps)

	def rampDrainCurrent(self, currentStart, currentSetPoint, steps=None):
		if(steps == None):
			steps = abs(currentStart - currentSetPoint)//1e-9
			steps = min(steps, self.stepsPerRamp)
		
		if(steps <= 1):
			self.setId(currentSetPoint)	
			return
			
		drainCurrents = np.linspace(currentStart, currentSetPoint, steps).tolist()
		for drainCurrent in drainCurrents:
			self.setId(drainCurrent)

	def rampDrainCurrentTo(self, currentSetPoint, steps=None):
		currentStart = self.getId()
		self.rampDrainCurrent(currentStart, currentSetPoint, steps)

	def rampDrainCurrentDown(self, steps=None):
		print('Ramping down SMU drain current.')
		self.rampDrainCurrentTo(0, steps)

	def rampDownCurrents(self, steps=None):
		print('Ramping down SMU channels.')
		self.rampDrainCurrentDown(steps)
		self.rampGateCurrentDown(steps)
		
	
	
# === B2900A Sub-Class Definition ===
	
class B2912A(SourceMeasureUnit):
	# === Generic instance variables ===
	system_id = ''
	stepsPerRamp = 20
	measurementsPerSecond = 40
	measurementRateVariabilityFactor = 2
	nplc = 1
	
	# === System-specific instance variables ===
	smu = None
	source1_mode = 'voltage'
	source2_mode = 'voltage'
	system_settings = {}
	
	def __init__(self, visa_instance, visa_id, defaultComplianceCurrent, system_settings):
		self.smu = visa_instance
		self.system_id = visa_id
		self.system_settings = system_settings
		self.use_binary = False
		self.initialize()
		self.setComplianceCurrent(defaultComplianceCurrent)
	
	# --- Internal ---
	def initialize(self):
		if((self.system_settings is not None) and ('reset' in self.system_settings) and (not self.system_settings['reset'])):
			pass # don't reset on startup if you are specifically told not to by the system settings
		else:
			self.clearAndDisarm()
			self.smu.write('*CLS') # Clear
			self.smu.write("*RST") # Reset
		
		self.smu.write(':system:lfrequency 60')
		
		self.smu.write(':sense1:curr:range:auto ON')
		self.smu.write(':sense1:curr:range:auto:llim 1e-8')
		# self.smu.write(':sense1:curr:range 10E-6')
		
		self.smu.write(':sense2:curr:range:auto ON')
		self.smu.write(':sense2:curr:range:auto:llim 1e-8')
		# self.smu.write(':sense2:curr:range 10E-6')
		
		if ((self.system_settings is not None) and ('channel1SourceMode' in self.system_settings)):
			self.setChannel1SourceMode(self.system_settings['channel1SourceMode'])
			self.setChannel2SourceMode(self.system_settings['channel2SourceMode'])
		else:
			self.smu.write(":source1:function:mode voltage")
			self.smu.write(":source2:function:mode voltage")
			
			self.smu.write(":source1:voltage 0.0")
			self.smu.write(":source2:voltage 0.0")
		
		self.smu.write(":sense1:curr:nplc 1")
		self.smu.write(":sense2:curr:nplc 1")
		
		if ((self.system_settings is not None) and ('turnChannelsOn' in self.system_settings) and (self.system_settings['turnChannelsOn'])):
			self.smu.write(":outp1 ON")
			self.smu.write(":outp2 ON")
		
		self.smu.write("*WAI") # Explicitly wait for all of these commands to finish before handling new commands
	
	def setTimeout(self, timeout_ms=60000):
		self.smu.timeout = timeout_ms
	
	# --- Communication ---
	def setParameter(self, parameter):
		self.smu.write(parameter)
	
	def setDevice(self, deviceID):
		pass
	
	def disconnect(self):
		pass
	
	# --- Measurement Channels ---	
	def setComplianceCurrent(self, complianceCurrent=100e-6):
		self.setParameter(":sense1:curr:prot {}".format(complianceCurrent))
		self.setParameter(":sense2:curr:prot {}".format(complianceCurrent))

	def setComplianceVoltage(self, complianceVoltage):
		self.setParameter(":sense1:volt:prot {}".format(complianceVoltage))
		self.setParameter(":sense2:volt:prot {}".format(complianceVoltage))

	def turnChannelsOn(self):
		self.setParameter(":output1 ON")
		self.setParameter(":output2 ON")
	
	def turnChannelsOff(self):
		self.setParameter(":output1 OFF")
		self.setParameter(":output2 OFF")
	
	def setNPLC(self, nplc=1):
		self.setParameter(":sense1:curr:nplc {}".format(nplc))
		self.setParameter(":sense1:volt:nplc {}".format(nplc))
		self.setParameter(":sense2:curr:nplc {}".format(nplc))
		self.setParameter(":sense2:volt:nplc {}".format(nplc))	

	def turnAutoRangingOn(self):
		self.setParameter(':sense1:curr:range:auto ON')
		self.setParameter(':sense2:curr:range:auto ON')

	def turnAutoRangingOff(self):
		self.setParameter(':sense1:curr:range:auto OFF')
		self.setParameter(':sense2:curr:range:auto OFF')

	def setChannel1SourceMode(self, mode="voltage"):
		if(mode in ["voltage", "current"]):
			self.setParameter(":source1:function:mode {}".format(mode))
			self.source1_mode = mode
			print('Source 1 mode set to: ' + str(mode))

	def setChannel2SourceMode(self, mode="voltage"):
		if(mode in ["voltage", "current"]):
			self.setParameter(":source2:function:mode {}".format(mode))
			self.source2_mode = mode
			print('Source 2 mode set to: ' + str(mode))

	def getDrainSourceMode(self):
		return self.source1_mode
	
	def getGateSourceMode(self):
		return self.source2_mode

	# --- Source ---	
	def setVds(self, voltage):
		self.setParameter(":source1:voltage {}".format(voltage))

	def setVgs(self, voltage):
		self.setParameter(":source2:voltage {}".format(voltage))
		
	def setId(self, current):
		self.setParameter(":source1:current {}".format(current))

	def setIg(self, current):
		self.setParameter(":source2:current {}".format(current))
	
	# --- Measure ---	
	def setBinaryDataTransfer(self, useBinary=True):
		if useBinary and not self.use_binary:
			self.smu.write(':form real,32')
			self.smu.write(':form:border swap')
			self.smu.values_format.use_binary('d', False, list)
		
		if not useBinary and self.use_binary:
			self.smu.write(':form asc')
			self.smu.write(':form:border norm')
			self.smu.values_format.use_ascii('f', ',', list)
		
		self.use_binary = useBinary
		
	def query_values(self, query):
		if(self.use_binary):
			return self.smu.query_binary_values(query)
		return self.smu.query_ascii_values(query)
	
	def takeMeasurement(self, retries=3):
		for i in range(retries):
			try:
				data = self.query_values(':MEAS? (@1:2)')
				break
			except Exception as e:
				print('SMU measurement failed on try: ' + str(i+1) + (', retrying...' if(i+1 < retries) else (', aborting measurement.')))
				self.clearAndDisarm()
				data = [0 for j in range(10)]
		
		return {
			'V_ds': data[0],
			'I_d':  data[1],
			'V_gs': data[6],
			'I_g':  data[7]
		}
	
	# --- Sweep ---
	# SWEEP: configure all hardware settings to prepare a sweep
	def setupSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None, src2vals=None):
		points = int(points)
		
		# Set up voltages to apply
		if src1vals is None:
			self.smu.write(":source1:{}:mode sweep".format(self.source1_mode))
			self.smu.write(":source1:{}:start {}".format(self.source1_mode, src1start))
			self.smu.write(":source1:{}:stop {}".format(self.source1_mode, src1stop)) 
			self.smu.write(":source1:{}:points {}".format(self.source1_mode, points))
		else:
			self.smu.write(':source1:{}:mode list'.format(self.source1_mode))
			self.smu.write(':source1:list:{} {}'.format(self.source2_mode, ','.join(map(str, src1vals))))
		
		if src2vals is None:
			self.smu.write(":source2:{}:mode sweep".format(self.source2_mode))
			self.smu.write(":source2:{}:start {}".format(self.source2_mode, src2start))
			self.smu.write(":source2:{}:stop {}".format(self.source2_mode, src2stop)) 
			self.smu.write(":source2:{}:points {}".format(self.source2_mode, points))
		else:
			self.smu.write(':source2:{}:mode list'.format(self.source2_mode))
			self.smu.write(':source2:list:{} {}'.format(self.source2_mode, ','.join(map(str, src2vals))))
		
		# Set up number of measurements to take
		if triggerInterval is None:
			self.smu.write(":trigger1:source aint")
			self.smu.write(":trigger1:count {}".format(points))
			self.smu.write(":trigger2:source aint")
			self.smu.write(":trigger2:count {}".format(points))
			timeToTakeMeasurements = (self.nplc)*(points/self.measurementsPerSecond)
		else:
			self.smu.write(":trigger1:source timer")
			self.smu.write(":trigger1:timer {}".format(triggerInterval))
			self.smu.write(":trigger1:count {}".format(points))
			self.smu.write(":trigger2:source timer")
			self.smu.write(":trigger2:timer {}".format(triggerInterval))
			self.smu.write(":trigger2:count {}".format(points))
			timeToTakeMeasurements = (triggerInterval*points)
		
		self.smu.write("*WAI")
		
		return timeToTakeMeasurements
	
	# SWEEP: trigger a sweep to begin
	def initSweep(self):
		self.smu.write(":init (@1:2)")
		self.smu.write("*WAI")
	
	# SWEEP: Setup and trigger a sweep to begin
	def startSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None, src2vals=None):
		timeToTakeMeasurements = self.setupSweep(src1start, src1stop, src2start, src2stop, points, triggerInterval=triggerInterval, src1vals=src1vals, src2vals=src2vals)
		
		self.smu.write("*WAI")
		self.initSweep()
		
		return timeToTakeMeasurements
	
	# SWEEP: Retrieve data from most recent sweep
	def endSweep(self, endMode=None, includeCurrents=[True, True], includeVoltages=[True, True], includeTimes=True):
		if(not isinstance(includeCurrents, list)):
			includeCurrents = [includeCurrents, includeCurrents]
		if(not isinstance(includeVoltages, list)):
			includeVoltages = [includeVoltages, includeVoltages]
		
		try:
			current1s = self.query_values(":fetch:arr:curr? (@1)") 	if(includeCurrents[0]) else None
			voltage1s = self.query_values(":fetch:arr:voltage? (@1)") if(includeVoltages[0]) else None
			current2s = self.query_values(":fetch:arr:curr? (@2)")	if(includeCurrents[1]) else None
			voltage2s = self.query_values(":fetch:arr:voltage? (@2)") if(includeVoltages[1]) else None
			timestamps = self.query_values(":fetch:array:time? (@2)") if(includeTimes) else None
		except Exception as e:
			self.clearAndDisarm()
			current1s = None
			voltage1s = None
			current2s = None
			voltage2s = None
			timestamps = None
		
		if(endMode is not None):
			self.smu.write(":source1:{}:mode {}".format(self.source1_mode, endMode))
			self.smu.write(":source2:{}:mode {}".format(self.source2_mode, endMode))
		
		return {
			'Vds_data': voltage1s,
			'Id_data':  current1s,
			'Vgs_data': voltage2s,
			'Ig_data':  current2s,
			'timestamps': timestamps
		}
	
	# SWEEP: Perform a fully hardware-driven sweep
	def takeSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None, src2vals=None, includeCurrents=True, includeVoltages=True, includeTimes=True):
		timeToTakeMeasurements = self.startSweep(src1start, src1stop, src2start, src2stop, points, triggerInterval=triggerInterval, src1vals=src1vals, src2vals=src2vals)
		
		time.sleep(timeToTakeMeasurements)
		
		return self.endSweep(endMode='fixed', includeCurrents=includeCurrents, includeVoltages=includeVoltages, includeTimes=includeTimes)
	
	# --- Arm ---
	def arm(self, count=1):
		"""Arm the instrument.
		
		Take the instrument from the idle state to the armed state, enabling it to recieve hardware triggers.
		
		:param count: The number of hardware triggers that can be recieved before returning to the idle state. This can be float('inf') for a permanent armed state.
		:type count: int, float"""
		
		print('Arming the instrument')
		
		if count != float('inf'):
			count = int(count)
		
		self.smu.write(':arm1:acq:count {}'.format(count))
		self.smu.write(':arm2:acq:count {}'.format(count))
	
	def clearAndDisarm(self):
		self.smu.clear()
		self.smu.write(':abort:all (@1,2)')
	
	def enableHardwareTriggerReception(self, pin=1):
		"""Configure the instrument to enable the reception of hardware triggers whenever it is armed."""
		
		print('Enabling hardware trigger reception on pin {}'.format(pin))
		
		# Configure the digital pin
		self.smu.write(':source:digital:ext{}:function tinp'.format(pin))
		self.smu.write(':source:digital:ext{}:polarity pos'.format(pin))
		self.smu.write(':source:digital:ext{}:toutput:type level'.format(pin))
		self.smu.write(':source:digital:ext{}:toutput:width 0.01'.format(pin))
		
		# Set the input pin as the trigger source
		self.smu.write(':trigger1:acq:source:signal ext{}'.format(pin))
		self.smu.write(':trigger2:acq:source:signal ext{}'.format(pin))
	
	def enableHardwareArmReception(self, pin=1):
		"""Configure the instrument to enable the reception of hardware arm events whenever it is initiated."""
		
		print('Enabling hardware arm reception on pin {}'.format(pin))
		
		# Configure the digital pin
		self.smu.write(':source:digital:ext{}:function tinp'.format(pin))
		self.smu.write(':source:digital:ext{}:polarity pos'.format(pin))
		self.smu.write(':source:digital:ext{}:toutput:type level'.format(pin))
		self.smu.write(':source:digital:ext{}:toutput:width 0.01'.format(pin))
		
		# Set the input pin as the trigger source
		self.smu.write(':arm1:all:source:signal ext{}'.format(pin))
		self.smu.write(':arm2:all:source:signal ext{}'.format(pin))
	
	# --- Digital GPIO ---
	def digitalWrite(self, pin, signal):
		if pin < 0:
			return
		
		prior = self.smu.query(':source:digital:data?')
		decBin = pow(2, pin-1)
		
		self.smu.write(":format:digital ascii")
		self.smu.write(":source:digital:external" + str(pin) + ":function DIO")
		self.smu.write(":source:digital:external" + str(pin) + ":polarity positive")
		if signal == "HIGH":
			self.smu.write(":source:digital:data " + str(int(prior) | decBin))
		
		elif signal == "LOW":
			self.smu.write(":source:digital:data " + str(int(prior) & ~decBin))
		


# === PCB Sub-Class Definition ===

class PCB_System(SourceMeasureUnit):
	# === Generic instance variables ===
	system_id = ''
	stepsPerRamp = 5
	measurementsPerSecond = 10
	measurementRateVariabilityFactor = 2
	nplc = 1
	
	# === System-specific instance variables ===
	ser = None
	signal_channel = 1

	def __init__(self, pySerial, port, system_settings):
		self.ser = pySerial
		self.system_id = port
		if(port == smu_system_configurations['Bluetooth']['PCB']['uniqueID']):
			print('Enabling bluetooth communication (can be slow).')
			self.setParameter('enable-uart-sending !', responseStartsWith='#')
		if((system_settings is not None) and ('channel' in system_settings)):
			self.signal_channel = system_settings['channel']
			self.setParameter('switch-all-selectors-to-signal {:}!'.format(self.signal_channel), responseStartsWith='#')

	# --- Internal ---
	# Wait for PCB to send a message. The best way to use this is to specify a unique character that the message will start with so that you know when you've received it. 
	def getResponse(self, startsWith='', lines=1, printResponse=True):
		response = ''
		for i in range(lines):
			line = self.ser.readline().decode(encoding='UTF-8')
			if(startsWith != ''):
				while(line[0] != startsWith):
					print('NOTE: ' + str(line), end='')
					line = self.ser.readline().decode(encoding='UTF-8')
			response += line
		if(printResponse):
			print(response, end='')
		return response

	# --- Communication ---
	def setParameter(self, parameter, responseStartsWith=None):
		self.ser.write( str(parameter).encode('UTF-8') )
		if(responseStartsWith is not None):
			self.getResponse(startsWith=responseStartsWith)

	# Make connections to a specific device
	def setDevice(self, deviceID):
		# Disconnect any previously connected devices
		self.setParameter('disconnect-all-from-all !', responseStartsWith='#')
		
		# Make sure the device selector is delivering the correct signal to our device of interest
		self.turnChannelsOn()
			
		# Extract device contact numbers from the deviceID
		if('-' not in deviceID):
			print('PCB system is unable to connect to device: "' + str(deviceID) +'".')
			return
		contactPad1 = int(deviceID.split('-')[0])
		contactPad2 = int(deviceID.split('-')[1])
		
		# Connect to device and run calibration routine
		self.setParameter("connect-device {:} {:}!".format(contactPad1, contactPad2), responseStartsWith='#')
		self.setParameter("calibrate-adc-offset !", responseStartsWith='#')
		print('Switched to device: ' + str(deviceID))

	def disconnect(self):
		self.ser.close()
	
	# --- Measurement Channels ---
	def setComplianceCurrent(self, complianceCurrent):
		pass

	def turnChannelsOn(self):
		if(self.signal_channel == 2):
			self.setParameter('connect-all-selectors-secondary !', responseStartsWith='#')
		else:
			self.setParameter('connect-all-selectors !', responseStartsWith='#')
	
	def turnChannelsOff(self):
		self.setParameter('disconnect-all-selectors !', responseStartsWith='#')

	def getDrainSourceMode(self):
		return 'voltage'
	
	def getGateSourceMode(self):
		raise 'voltage'

	# --- Source ---
	# Set Vds in millivolts (easy communication, avoids using decimal numbers)
	def setVds_mV(self, voltage):
		self.setParameter("set-vds-mv {:.0f}!".format(voltage*1000), responseStartsWith='#')

	# Set Vgs in millivolts (easy communication, avoids using decimal numbers)
	def setVgs_mV(self, voltage):
		self.setParameter("set-vgs-mv {:.0f}!".format(voltage*1000), responseStartsWith='#')
	
	# Set Vds in Volts
	def setVds(self, voltage):
		self.setParameter("set-vds {:.3f}!".format(voltage), responseStartsWith='#')

	# Set Vgs in Volts
	def setVgs(self, voltage):
		self.setParameter("set-vgs {:.3f}!".format(voltage), responseStartsWith='#')

	# --- Measure ---
	# Convert to the standard data format
	def formatMeasurement(self, measurement):
		data = json.loads(str(measurement))
		i_d = float(data[0])
		v_gs = float(data[1])
		v_ds = float(data[2])
		i_g = float(data[3]) if(len(data) >= 4) else 0.0
		return {
			'V_ds': v_ds,
			'I_d':  i_d,
			'V_gs': v_gs,
			'I_g':  i_g
		}

	def takeMeasurement(self):
		self.setParameter('measure !')
		response = self.getResponse(startsWith='[', printResponse=False)
		print('MEASURE: ' + str(response), end='')
		return self.formatMeasurement(response)

	# --- Sweep ---
	# SWEEP: configure all hardware settings to prepare a sweep
	def setupSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None, src2vals=None):
		points = int(points)
		
		src1loops = 0
		src2loops = 0
		
		# If sweep was specified by arrays of points, choose reasonable values for src1start/src1stop
		if((src1vals is not None) and (isinstance(src1vals, list)) and (len(src1vals) > 0)): 
			src1start = src1vals[0]
			src1stop = src1vals[-1]
			
			if((src1start != max(src1vals)) and (src1stop != max(src1vals))):
				src1stop = max(src1vals)
				src1loops = 1
			elif((src1start != min(src1vals)) and (src1stop != min(src1vals))):
				src1stop = min(src1vals)
				src1loops = 1
		
		# If sweep was specified by arrays of points, choose reasonable values for src2start/src2stop
		if((src2vals is not None) and (isinstance(src2vals, list)) and (len(src1vals) > 0)): 
			src2start = src2vals[0]
			src2stop = src2vals[-1]
		
			if((src2start != max(src2vals)) and (src2stop != max(src2vals))):
				src2stop = max(src2vals)
				src2loops = 1
			elif((src2start != min(src2vals)) and (src2stop != min(src2vals))):
				src2stop = min(src2vals)
				src2loops = 1
		
		timeToTakeMeasurements = (self.nplc)*(points/self.measurementsPerSecond)
		
		return {
			'timeToTakeMeasurements': 1.5*timeToTakeMeasurements,
			'src1start': src1start,
			'src1stop':  src1stop,
			'src2start': src2start,
			'src2stop':  src2stop,
			'points': int(points),
			'src1loops': src1loops,
			'src2loops': src2loops,
		}
	
	# SWEEP: trigger a sweep to begin
	def triggerSweep(self, src1start, src1stop, src2start, src2stop, points, src1loops=0, src2loops=0):
		# Static Bias
		if(src1start == src1stop and src2start == src2stop):
			self.setVds(src1start)
			self.setVgs(src2start)
			self.setParameter('measure-multiple {:d}!'.format(points))
			
		# Gate Sweep
		elif(src1start == src1stop):
			self.setVds(src1start)
			if(src2loops > 0):
				self.setParameter('gate-sweep-loop {:.3f} {:.3f} {:d}!'.format(src2start, src2stop, points))
			else:
				self.setParameter('gate-sweep {:.3f} {:.3f} {:d}!'.format(src2start, src2stop, points))
				
		# Drain Sweep
		elif(src2start == src2stop):
			self.setVgs(src2start)
			if(src1loops > 0):
				self.setParameter('drain-sweep-loop {:.3f} {:.3f} {:d}!'.format(src1start, src1stop, points))
			else:
				self.setParameter('drain-sweep {:.3f} {:.3f} {:d}!'.format(src1start, src1stop, points))
		
		# Not a Static Bias, Gate Sweep, or Drain Sweep
		else:
			raise NotImplementedError('PCB system multi-channel sweep is not implemented.')

	# SWEEP: Setup and trigger a sweep to begin
	def startSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None, src2vals=None):
		sweepSetupInfo = self.setupSweep(src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None, src2vals=None)
		
		self.triggerSweep(sweepSetupInfo['src1start'], sweepSetupInfo['src1stop'], sweepSetupInfo['src2start'], sweepSetupInfo['src2stop'], points=sweepSetupInfo['points'], src1loops=sweepSetupInfo['src1loops'], src2loops=sweepSetupInfo['src2loops'])
		
		return timeToTakeMeasurements

	# SWEEP: Retrieve data from most recent sweep
	def endSweep():
		vds_data = []
		id_data = []
		vgs_data = []
		ig_data = []
		
		# Read measurements from output buffer
		while(self.ser.in_waiting):
			response = self.getResponse()
			data = self.formatMeasurement(response)
			vds_data.append(data['V_ds'])
			id_data.append(data['I_d'])
			vgs_data.append(data['V_gs'])
			ig_data.append(data['I_g'])

		return {
			'Vds_data': vds_data,
			'Id_data': id_data,
			'Vgs_data': vgs_data,
			'Ig_data': ig_data
		}

	# SWEEP: Perform a fully hardware-driven sweep
	def takeSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None, src2vals=None):
		timeToTakeMeasurements = self.startSweep(src1start, src1stop, src2start, src2stop, points)

		time.sleep(timeToTakeMeasurements)	
		
		return self.endSweep()



# === Emulator Sub-Class Definition ===

class Emulator(SourceMeasureUnit):
	'''
	For use when computer is not connected to any device, but testing of certain UI features is desired. Returns dummy data
	for use when testing.
	'''

	# === Generic instance variables ===
	system_id = ''
	stepsPerRamp = 20
	measurementsPerSecond = 40
	measurementRateVariabilityFactor = 2
	nplc = 1
	
	# === System-specific instance variables ===
	vds = 0
	vgs = 0
	system_settings = {}

	def __init__(self):
		pass

	def setTimeout(self, timeout_ms=60000):
		pass

	# --- Communication ---
	def setParameter(self, parameter):
		pass

	def setDevice(self, deviceID):
		pass
	
	def disconnect(self):
		pass

	# --- Measurement Channels ---
	def turnChannelsOn(self):
		pass

	def turnChannelsOff(self):
		pass

	def setComplianceCurrent(self, complianceCurrent=100e-6):
		pass

	def setComplianceVoltage(self, complianceVoltage):
		pass

	def setChannel1SourceMode(self, mode="voltage"):
		if(mode in ["voltage", "current"]):
			self.source1_mode = mode

	def setChannel2SourceMode(self, mode="voltage"):
		if(mode in ["voltage", "current"]):
			self.source2_mode = mode

	def getDrainSourceMode(self):
		return self.source1_mode
		
	def getGateSourceMode(self):
		return self.source2_mode

	# --- Source ---
	def setVds(self, voltage):
		self.vds = voltage

	def setVgs(self, voltage):
		self.vgs = voltage

	def setId(self, current):
		pass

	def setIg(self, current):
		pass

	# --- Measure ---
	def canonical_model(self, K, vt, vgs, vds):
		return ( (K*( (vgs - vt)*vds - 0.5*(vds**2) )) if(vds < vgs-vt) else (0.5 * K * ((max(0, vgs-vt))**2)) )
	
	def takeMeasurement(self, retries=3):
		time.sleep(0.025)

		vds = self.vds
		vgs = self.vgs
		i_d = self.canonical_model(100e-6, 0.5, vgs, vds)
		
		vds = 1*random.randint(0,1)
		vgs = 3.3*random.randint(0,1)
		i_d = 0.001*random.randint(0,1)

		return {
			'V_ds': vds,
			'I_d': i_d,
			'V_gs': vgs,
			'I_g': 0.00000000001*random.randint(0,1)
		}

	# --- Sweep ---
	def takeSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None, src2vals=None):
		time.sleep(0.1)

		return {
			'Vds_data': [1*random.randint(0,1)]*20,
			'Id_data': [0.001*random.randint(0,1)]*20,
			'Vgs_data': [3.3*random.randint(0,1)]*20,
			'Ig_data': [0.00000000001*random.randint(0,1)]*20,
			'timestamps': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
		}
	

	

if (__name__ == '__main__'):
	pcb = getConnectionToPCB(system_settings=smu_system_configurations['B2900A + PCB']['PCB']['settings'])
	keysight = getConnectionToVisaResource(system_settings=smu_system_configurations['B2900A + PCB']['SMU']['settings'])
	pcb.setDevice('1-2')		
	print(keysight.takeMeasurement())





