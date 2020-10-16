# === Imports ===
import time
import numpy as np

import pipes



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]

	# Print the starting message
	print('Starting Benchtop Mode.')
	smu_instance.rampDownVoltages()

	# === START ===	
	results = runBenchtop(smu_instance, share=share)
	
	# Ramp down channels
	smu_instance.rampDownVoltages()
	# === COMPLETE ===


# === Data Collection ===
def runBenchtop(smu_instance, share=None):
	MINIMUM_REFRESH_RATE = 0.1
	MAXIMUM_REFRESH_RATE = 10
	refresh_rate = 1
	
	while(True):
		message = pipes.recv(share, 'QueueToDispatcher', timeout=1/max( min(refresh_rate,MAXIMUM_REFRESH_RATE) , MINIMUM_REFRESH_RATE ))
				
		if(message is not None):			
			if(message.get('type') == 'SetVoltage'):
				if(message['channel'] == 1):
					smu_instance.setVds(float(message['voltage']))
				elif(message['channel'] == 2):
					smu_instance.setVgs(float(message['voltage']))
			
			if(message.get('type') == 'SetRefreshRate'):
				refresh_rate = float(message['refresh_rate'])
			
			if(message.get('type') == 'Stop'):
				raise pipes.AbortError('Aborting Benchtop measurements.')
	
		measurement = smu_instance.takeMeasurement()
		timestamp = time.time()

		pipes.send(share, 'QueueToUI', {'type': 'BenchtopMeasurement', 'measurement':measurement, 'timestamp':timestamp})


				

	