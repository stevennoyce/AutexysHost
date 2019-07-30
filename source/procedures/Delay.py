# === Imports ===
import time

import pipes

# === Main ===
def run(parameters, share=None):
	# No setup required, just run
	runDelay(parameters)	

def runDelay(parameters, share=None):
	d_parameters = parameters['runConfigs']['Delay']
	print('Starting ' + str(d_parameters['delayTime']) + "s Delay...")
	print(d_parameters['message'])
	time.sleep(d_parameters['delayTime'])

