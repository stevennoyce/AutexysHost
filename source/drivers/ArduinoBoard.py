"""This module defines a common Python interface for communicating to Arduino boards over the Arduino Serial interface."""

# === Imports ===
import serial as pySerial
import time
import json
import numpy as np



# === Connection API ===

def getConnection(baud):
	# Iterate over possible USB connections
	ser = None
	for port in ['/dev/cu.wchusbserial1410', '/dev/cu.wchusbserial1420']:
		try:
			ser = pySerial.Serial(port, baud, timeout=0.5)
			break
		except:
			pass
	
	# If not able to connect, return null instance
	if(ser is None): 
		print("No Arduino connected.")
		return NullArduinoSerial()			
	
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
			while(response[0] != startsWith):
				print('SKIPPED:' + str(response))
				response = self.ser.readline().decode(encoding='UTF-8')
		return response

	def takeMeasurement(self):
		self.writeSerial("MEAS!")
		sensor_data = json.loads(self.getResponse(startsWith='{'))
		print(sensor_data)
		return sensor_data



# === Null Arduino Class Definition ===

class NullArduinoSerial(ArduinoSerial):
	def __init__(self):
		pass

	def takeMeasurement(self):
		return {}




