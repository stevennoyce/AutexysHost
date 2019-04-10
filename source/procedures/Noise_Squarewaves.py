# === Imports ===
import time
import numpy as np

from procedures import Device_History as deviceHistoryScript
from utilities import DataLoggerUtility as dlu
from utilities import SequenceGeneratorUtility as dgu


# === Main ===
def run(parameters, smu_instance, isSavingResults=True, isPlottingResults=False):
	# Get shorthand name to easily refer to configuration parameters
	rt_params = parameters['runConfigs']['NoiseCollection']
	
	pointsPerSetpoint = rt_params['pointsPerSetpoint']
	if pointsPerSetpoint is None:
		pointsPerSetpoint = int(2048/len(rt_params['gateVoltages']))
	
	# Print the starting message
	print('Starting Noise Collection')
	smu_instance.setComplianceCurrent(rt_params['complianceCurrent'])	
	
	# === START ===
	for drainVoltage in rt_params['drainVoltages']:
		print('Ramping drain voltage.')
		smu_instance.rampDrainVoltageTo(drainVoltage)
		
		results = runNoiseCollection(smu_instance, 
									measurementSpeed=rt_params['measurementSpeed'],
									drainVoltage=drainVoltage,
									gateVoltages=rt_params['gateVoltages'], 
									pointsPerSetpoint=pointsPerSetpoint)
		
		smu_instance.rampDownVoltages()
		
		# === COMPLETE ===
		
		# Add important metrics from the run to the parameters for easy access later in ParametersHistory
		parameters['Computed'] = results['Computed']
		
		# Copy parameters and add in the test results
		jsonData = dict(parameters)
		jsonData['Results'] = results['Raw']
		
		# Save results as a JSON object
		if(isSavingResults):
			print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
			dlu.saveJSON(dlu.getDeviceDirectory(parameters), rt_params['saveFileName'], jsonData, subDirectory='Ex'+str(parameters['startIndexes']['experimentNumber']))
	
	return jsonData

# === Data Collection ===
def runNoiseCollection(smu_instance, measurementSpeed, drainVoltage, gateVoltages, pointsPerSetpoint):
	Vds = drainVoltage
	Vgs = gateVoltages[0]
	
	smu_instance.rampGateVoltageTo(Vgs)
	
	# totalPoints = pointsPerSetpoint*len(gateVoltages)
	
	smuGateVoltages =  [v for v in gateVoltages for i in range(pointsPerSetpoint)]
	smuDrainVoltages = [drainVoltage for v in gateVoltages for i in range(pointsPerSetpoint)]
	triggerInterval = 1/measurementSpeed
	
	# Use SMU built-in sweep to sweep the gate forwards and backwards
	measurements = smu_instance.takeSweep(Vds, Vds, Vgs, Vgs, 100e3, triggerInterval=triggerInterval, src1vals=smuDrainVoltages, src2vals=smuGateVoltages)
	
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
			
		}
	}


	