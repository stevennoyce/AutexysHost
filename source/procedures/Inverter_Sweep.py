# === Imports ===
import time
import numpy as np

import pipes
import Live_Plot_Data_Point as livePlotter
from utilities import DataLoggerUtility as dlu
from utilities import SequenceGeneratorUtility as dgu



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses two SMUs, one for applying the power supply and one for measuring VIN/VOUT
	smu_sweep = smu_systems['logicSignalSMU']
	smu_vdd = smu_systems['powerSupplySMU']
	
	# Get shorthand name to easily refer to configuration parameters
	is_parameters = parameters['runConfigs']['InverterSweep']

	# Print the starting message
	print('Sweeping the inverter: V_DD='+str(is_parameters['vddSupplyVoltageSetPoint'])+'V, min V_IN='+str(is_parameters['inputVoltageMinimum'])+'V, max V_IN='+str(is_parameters['inputVoltageMaximum'])+'V')
	smu_sweep.setComplianceCurrent(is_parameters['complianceCurrent'])	
	smu_vdd.setComplianceCurrent(is_parameters['complianceCurrent'])	

	# === START ===
	# Apply V_DD to the inverter
	print('Ramping supply voltage (VDD).')
	smu_vdd.rampDrainVoltageTo(is_parameters['vddSupplyVoltageSetPoint'])
	
	# Switch Channel 1 of smu_sweep into current-sourcing mode so that it can measure V_OUT without applying a voltage to the output side
	smu_sweep.setChannel1SourceMode(mode="current")
	smu_sweep.setId(0)
	
	print('Beginning to sweep input voltage.')
	results = runInverterSweep( smu_sweep, 
							inputVoltageMinimum=is_parameters['inputVoltageMinimum'], 
							inputVoltageMaximum=is_parameters['inputVoltageMaximum'], 
							stepsInVINPerDirection=is_parameters['stepsInVINPerDirection'],
							pointsPerVIN=is_parameters['pointsPerVIN'],
							inputVoltageRamps=is_parameters['inputVoltageRamps'],
							delayBetweenMeasurements=is_parameters['delayBetweenMeasurements'],
							share=share)
	
	# Switch Channel 1 of smu_sweep back to normal voltage-sourcing mode
	smu_sweep.setChannel1SourceMode(mode="voltage")
	smu_sweep.setVds(0)
	
	# Ramp down SMU channels
	smu_sweep.rampDownVoltages()
	smu_vdd.rampDownVoltages()
	# === COMPLETE ===

	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']
	
	# Print the metrics
	print('Max input current: {:.4e}'.format(results['Computed']['iin_max']))
	print('Min input current: {:.4e}'.format(results['Computed']['iin_min']))
	print('Max output current: {:.4e}'.format(results['Computed']['iout_max']))
	print('Min output current: {:.4e}'.format(results['Computed']['iout_min']))

	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
		
	# Save results as a JSON object
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), is_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))

	return jsonData

# === Data Collection ===
def runInverterSweep(smu_sweep, inputVoltageMinimum, inputVoltageMaximum, stepsInVINPerDirection, pointsPerVIN, inputVoltageRamps, delayBetweenMeasurements, share=None):
	# Generate list of input voltages to apply
	inputVoltages = dgu.sweepValuesWithDuplicates(inputVoltageMinimum, inputVoltageMaximum, stepsInVINPerDirection*2*pointsPerVIN, pointsPerVIN, ramps=inputVoltageRamps)
	
	vin_data   = [[] for i in range(len(inputVoltages))]
	iin_data   = [[] for i in range(len(inputVoltages))]
	vout_data  = [[] for i in range(len(inputVoltages))]
	iout_data  = [[] for i in range(len(inputVoltages))]
	timestamps = [[] for i in range(len(inputVoltages))]
	
	# Ramp V_IN and wait a second for everything to settle down
	smu_sweep.rampGateVoltageTo(inputVoltageMinimum)
	time.sleep(1)

	for direction in range(len(inputVoltages)):
		for (VINi, inputVoltage) in enumerate(inputVoltages[direction]):
			# Send a progress message
			pipes.progressUpdate(share, 'Inverter Sweep Point', start=0, current=direction*len(inputVoltages[0])+VINi+1, end=len(inputVoltages)*len(inputVoltages[0]))
			
			# Apply V_IN
			smu_sweep.setVgs(inputVoltage)

			# If delayBetweenMeasurements is non-zero, wait before taking the measurement
			if(delayBetweenMeasurements > 0):
				time.sleep(delayBetweenMeasurements)

			# Take Measurement and save it
			measurement = smu_sweep.takeMeasurement()

			timestamp = time.time()
			
			vin_data[direction].append(measurement['V_gs'])
			iin_data[direction].append(measurement['I_g'])
			vout_data[direction].append(measurement['V_ds'])
			iout_data[direction].append(measurement['I_d'])
			timestamps[direction].append(timestamp)

			# Send a data message
			preppedInputVoltage = inputVoltage if abs((inputVoltage - measurement['V_gs'])) < abs(0.1*inputVoltage) else measurement['V_gs']
			pipes.livePlotUpdate(share, plots=
			[livePlotter.createDataPoint(plotID='Voltage Transfer Characteristic', 
											label='Output Voltage',
											xValue=preppedInputVoltage, 
											yValue=measurement['V_ds'],
											xAxisTitle='Input Voltage (V)', 
											yAxisTitle='Voltage (V)', 
											yscale='lin', 
											enumerateLegend=True,
											timeseries=False),
			 livePlotter.createDataPoint(plotID='Output Voltage vs. Time', 
											label='Output Voltage',
											xValue=timestamp, 
											yValue=measurement['V_ds'],
											xAxisTitle='Time (s)', 
											yAxisTitle='Voltage (V)', 
											yscale='lin', 
											enumerateLegend=True,
											timeseries=True),
			])
		livePlotter.incrementActivePlots()

	# Ramp V_IN down to zero
	smu_sweep.rampGateVoltageDown()

	return {
		'Raw':{
			'vin_data':vin_data,
			'iin_data':iin_data,
			'vout_data':vout_data,
			'iout_data':iout_data,
			'timestamps':timestamps,
			'inputVoltages':inputVoltages,
		},
		'Computed':{
			'iin_max':  np.max(np.abs(iin_data)),
			'iin_min':  np.min(np.abs(iin_data)),
			'iout_max': np.max(np.abs(iout_data)),
			'iout_min': np.min(np.abs(iout_data)),
		}
	}


	