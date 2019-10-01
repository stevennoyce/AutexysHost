"""This module defines a common Python interface for communicating to SMU systems. It also defines the possible sets of SMUs that can be
connected to and the ports/MAC addresses need to connect."""

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

smu_system_configurations = {
	'single': {
		'SMU': {
			'uniqueID': '',
			'type': 'B2912A',
			'settings': {}
		}
	},
	'standalone': {
		'PCB': {
			'uniqueID': '',
			'type': 'PCB2v14',
			'settings': {}
		}
	},
	'bluetooth': {
		'PCB': {
			'uniqueID': '/dev/tty.HC-05-DevB',
			'type': 'PCB2v14',
			'settings': {}
		}
	},
	'slowSMU1': {
		'SMU': {
			'uniqueID': 'USB0::0x0957::0x8C18::MY51142879::INSTR',
			'type': 'B2912A',
			'settings': {}
		}
	},
	'fastSMU1': {
		'SMU': {
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141244::INSTR',
			'type': 'B2912A',
			'settings': {}
		}
	},
	'fastSMU2': {
		'SMU': {
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141241::INSTR',
			'type': 'B2912A',
			'settings': {}
		}
	},
	'double': {
		'deviceSMU':{
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141244::INSTR',
			'type': 'B2912A',
			'settings': {
				'reset': False,
				'turnChannelsOn': False,
				'channel1SourceMode': 'voltage',
				'channel2SourceMode': 'voltage'
			}
		},
		'secondarySMU':{
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141241::INSTR',
			'type': 'B2912A',
			'settings': {
				'reset': False,
				'turnChannelsOn': False,
				'channel1SourceMode': 'current',
				'channel2SourceMode': 'current'
			}
		}
	},
	'inverter': {
		'sweepSMU':{
			'uniqueID': 'USB0::0x0957::0x8E18::MY51141241::INSTR',
			'type': 'B2912A',
			'settings': {
				'reset': True,
				'channel1SourceMode': 'current',
				'channel2SourceMode': 'voltage'
			}
		},
		'powerSupplySMU':{
			'uniqueID': 'USB0::0x0957::0x8C18::MY51142879::INSTR',
			'type': 'B2912A',
			'settings': {
				'reset': True,
				'channel1SourceMode': 'voltage',
				'channel2SourceMode': 'voltage'
			}
		}
	}
}

defaultTimeout = 60000

def getSystemConfiguration(systemType):
	return copy.deepcopy(smu_system_configurations[systemType])

def getConnectionToVisaResource(uniqueIdentifier='', system_settings=None, defaultComplianceCurrent=100e-6, smuTimeout=defaultTimeout):
	import visa
	
	try:
		rm = visa.ResourceManager()
		if(uniqueIdentifier == ''):
			uniqueIdentifier = rm.list_resources()[0]
		instance = rm.open_resource(uniqueIdentifier)
		print(instance.query('*IDN?'))
		print('Opened VISA connection through NI-VISA backend.')
	except:
		rm = visa.ResourceManager('@py')
		if(uniqueIdentifier == ''):
			uniqueIdentifier = rm.list_resources()[0]
		instance = rm.open_resource(uniqueIdentifier)
		print(instance.query('*IDN?'))
		print('Opened VISA connection through PyVISA-py backend.')
		
	instance.timeout = smuTimeout
	return B2912A(instance, uniqueIdentifier, defaultComplianceCurrent, system_settings)

def getConnectionToPCB(pcb_port='', system_settings=None):
	if(pcb_port == ''):
		active_ports = [port for port in pySerialPorts.comports() if(port.description != 'n/a')]
		if(len(active_ports) == 0):
			raise Exception('Unable to find any active serial ports to connect to PCB.')
		else:
			pcb_port = active_ports[0]
	try:
		ser = pySerial.Serial(pcb_port, 115200)
	except:
		ser = pySerial.Serial(pcb_port.device, 115200)
	return PCB2v14(ser, pcb_port)

def getConnectionToEmulator():
	return Emulator()

class SourceMeasureUnit:
	system_id = ''
	stepsPerRamp = 15
	measurementsPerSecond = None
	measurementRateVariabilityFactor = None
	
	def turnChannelsOn(self):
		raise NotImplementedError("Please implement SourceMeasureUnit.turnChannelsOn()")
	
	def turnChannelsOff(self):
		raise NotImplementedError("Please implement SourceMeasureUnit.turnChannelsOff()")
	
	def setComplianceCurrent(self, complianceCurrent):
		raise NotImplementedError("Please implement SourceMeasureUnit.setComplianceCurrent()")

	def setDevice(self, deviceID):
		raise NotImplementedError("Please implement SourceMeasureUnit.setDevice()")

	def setParameter(self, parameter):
		raise NotImplementedError("Please implement SourceMeasureUnit.setParameter()")

	def setVds(self, voltage):
		raise NotImplementedError("Please implement SourceMeasureUnit.setVds()")

	def setVgs(self, voltage):
		raise NotImplementedError("Please implement SourceMeasureUnit.setVgs()")

	def setId(self, current):
		raise NotImplementedError("Please implement SourceMeasureUnit.setId()")
	
	def setIg(self, current):
		raise NotImplementedError("Please implement SourceMeasureUnit.setIg()")

	def takeMeasurement(self):
		raise NotImplementedError("Please implement SourceMeasureUnit.takeMeasurement()")

	def takeSweep(self, src1start, src1stop, src2start, src2stop, points):
		raise NotImplementedError("Please implement SourceMeasureUnit.takeSweep()")
	
	def disconnect(self):
		raise NotImplementedError("Please implement SourceMeasureUnit.disconnect()")

	def getVds(self):
		return self.takeMeasurement()['V_ds']

	def getVgs(self):
		return self.takeMeasurement()['V_gs']
	
	def getId(self):
		return self.takeMeasurement()['I_d']

	def getIg(self):
		return self.takeMeasurement()['I_g']

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
		self.rampDrainVoltageTo(0, steps)

	def rampDownVoltages(self, steps=None):
		print('Ramping down SMU channels.')
		self.rampDrainVoltageDown(steps)
		self.rampGateVoltageDown(steps)
	
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
		self.rampDrainCurrentTo(0, steps)

	def rampDownCurrents(self, steps=None):
		print('Ramping down SMU channels.')
		self.rampDrainCurrentDown(steps)
		self.rampGateCurrentDown(steps)
		
	
	
class B2912A(SourceMeasureUnit):
	smu = None
	system_id = ''
	stepsPerRamp = 20
	measurementsPerSecond = 40
	measurementRateVariabilityFactor = 2
	nplc = 1
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
	
	def setDevice(self, deviceID):
		pass
	
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
		if self.use_binary:
			return self.smu.query_binary_values(query)
		
		return self.smu.query_ascii_values(query)
	
	def setParameter(self, parameter):
		self.smu.write(parameter)

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

	def setComplianceCurrent(self, complianceCurrent=100e-6):
		self.setParameter(":sense1:curr:prot {}".format(complianceCurrent))
		self.setParameter(":sense2:curr:prot {}".format(complianceCurrent))

	def setComplianceVoltage(self, complianceVoltage):
		self.setParameter(":sense1:volt:prot {}".format(complianceVoltage))
		self.setParameter(":sense2:volt:prot {}".format(complianceVoltage))

	def setChannel1SourceMode(self, mode="voltage"):
		if(mode in ["voltage", "current"]):
			self.setParameter(":source1:function:mode {}".format(mode))
			source1_mode = mode
			print('Source 1 mode set to: ' + str(mode))

	def setChannel2SourceMode(self, mode="voltage"):
		if(mode in ["voltage", "current"]):
			self.setParameter(":source2:function:mode {}".format(mode))
			source2_mode = mode
			print('Source 2 mode set to: ' + str(mode))

	def setVds(self, voltage):
		self.setParameter(":source1:voltage {}".format(voltage))

	def setVgs(self, voltage):
		self.setParameter(":source2:voltage {}".format(voltage))
		
	def setId(self, current):
		self.setParameter(":source1:current {}".format(current))

	def setIg(self, current):
		self.setParameter(":source2:current {}".format(current))
	
	def setTimeout(self, timeout_ms=defaultTimeout):
		self.smu.timeout = timeout_ms
	
	def clearAndDisarm(self):
		self.smu.clear()
		self.smu.write(':abort:all (@1,2)')
	
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
	
	def initSweep(self):
		self.smu.write(":init (@1:2)")
		self.smu.write("*WAI")
	
	def startSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None, src2vals=None):
		timeToTakeMeasurements = self.setupSweep(src1start, src1stop, src2start, src2stop, points, triggerInterval=triggerInterval, src1vals=src1vals, src2vals=src2vals)
		
		self.smu.write("*WAI")
		self.initSweep()
		
		return timeToTakeMeasurements
	
	def endSweep(self, endMode=None, includeCurrents=[True, True], includeVoltages=[True,True], includeTimes=True):
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
	
	def takeSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None, src2vals=None, includeCurrents=True, includeVoltages=True, includeTimes=True):
		timeToTakeMeasurements = self.startSweep(src1start, src1stop, src2start, src2stop, points, triggerInterval=triggerInterval, src1vals=src1vals, src2vals=src2vals)
		
		time.sleep(timeToTakeMeasurements)
		
		return self.endSweep(endMode='fixed', includeCurrents=includeCurrents, includeVoltages=includeVoltages, includeTimes=includeTimes)
	
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
	
	def disconnect(self):
		pass
	
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
		


class PCB2v14(SourceMeasureUnit):
	ser = None
	system_id = ''
	stepsPerRamp = 5
	measurementsPerSecond = 10
	measurementRateVariabilityFactor = 2
	nplc = 1

	def __init__(self, pySerial, pcb_port):
		self.ser = pySerial
		self.system_id = pcb_port

	def setComplianceCurrent(self, complianceCurrent):
		pass

	def setParameter(self, parameter):
		self.ser.write( str(parameter).encode('UTF-8') )

	def getResponse(self, startsWith='', lines=1, printResponse=True):
		response = ''
		for i in range(lines):
			line = self.ser.readline().decode(encoding='UTF-8')
			if(startsWith != ''):
				while(line[0] != startsWith):
					print('SKIPPED: ' + str(line))
					line = self.ser.readline().decode(encoding='UTF-8')
			response += line
		if(printResponse):
			print(response, end='')
		return response

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

	def setDevice(self, deviceID):
		self.setParameter('connect-intermediates !')
		self.getResponse(lines=9)
		self.setParameter('disconnect-all-from-all !')
		self.getResponse(lines=9)
		contactPad1 = int(deviceID.split('-')[0])
		contactPad2 = int(deviceID.split('-')[1])
		intermediate1 = (1) if(contactPad1 <= 32) else (3)
		intermediate2 = (2) if(contactPad2 <= 32) else (4)
		print('connecting contact: ' + str(contactPad1) + ' to AMUX: ' + str(intermediate1))
		print('connecting contact: ' + str(contactPad2) + ' to AMUX: ' + str(intermediate2))
		self.setParameter("connect {} {}!".format(contactPad1, intermediate1))
		self.getResponse(lines=3)
		self.setParameter("connect {} {}!".format(contactPad2, intermediate2))
		self.getResponse(lines=3)
		self.setParameter("calibrate-offset !")
		self.getResponse(startsWith='#', lines=9)
		print('Switched to device: ' + str(deviceID))

	def setVds(self, voltage):
		self.setParameter("set-vds-mv {:.0f}!".format(voltage*1000))
		self.getResponse(startsWith='#')

	def setVgs(self, voltage):
		self.setParameter("set-vgs-mv {:.0f}!".format(voltage*1000))
		self.getResponse(startsWith='#')

	def takeMeasurement(self):
		self.setParameter('measure !')
		response = self.getResponse(startsWith='[', printResponse=False)
		print('MEASURE: ' + str(response), end='')
		return self.formatMeasurement(response)

	def takeSweep(self, src1start, src1stop, src2start, src2stop, points):
		vds_data = []
		id_data = []
		vgs_data = []
		ig_data = []
		points = int(points)

		if(src1start == src1stop and src2start == src2stop):
			self.setParameter('measure-multiple {:d}!'.format(points))

			timeToTakeMeasurements = (self.nplc)*(points/self.measurementsPerSecond)
			time.sleep(1.5 * timeToTakeMeasurements)

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


		raise NotImplementedError('PCB2v14 general sweep not implemented.')

		return {
			'Vds_data': vds_data,
			'Id_data': id_data,
			'Vgs_data': vgs_data,
			'Ig_data': ig_data
		}
	
	def disconnect(self):
		self.ser.close()

class Emulator(SourceMeasureUnit):
	'''
	For use when computer is not connected to any device, but testing of certain UI features is desired. Returns dummy data
	for use when testing.
	'''

	smu = None
	system_id = ''
	stepsPerRamp = 20
	measurementsPerSecond = 40
	measurementRateVariabilityFactor = 2
	nplc = 1
	source1_mode = 'voltage'
	source2_mode = 'voltage'
	system_settings = {}

	def __init__(self):
		pass

	def initialize(self):
		pass

	def setDevice(self, deviceID):
		pass

	def setBinaryDataTransfer(self, useBinary=True):
		pass

	def query_values(self, query):
		return [1, 2, 3, 4, 5]

	def setParameter(self, parameter):
		pass

	def turnChannelsOn(self):
		pass

	def turnChannelsOff(self):
		pass

	def setNPLC(self, nplc=1):
		pass

	def turnAutoRangingOn(self):
		pass

	def turnAutoRangingOff(self):
		pass

	def setComplianceCurrent(self, complianceCurrent=100e-6):
		pass

	def setComplianceVoltage(self, complianceVoltage):
		pass

	def setChannel1SourceMode(self, mode="voltage"):
		pass

	def setChannel2SourceMode(self, mode="voltage"):
		pass

	def setVds(self, voltage):
		pass

	def setVgs(self, voltage):
		pass

	def setId(self, current):
		pass

	def setIg(self, current):
		pass

	def setTimeout(self, timeout_ms=defaultTimeout):
		pass

	def clearAndDisarm(self):
		pass

	def takeMeasurement(self, retries=3):
		time.sleep(0.1)

		return {
			'V_ds': 1*random.randint(0,1),
			'I_d': 0.001*random.randint(0,1),
			'V_gs': 3.3*random.randint(0,1),
			'I_g': 0.00000000001*random.randint(0,1)
		}

	def setupSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None,
				   src2vals=None):
		return 10

	def initSweep(self):
		pass

	def startSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None,
				   src2vals=None):
		return 10

	def endSweep(self, endMode=None, includeCurrents=[True, True], includeVoltages=[True, True], includeTimes=True):
		return {
			'Vds_data': [[1*random.randint(0,1)]*10]*2,
			'Id_data': [[0.001*random.randint(0,1)]*10]*2,
			'Vgs_data': [[3.3*random.randint(0,1)]*10]*2,
			'Ig_data': [[0.00000000001*random.randint(0,1)]*10]*2,
			'timestamps': [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]]
		}

	def takeSweep(self, src1start, src1stop, src2start, src2stop, points, triggerInterval=None, src1vals=None,
				  src2vals=None, includeCurrents=True, includeVoltages=True, includeTimes=True):
		time.sleep(0.1)

		return {
			'Vds_data': [[1*random.randint(0,1)]*10]*2,
			'Id_data': [[0.001*random.randint(0,1)]*10]*2,
			'Vgs_data': [[3.3*random.randint(0,1)]*10]*2,
			'Ig_data': [[0.00000000001*random.randint(0,1)]*10]*2,
			'timestamps': [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]]
		}

	def arm(self, count=1):
		pass

	def enableHardwareTriggerReception(self, pin=1):
		pass

	def enableHardwareArmReception(self, pin=1):
		pass

	def disconnect(self):
		pass

	def digitalWrite(self, pin, signal):
		pass

if (__name__ == '__main__'):
	getConnectionToVisaResource()





