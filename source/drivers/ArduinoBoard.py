"""This module defines a common Python interface for communicating to Arduino boards over the Arduino Serial interface."""

# === Imports ===
import time
import json
import numpy as np

import serial as pySerial
import serial.tools.list_ports as pySerialPorts



# === Connection API ===

def getConnection(port='', baud=115200, system_settings=None):
	# Iterate over possible USB connections, with looser restrictions if port == 'any'
	active_ports = []
	if(port == ''):
		limited_ports = [serial_port for serial_port in pySerialPorts.comports() if(serial_port.device in ['/dev/cu.wchusbserial1410', '/dev/cu.wchusbserial1420', '/dev/cu.wchusbserial14101'])]
		if(len(limited_ports) > 0):
			port = limited_ports[0].device
	elif(port == 'any'):
		active_ports = [serial_port for serial_port in pySerialPorts.comports() if(serial_port.description != 'n/a')]
		if(len(active_ports) > 0):
			port = active_ports[0].device
	
	# If not able to connect, return null instance
	if(port in ['', 'any']): 
		print("No Arduino connected.")
		return NullArduinoSerial()			
	
	# Connect to Arduino over pyserial
	ser = pySerial.Serial(port, baud, timeout=0.5)
	
	# Print connection beginning message
	print("Beginning connection to Arduino on serial port: " + str(port))
	
	return ArduinoSerial(ser)



# === Arduino Base Class Definition ===

class ArduinoSerial:
	ser = None
	measurementsPerSecond = 0.25

	def __init__(self, pySerial):
		self.ser = pySerial
		time.sleep(2)
		self.writeSerial('CONN!')
		print(self.getResponse(startsWith='#'), end='')

	def writeSerial(self, message):
		self.ser.write( str(message).encode('UTF-8') )
		#time.sleep(0.05)

	def getResponse(self, startsWith=''):
		response = self.ser.readline().decode(encoding='UTF-8')
		if(startsWith != ''):
			while(len(response) == 0) or (response[0] != startsWith):
				print('SKIPPED:' + str(response))
				response = self.ser.readline().decode(encoding='UTF-8')
		return response

	def takeMeasurement(self):
		self.writeSerial("MEAS!")
		response = self.getResponse(startsWith='{')
		print(response.rstrip())
		sensor_data = json.loads(response)
		return sensor_data



# === Null Arduino Class Definition ===

class NullArduinoSerial(ArduinoSerial):
	def __init__(self):
		pass

	def takeMeasurement(self):
		return {}




