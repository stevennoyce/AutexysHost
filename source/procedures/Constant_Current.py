# === Imports ===
import time
import numpy as np

import pipes
import Live_Plot_Data_Point as livePlotter
from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]
	
	# Get shorthand name to easily refer to configuration parameters
	cc_parameters = parameters['runConfigs']['ConstantCurrent']
	
	# Print the starting message
	print('Constant Current is starting.')
	
	# === START ===
	results = runConstantCurrent(smu_instance,
								 currentApplied=cc_parameters['currentApplied'],
								 currentDuration=cc_parameters['currentDuration'],
								 currentDataInterval=cc_parameters['currentDataInterval'],
								 enableSweep=cc_parameters['enableSweep'],
								 sweepStart=cc_parameters['sweepStart'],
								 sweepEnd=cc_parameters['sweepEnd'],
								 sweepSteps=cc_parameters['sweepSteps'],
								 sweepDelayBetweenMeasurements=cc_parameters['sweepDelayBetweenMeasurements'],
								 sweepFrequency=cc_parameters['sweepFrequency'])
	# === COMPLETE ===
	
	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
	
	# Save results as a JSON object
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), cc_parameters['saveFileName'], jsonData, subDirectory=parameters['experimentSubFolder']+str(parameters['startIndexes']['experimentNumber']))
	
	return jsonData

def runConstantCurrent(smu_instance, currentApplied, currentDuration, currentDataInterval, enableSweep, sweepStart, sweepEnd, sweepSteps, sweepDelayBetweenMeasurements, sweepFrequency):
	voltage_data = []
	current_data = []
	timestamps = []
	sweep_voltage_data = []
	sweep_current_data = []
	sweep_timestamps = []
	sweep_number = []
	
	# Define our sweep function
	def run_sweep(sweepStart, sweepEnd, sweepSteps, sweepDelayBetweenMeasurements, sweepNumber=0):
		# Configure Channels to Run Sweep
		smu_instance.turnChannelsOff()
		smu_instance.setChannel1SourceMode(mode='voltage')
		smu_instance.setChannel2SourceMode(mode='voltage')
		smu_instance.setParameter(":sense1:curr:prot {}".format(100e-6))
		smu_instance.setParameter(":sense2:curr:prot {}".format(100e-6))
		smu_instance.rampDownVoltages()
		smu_instance.turnChannelsOn()
		
		sweep_voltages = dgu.sweepValuesWithDuplicates(sweepStart, sweepEnd, sweepSteps, 1, ramps=2)
		
		run_voltages = []
		run_currents = []
		run_timestamps = []
		run_sweep_numbers = []
		
		# Do Sweep
		for v in sweep_voltages:
			smu_instance.setVgs(v)
			
			timestamp = time.time()
			measurement = smu_instance.takeMeasurement()
			
			run_voltages.append(measurement['V_ds'])
			run_currents.append(measurement['I_d'])
			run_timestamps.append(timestamp)
			run_sweep_numbers.append(sweepNumber)
			
		sweep_voltage_data.append(run_voltages)
		sweep_current_data.append(run_currents)
		sweep_timestamps.append(run_timestamps)
		sweep_number.append(run_sweep_numbers)
		
		# Configure Channels to Run Constant Current
		smu_instance.turnChannelsOff()
		smu_instance.setChannel1SourceMode(mode='voltage')
		smu_instance.setChannel2SourceMode(mode='voltage')
		smu_instance.rampDownVoltages()
		smu_instance.setChannel1SourceMode(mode='current')
		smu_instance.setParameter(":sense1:volt:prot {}".format(cc_parameters['complianceVoltage']))
		smu_instance.rampDrainCurrentDown()
		smu_instance.turnChannel1On()
		smu_instance.turnChannel2Off()
		
		# Set Constant Current
		smu_instance.rampDrainCurrentTo(currentApplied)
	
	
	# Configure Channels to Run Constant Current
	smu_instance.turnChannelsOff()
	smu_instance.setChannel1SourceMode(mode='voltage')
	smu_instance.setChannel2SourceMode(mode='voltage')
	smu_instance.rampDownVoltages()
	smu_instance.setChannel1SourceMode(mode='current')
	smu_instance.setParameter(":sense1:volt:prot {}".format(cc_parameters['complianceVoltage']))
	smu_instance.rampDrainCurrentDown()
	smu_instance.turnChannel1On()
	smu_instance.turnChannel2Off()
	
	# Set Constant Current
	smu_instance.rampDrainCurrentTo(currentApplied)
	
	# Prepare to loop
	start_time = time.time()
	now = lambda: time.time()
	time_elapsed = lambda: now() - start_time
	last_sweep_timestamp = None
	number_of_sweeps_run = 0
	
	while(time_elapsed() < currentDuration):
		# === Sweep ===
		is_time_for_a_sweep = (last_sweep_timestamp is None) or (now() - last_sweep_timestamp > sweepFrequency)
		if(enableSweep and is_time_for_a_sweep):
			number_of_sweeps_run += 1
			run_sweep(sweepStart, sweepEnd, sweepSteps, sweepDelayBetweenMeasurements, sweepNumber=number_of_sweeps_run)
			#time.sleep(5)
			last_sweep_timestamp = now()
		# =============
		
		# === Constant Current ===
		timestamp = time.time()
		measurement = smu_instance.takeMeasurement()
		
		voltage_data.append(measurement['V_ds'])
		current_data.append(measurement['I_d'])
		timestamps.append(timestamp)
		
		# Pause for the interval time
		if(currentDataInterval > 0):
			time.sleep(currentDataInterval)
		# =============
	
	return {
		'Raw': {
			'voltage_data':voltage_data,
			'current_data':current_data,
			'timestamps':timestamps,
			'sweep_voltage_data':sweep_voltage_data,
			'sweep_current_data':sweep_current_data,
			'sweep_timestamps':sweep_timestamps,
			'sweep_number':sweep_number,
		}
	}
	
	
	
	
	
	
	
	
	
	
	
	