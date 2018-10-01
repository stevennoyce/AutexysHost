# === Imports ===
import time

# === Main ===
def run(parameters):
	# No setup required, just run
	runDelay(parameters)	

def runDelay(parameters):
	delay_parameters = parameters['runConfigs']['Delay']
	print('Starting ' + str(delay_parameters['delayTime']) + "s Delay...")
	print(delay_parameters['message'])
	time.sleep(delay_parameters['delayTime'])

