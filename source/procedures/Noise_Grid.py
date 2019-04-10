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
	
	# Get shorthand name to easily refer to configuration parameters
	gs_parameters = parameters['runConfigs']['GateSweep']
	
	# Print the starting message
	print('Measuring Noise: V_DS='+str(gs_parameters['drainVoltageSetPoint'])+'V, min V_GS='+str(gs_parameters['gateVoltageMinimum'])+'V, max V_GS='+str(gs_parameters['gateVoltageMaximum'])+'V')
	smu_instance.setComplianceCurrent(gs_parameters['complianceCurrent'])	
	
	# === START ===
	# Apply drain voltage
	print('Ramping drain voltage.')
	smu_instance.rampDrainVoltageTo(gs_parameters['drainVoltageSetPoint'])
	
	print('Beginning to sweep gate voltage.')
	results = runNoiseGrid( smu_instance, 
							isFastSweep=gs_parameters['isFastSweep'],
							fastSweepSpeed=gs_parameters['fastSweepSpeed'],
							drainVoltageSetPoint=gs_parameters['drainVoltageSetPoint'],
							gateVoltageMinimum=gs_parameters['gateVoltageMinimum'], 
							gateVoltageMaximum=gs_parameters['gateVoltageMaximum'], 
							stepsInVGSPerDirection=gs_parameters['stepsInVGSPerDirection'],
							pointsPerVGS=gs_parameters['pointsPerVGS'],
							gateVoltageRamps=gs_parameters['gateVoltageRamps'])
	smu_instance.rampDownVoltages()
	# === COMPLETE ===
	
	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']
	
	# Print the metrics
	print('Current Mean: {:.4f}'.format(results['Computed']['onOffRatio']))
	print('Current Std Dev: {:.4e}'.format(results['Computed']['onCurrent']))
	print('SNR: {:.4e}'.format(results['Computed']['offCurrent']))
	print('Slope: {:.4e}'.format(results['Computed']['ig_max']))
	
	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']
	
	# Save results as a JSON object
	if(isSavingResults):
		print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
		dlu.saveJSON(dlu.getDeviceDirectory(parameters), gs_parameters['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))
	
	# Show plots to the user
	if(isPlottingResults):
		deviceHistoryScript.run(dh_parameters)
	
	return jsonData

# === Data Collection ===
def runNoiseGrid(smu_instance, speed, drainVoltage, gateVoltage, points, gateVoltageRamps):
	# Ramp gate and wait a second for everything to settle down
	smu_instance.rampGateVoltageTo(gateVoltageMinimum)
	time.sleep(1)
	
	triggerInterval = 1/speed
	
	# Use SMU built-in sweep to sweep the gate forwards and backwards
	measurements = smu_instance.takeSweep(drainVoltage, drainVoltage, gateVoltage, gateVoltage, steps, triggerInterval=triggerInterval)
	
	# Save forward measurements
	vds_data = measurements['Vds_data']
	id_data  = measurements['Id_data']
	vgs_data = measurements['Vgs_data']
	ig_data  = measurements['Ig_data']
	timestamps = measurements['timestamps']
	
	# Save true measured Vgs as the applied voltages
	gateVoltages = vgs_data

	return {
		'Raw':{
			'vds_data':vds_data,
			'id_data':id_data,
			'vgs_data':vgs_data,
			'ig_data':ig_data,
			'timestamps':timestamps,
			'gateVoltages':gateVoltages,
		},
		'Computed':{
			'onOffRatio':onOffRatio(id_data),
			'onCurrent':onCurrent(id_data),
			'offCurrent':offCurrent(id_data),
			'ig_max':max(abs(np.array(ig_data[0] + ig_data[1])))
		}
	}

def onOffRatio(drainCurrent):
	return onCurrent(drainCurrent)/offCurrent(drainCurrent)

def onCurrent(drainCurrent):
	absDrainCurrent = abs(np.array(drainCurrent))
	return np.percentile(absDrainCurrent, 99)

def offCurrent(drainCurrent):
	absDrainCurrent = abs(np.array(drainCurrent))
	return (np.percentile(absDrainCurrent, 5))

	