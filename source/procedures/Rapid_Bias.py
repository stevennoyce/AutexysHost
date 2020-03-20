# === Imports ===
import time
import numpy as np

import pipes
import Live_Plot_Data_Point as livePlotter
from utilities import DataLoggerUtility as dlu
from utilities import SequenceGeneratorUtility as dgu



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]
	
	# Get shorthand name to easily refer to configuration parameters
	rb_parameters = parameters['runConfigs']['RapidBias']

	# Print the starting message
	print('Starting rapid bias in ' + str(rb_parameters['waveform']) + ' wave mode.')
	smu_instance.setComplianceCurrent(rb_parameters['complianceCurrent'])	

	# === START ===
	print('Beginning to rapid bias.')
	results = runRapidBias(smu_instance, 
							waveform=rb_parameters['waveform'],
							drainVoltageSetPoints=rb_parameters['drainVoltageSetPoints'],
							gateVoltageSetPoints=rb_parameters['gateVoltageSetPoints'],
							measurementPoints= rb_parameters['measurementPoints'],
							averageOverPoints=rb_parameters['averageOverPoints'],
							maxStepInVDS=rb_parameters['maxStepInVDS'],
							maxStepInVGS=rb_parameters['maxStepInVGS'],
							startGrounded=rb_parameters['startGrounded'],
							supplyDrainVoltage=rb_parameters['supplyDrainVoltage'],
							supplyGateVoltage=rb_parameters['supplyGateVoltage'],
							share=share)
	
	# If any channels were switched into high-resistance mode, switch them back to the typical voltage-source mode
	if(not rb_parameters['supplyDrainVoltage']):
		smu_instance.setChannel1SourceMode(mode='voltage')
	if(not rb_parameters['supplyGateVoltage']):	
		smu_instance.setChannel2SourceMode(mode='voltage')
		
	# Ramp down SMU channels	
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
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), rb_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))
	
	return jsonData

# === Data Collection ===
def runRapidBias(smu_instance, waveform, drainVoltageSetPoints, gateVoltageSetPoints, measurementPoints, averageOverPoints, maxStepInVDS, maxStepInVGS, startGrounded, supplyDrainVoltage=True, supplyGateVoltage=True, share=None):
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
		# Otherwise just ramp to your starting voltages (unless the channels are measuring voltage rather than supplying it)
		if(supplyGateVoltage):
			smu_instance.rampGateVoltageTo(gateVoltageSetPoints[0])
			print('Ramped to starting gate bias.')
		else:
			smu_instance.setChannel2SourceMode(mode='current')
			smu_instance.setIg(0)
		
		if(supplyDrainVoltage):
			smu_instance.rampDrainVoltageTo(drainVoltageSetPoints[0])
			print('Ramped to starting drain bias.')
		else:
			smu_instance.setChannel1SourceMode(mode='current')
			smu_instance.setId(0)
	
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
		# Send a progress message
		pipes.progressUpdate(share, 'Rapid Bias Point', start=0, current=i+1, end=len(gateVoltages))
		
		# Apply V_GS and V_DS (only issue commands that affect the voltage)
		if(supplyGateVoltage and ((i == 0) or (gateVoltages[i] != gateVoltages[i-1]))):
			smu_instance.setVgs(gateVoltages[i])
		if(supplyDrainVoltage and ((i == 0) or (drainVoltages[i] != drainVoltages[i-1]))):
			smu_instance.setVds(drainVoltages[i])

		# Take Measurement and add it to the buffer
		measurement = smu_instance.takeMeasurement()
		timestamp = time.time()
		measurement['timestamp'] = timestamp
		
		measurement_buffer.append(measurement)
		
		# Once the buffer reaches the desired number of measurements to average over, save the mean data and timestamp and reset the buffer
		if(len(measurement_buffer) >= averageOverPoints):
			vds_data.append(np.mean([entry['V_ds'] for entry in measurement_buffer]))
			id_data.append(np.mean([entry['I_d'] for entry in measurement_buffer]))
			vgs_data.append(np.mean([entry['V_gs'] for entry in measurement_buffer]))
			ig_data.append(np.mean([entry['I_g'] for entry in measurement_buffer]))
			timestamps.append(np.mean([entry['timestamp'] for entry in measurement_buffer]))
			measurement_buffer = []
			
			# Send a data message
			pipes.livePlotUpdate(share,plots=
			[livePlotter.createLiveDataPoint(plotID='Current vs. Time', 
												labels=['Drain Current', 'Gate Current'],
												xValues=[timestamps[-1], timestamps[-1]], 
												yValues=[id_data[-1], ig_data[-1]], 
												xAxisTitle='Time (s)', 
												yAxisTitle='Current (A)', 
												yscale='log', 
												plotMode='lines',
												enumerateLegend=False,
												timeseries=True),
			])
		
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
	

