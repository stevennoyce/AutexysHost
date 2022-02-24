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
	fpp_parameters = parameters['runConfigs']['FourPointProbe']

	# Print the starting message
	print('Running 4-point probe measurement.')
	smu_instance.setComplianceVoltage(fpp_parameters['complianceVoltage'])
	smu_instance.setParameter(":sense1:remote ON")
	smu_instance.setChannel1SourceMode("current")

	# === START ===
	print('Beginning to sweep current.')
	results = runFourPointProbe( smu_instance,
							drainCurrentStart=1e-6,
							drainCurrentEnd=1e-3,
							steps=100,
							delayBetweenMeasurements=0,
							share=share)
	
	# Ramp down channels
	smu_instance.rampDrainCurrentDown()
	# === COMPLETE ===

	# Add important metrics from the run to the parameters for easy access later in ParametersHistory
	parameters['Computed'] = results['Computed']

	# Copy parameters and add in the test results
	jsonData = dict(parameters)
	jsonData['Results'] = results['Raw']

	# Save results as a JSON object
	print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
	dlu.saveJSON(dlu.getDeviceDirectory(parameters), fpp_parameters['saveFileName'], jsonData, subDirectory=parameters['experimentSubFolder']+str(parameters['startIndexes']['experimentNumber']))

	return jsonData

# === Data Collection ===
def runFourPointProbe(smu_instance, drainCurrentStart, drainCurrentEnd, steps, delayBetweenMeasurements, share=None):
	drainCurrents = dgu.sweepValues(drainCurrentStart, drainCurrentEnd, steps)

	vds_data   = []
	id_data    = []
	timestamps = []

	# Ramp gate and wait a second for everything to settle down
	smu_instance.rampDrainCurrentTo(drainCurrentStart)
	time.sleep(1)

	for direction, _ in enumerate(drainCurrents):
		for i, drainCurrent in enumerate(drainCurrents[direction]):
			# Send a progress message
			pipes.progressUpdate(share, 'Four Point Probe', start=0, current=direction*len(drainCurrents[0])+i+1, end=len(drainCurrents)*len(drainCurrents[0]))

			# Apply I_d
			smu_instance.setId(drainCurrent)

			# If delayBetweenMeasurements is non-zero, wait before taking the measurement
			if(delayBetweenMeasurements > 0):
				time.sleep(delayBetweenMeasurements)

			# Take Measurement and save it
			measurement = smu_instance.takeMeasurement()

			timestamp = time.time()

			vds_data.append(measurement['V_ds'])
			id_data.append(measurement['I_d'])
			timestamps.append(timestamp)

			# Send a data message
			pipes.livePlotUpdate(share, plots=
			[livePlotter.createLiveDataPoint(plotID='Four Point Probe', 
											labels=['Drain Voltage'],
											xValues=[measurement['I_d']], 
											yValues=[measurement['V_ds']], 
											#colors=['', '#4FB99F'],
											xAxisTitle='Current (A)', 
											yAxisTitle='Voltage (V)', 
											yscale='linear', 
											plotMode='lines',
											enumerateLegend=True,
											timeseries=False),
			livePlotter.createLiveDataPoint(plotID='Resistance', 
											labels=['Resistance'],
											xValues=[measurement['I_d']], 
											yValues=[measurement['V_ds']/measurement['I_d']], 
											#colors=['', '#4FB99F'],
											xAxisTitle='Current (A)', 
											yAxisTitle='Resistance (Ω)', 
											yscale='linear', 
											plotMode='lines',
											enumerateLegend=True,
											timeseries=False),
			livePlotter.createLiveDataPoint(plotID='Surface Resistance', 
											labels=['Surface Resistance'],
											xValues=[measurement['I_d']], 
											yValues=[np.pi/np.log(2)*measurement['V_ds']/measurement['I_d']], 
											#colors=['', '#4FB99F'],
											xAxisTitle='Current (A)', 
											yAxisTitle='Surface Resistance (Ω)', 
											yscale='linear', 
											plotMode='lines',
											enumerateLegend=True,
											timeseries=False),
			])
			
	return {
		'Raw':{
			'vds_data':vds_data,
			'id_data':id_data,
			'timestamps':timestamps,
		},
		'Computed':{
			
		}
	}



	