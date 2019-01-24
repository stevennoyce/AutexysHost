# === Imports ===
import time
import numpy as np

from procedures import Device_History as deviceHistoryScript
from utilities import DataLoggerUtility as dlu
from utilities import SequenceGeneratorUtility as dgu



# === Main ===
def run(parameters, smu_instance, isSavingResults=True, isPlottingResults=False):
	# Create distinct parameters for plotting the results
	dh_parameters = {}
	dh_parameters['Identifiers'] = dict(parameters['Identifiers'])
	dh_parameters['dataFolder'] = parameters['dataFolder']
	dh_parameters['plotGateSweeps'] = False
	dh_parameters['plotBurnOuts'] = False
	dh_parameters['plotStaticBias'] = False
	dh_parameters['excludeDataBeforeJSONExperimentNumber'] = parameters['startIndexes']['experimentNumber']
	dh_parameters['excludeDataAfterJSONExperimentNumber'] =  parameters['startIndexes']['experimentNumber']

	# Get shorthand name to easily refer to configuration parameters
	ds_parameters = parameters['runConfigs']['DrainSweep']

	# Print the starting message
	print('Sweeping the drain: V_GS='+str(ds_parameters['gateVoltageSetPoint'])+'V, min V_DS='+str(ds_parameters['drainVoltageMinimum'])+'V, max V_DS='+str(ds_parameters['drainVoltageMaximum'])+'V')
	smu_instance.setComplianceCurrent(ds_parameters['complianceCurrent'])	

	# === START ===
	# Apply drain voltage
	print('Ramping gate voltage.')
	smu_instance.rampGateVoltageTo(ds_parameters['gateVoltageSetPoint'])
	
	print('Beginning to sweep drain voltage.')
	results = runDrainSweep( smu_instance, 
							isFastSweep=ds_parameters['isFastSweep'],
							gateVoltageSetPoint=ds_parameters['gateVoltageSetPoint'],
							drainVoltageMinimum=ds_parameters['drainVoltageMinimum'], 
							drainVoltageMaximum=ds_parameters['drainVoltageMaximum'], 
							stepsInVDSPerDirection=ds_parameters['stepsInVDSPerDirection'],
							pointsPerVDS=ds_parameters['pointsPerVDS'],
							drainVoltageRamps=ds_parameters['drainVoltageRamps'])
	smu_instance.rampDownVoltages()
	# === COMPLETE ===

	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']
	
	# Print the metrics
	print('Max conductance: {:.4e}'.format(results['Computed']['G_max']))
	print('Max drain current: {:.4e}'.format(results['Computed']['id_max']))
	print('Max gate current: {:.4e}'.format(results['Computed']['ig_max']))

	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
		
	# Save results as a JSON object
	if(isSavingResults):
		print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
		dlu.saveJSON(dlu.getDeviceDirectory(parameters), ds_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))

	# Show plots to the user
	if(isPlottingResults):
		deviceHistoryScript.run(dh_parameters)
		
	return jsonData

# === Data Collection ===
def runDrainSweep(smu_instance, isFastSweep, gateVoltageSetPoint, drainVoltageMinimum, drainVoltageMaximum, stepsInVDSPerDirection, pointsPerVDS, drainVoltageRamps):
	# Generate list of drain voltages to apply
	drainVoltages = dgu.sweepValuesWithDuplicates(drainVoltageMinimum, drainVoltageMaximum, stepsInVDSPerDirection*2*pointsPerVDS, pointsPerVDS, ramps=drainVoltageRamps)
	
	vds_data   = [[]]*len(drainVoltages)
	id_data    = [[]]*len(drainVoltages)
	vgs_data   = [[]]*len(drainVoltages)
	ig_data    = [[]]*len(drainVoltages)
	timestamps = [[]]*len(drainVoltages)
	
	# Ramp drain and wait a second for everything to settle down
	smu_instance.rampDrainVoltageTo(drainVoltageMinimum)
	time.sleep(1)

	if(isFastSweep):
		# Use SMU built-in sweep to sweep the drain forwards and backwards
		forward_measurements = smu_instance.takeSweep(drainVoltageMinimum, drainVoltageMaximum, gateVoltageSetPoint, gateVoltageSetPoint, stepsInVDSPerDirection)
		reverse_measurements = smu_instance.takeSweep(drainVoltageMaximum, drainVoltageMinimum, gateVoltageSetPoint, gateVoltageSetPoint, stepsInVDSPerDirection)

		# Save forward measurements
		vds_data[0] = forward_measurements['Vds_data']
		id_data[0]  = forward_measurements['Id_data']
		vgs_data[0] = forward_measurements['Vgs_data']
		ig_data[0]  = forward_measurements['Ig_data']
		timestamps[0] = forward_measurements['timestamps']

		# Save reverse measurements
		vds_data[1] = reverse_measurements['Vds_data']
		id_data[1]  = reverse_measurements['Id_data']
		vgs_data[1] = reverse_measurements['Vgs_data']
		ig_data[1]  = reverse_measurements['Ig_data']
		timestamps[1] = reverse_measurements['timestamps']

		# Save true measured Vgs as the applied voltages
		drainVoltages = vds_data
	else:
		for direction in range(len(drainVoltages)):
			for drainVoltage in drainVoltages[direction]:
				# Apply V_DS
				smu_instance.setVds(drainVoltage)

				# Take Measurement and save it
				measurement = smu_instance.takeMeasurement()

				timestamp = time.time()
				
				vds_data[direction].append(measurement['V_ds'])
				id_data[direction].append(measurement['I_d'])
				vgs_data[direction].append(measurement['V_gs'])
				ig_data[direction].append(measurement['I_g'])
				timestamps[direction].append(timestamp)

	return {
		'Raw':{
			'vds_data':vds_data,
			'id_data':id_data,
			'vgs_data':vgs_data,
			'ig_data':ig_data,
			'timestamps':timestamps,
			'drainVoltages':drainVoltages,
		},
		'Computed':{
			'id_max':max(abs(np.array(id_data[0] + id_data[1]))),
			'G_max':max(abs(np.array(id_data[0] + id_data[1]) / np.array(vds_data[0] + vds_data[1]))),
			'ig_max':max(abs(np.array(ig_data[0] + ig_data[1])))
		}
	}

	