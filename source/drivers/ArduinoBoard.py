import serial as pySerial
import time
import json
import numpy as np

def getConnection(port, baud):
	ser = pySerial.Serial(port, baud, timeout=0.5)
	return ArduinoSerial(ser)

def getNullInstance():
	return NullArduinoSerial()

class ArduinoSerial:
	ser = None
	measurementsPerSecond = 0.25

	def __init__(self, pySerial):
		self.ser = pySerial
		time.sleep(2)
		print(self.getResponse(), end='')

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
		return sensor_data

class NullArduinoSerial(ArduinoSerial):
	def __init__(self):
		pass

	def takeMeasurement(self):
		return {}




