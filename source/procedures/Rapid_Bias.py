# === Imports ===
import time
import numpy as np

from utilities import DataLoggerUtility as dlu
from utilities import SequenceGeneratorUtility as dgu



# === Main ===
def run(parameters, smu_instance, isSavingResults=True, isPlottingResults=False):
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
def runRapidBias(smu_instance, waveform, drainVoltageSetPoints, gateVoltageSetPoints, measurementPoints, maxStepInVDS, maxStepInVGS, startGrounded):
	vds_data = []
	id_data = []
	vgs_data = []
	ig_data = []
	timestamps = []
	
	# In the normal case where the terminals start out grounded, just make sure the waveforms correctly start out at 0
	if(startGrounded):
		smu_instance.rampDownVoltages()
		drainVoltageSetPoints = [0] + drainVoltageSetPoints
		gateVoltageSetPoints = [0] + gateVoltageSetPoints
		measurementPoints = [1] + measurementPoints
	
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
	for i in range(len(gateVoltages)):
		# Apply V_GS and V_DS
		smu_instance.setVgs(gateVoltages[i])
		smu_instance.setVds(drainVoltages[i])

		# Take Measurement and save it
		measurement = smu_instance.takeMeasurement()

		timestamp = time.time()
		
		vds_data.append(measurement['V_ds'])
		id_data.append(measurement['I_d'])
		vgs_data.append(measurement['V_gs'])
		ig_data.append(measurement['I_g'])
		timestamps.append(timestamp)
		
	return {
		'Raw':{
			'vds_data':vds_data,
			'id_data':id_data,
			'vgs_data':vgs_data,
			'ig_data':ig_data,
			'timestamps':timestamps,
		},
		'Computed':{
		
		}
	}
	

