# === Imports ===
import time

import pipes

# === Main ===
def run(parameters, share=None):
	# No setup required, just run
	runDelay(parameters)	

def runDelay(parameters, share=None):
	delay_parameters = parameters['runConfigs']['Delay']
	print('Starting ' + str(delay_parameters['delayTime']) + "s Delay...")
	print(delay_parameters['message'])
	time.sleep(delay_parameters['delayTime'])

