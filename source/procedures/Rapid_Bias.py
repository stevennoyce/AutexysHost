# === Imports ===
import time
import numpy as np

import pipes
from utilities import DataLoggerUtility as dlu
from utilities import SequenceGeneratorUtility as dgu



# === Main ===
def run(parameters, smu_instance, isSavingResults=True, isPlottingResults=False, share=None):
	# Get shorthand name to easily refer to configuration parameters
	rb_parameters = parameters['runConfigs']['RapidBias']

	# Print the starting message
	print('Starting rapid bias in ' + str(rb_parameters['waveform']) + ' wave mode.')
	smu_instance.setComplianceCurrent(rb_parameters['complianceCurrent'])	

	# === START ===
	results = runRapidBias(smu_instance, 
							waveform=rb_parameters['waveform'],
							drainVoltageSetPoints=rb_parameters['drainVoltageSetPoints'],
							gateVoltageSetPoints=rb_parameters['gateVoltageSetPoints'],
							measurementPoints= rb_parameters['measurementPoints'],
							averageOverPoints=rb_parameters['averageOverPoints'],
							maxStepInVDS=rb_parameters['maxStepInVDS'],
							maxStepInVGS=rb_parameters['maxStepInVGS'],
							startGrounded=rb_parameters['startGrounded'])
	smu_instance.rampDownVoltages()
	# === COMPLETE ===

	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']
	
	# Print the metrics
	#print('Max current: {:.4f}'.format(results['Computed']['id_max']))

	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
	
	# Save results as a JSON object
	if(isSavingResults):
		print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
		dlu.saveJSON(dlu.getDeviceDirectory(parameters), rb_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))
	
	return jsonData

# === Data Collection ===
def runRapidBias(smu_instance, waveform, drainVoltageSetPoints, gateVoltageSetPoints, measurementPoints, averageOverPoints, maxStepInVDS, maxStepInVGS, startGrounded, share=None):
	vds_data = []
	id_data = []
	vgs_data = []
	ig_data = []
	timestamps = []
	
	# If you start the terminals as grounded, then you can see all of the starting transients and miss nothing
	if(startGrounded):
		smu_instance.rampDownVoltages()
		drainVoltageSetPoints = [0] + drainVoltageSetPoints
		gateVoltageSetPoints = [0] + gateVoltageSetPoints
		measurementPoints = [1] + measurementPoints
	else:
		# Otherwise just ramp to your starting voltages to simplify what is happening
		smu_instance.rampGateVoltageTo(gateVoltageSetPoints[0])
		smu_instance.rampDrainVoltageTo(drainVoltageSetPoints[0])
	
	# Generate waveforms from arrays of set-point values and a corresponding array of the number of times that each set-point should be measured
	gateVoltages = dgu.waveformValues(waveform, gateVoltageSetPoints, measurementPoints, maxStepInVGS)
	drainVoltages = dgu.waveformValues(waveform, drainVoltageSetPoints, measurementPoints, maxStepInVDS)
	
	# Adjust the length of gate and drain voltages
	lengthDifference = len(gateVoltages) - len(drainVoltages)
	if(lengthDifference > 0):
		finalVDS = drainVoltages[-1]
		drainVoltages.extend([finalVDS]*lengthDifference)
	elif(lengthDifference < 0):
		finalVGS = gateVoltages[-1]
		gateVoltages.extend([finalVGS]*lengthDifference)

	# -- at this point gateVoltages and drainVoltages are vectors of points to measure

	# Step through all voltage points to measure
	measurement_buffer = []
	for i in range(len(gateVoltages)):
		# Apply V_GS and V_DS (only issue commands that affect the voltage)
		if((i == 0) or (gateVoltages[i] != gateVoltages[i-1])):
			smu_instance.setVgs(gateVoltages[i])
		if((i == 0) or (drainVoltages[i] != drainVoltages[i-1])):
			smu_instance.setVds(drainVoltages[i])

		# Take Measurement and add it to the buffer
		measurement = smu_instance.takeMeasurement()
		timestamp = time.time()
		
		measurement_buffer.append([measurement, timestamp])
		
		# Once the buffer reaches the desired number of measurements to average over, save the mean data and timestamp and reset the buffer
		if(len(measurement_buffer) >= averageOverPoints):
			vds_data.append(np.mean([entry[0]['V_ds'] for entry in measurement_buffer]))
			id_data.append(np.mean([entry[0]['I_d'] for entry in measurement_buffer]))
			vgs_data.append(np.mean([entry[0]['V_gs'] for entry in measurement_buffer]))
			ig_data.append(np.mean([entry[0]['I_g'] for entry in measurement_buffer]))
			timestamps.append(np.mean([entry[1] for entry in measurement_buffer]))
			measurement_buffer = []
		
	return {
		'Raw':{
			'vds_data':vds_data,
			'id_data':id_data,
			'vgs_data':vgs_data,
			'ig_data':ig_data,
			'timestamps':timestamps,
			'gateVoltages':gateVoltages,
			'drainVoltages':drainVoltages,
		},
		'Computed':{
		
		}
	}
	

