# === Imports ===
import time

import pipes

# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# No setup required, just run
	runDelay(parameters, smu_systems, arduino_systems, share=share)	

def runDelay(parameters, smu_systems, arduino_systems, share=None):
	d_parameters = parameters['runConfigs']['Delay']
	print('Starting ' + str(d_parameters['delayTime']) + "s Delay...")
	print(d_parameters['message'])
	time.sleep(d_parameters['delayTime'])

