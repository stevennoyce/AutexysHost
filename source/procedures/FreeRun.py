# === Imports ===
import time
import numpy as np
import random

import pipes
import Live_Plot_Data_Point as livePlotter
from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_systems, arduino_systems, share=None):
	# This script uses the default SMU, which is the first one in the list of SMU systems
	smu_names = list(smu_systems.keys())
	smu_instance = smu_systems[smu_names[0]]

	# Get shorthand name to easily refer to configuration parameters
	fr_parameters = parameters['runConfigs']['FreeRun']

	# Print the starting message
	print('Free running: min V_DS='+str(fr_parameters['drainVoltageMinimum'])+'V, max V_DS='+str(fr_parameters['drainVoltageMaximum'])+'V, min V_GS='+str(fr_parameters['gateVoltageMinimum'])+'V, max V_GS='+str(fr_parameters['gateVoltageMaximum'])+'V')
	smu_instance.setComplianceCurrent(fr_parameters['complianceCurrent'])

	# === START ===
	print('Beginning to free run.')
	results = runFree( smu_instance,
						pointLimit=fr_parameters['pointLimit'],
						gateVoltageMinimum=fr_parameters['gateVoltageMinimum'],
						gateVoltageMaximum=fr_parameters['gateVoltageMaximum'],
						drainVoltageMinimum=fr_parameters['drainVoltageMinimum'],
						drainVoltageMaximum=fr_parameters['drainVoltageMaximum'],
						delayBetweenMeasurements=fr_parameters['delayBetweenMeasurements'],
						gateVoltageDistribution=fr_parameters['gateVoltageDistribution'],
						drainVoltageDistribution=fr_parameters['drainVoltageDistribution'],
						share=share)
	
	# Ramp down channels
	smu_instance.rampDownVoltages()
	# === COMPLETE ===

	# Copy parameters and add in the test results
	jsonData = dict(parameters)

	return jsonData

# === Data Collection ===
def runFree(smu_instance, pointLimit, gateVoltageMinimum, gateVoltageMaximum, drainVoltageMinimum, drainVoltageMaximum, delayBetweenMeasurements, gateVoltageDistribution='uniform', drainVoltageDistribution='uniform', share=None):
	index = 0
	
	# Define possible distributions
	distributions = {
		'uniform': lambda minimum, maximum: random.uniform(minimum, maximum),
		'striped': lambda minimum, maximum: random.choice(np.linspace(minimum, maximum, 5)),
	}
	nextGateVoltage = distributions[gateVoltageDistribution]
	nextDrainVoltage = distributions[drainVoltageDistribution]
	
	# Begin continuously applying randomly selected voltages from their distributions and taking measurements (until an interrupt is triggers by pipes, or a limit is reached)
	while((pointLimit is None) or (index < pointLimit)):
		# Send a progress message
		pipes.progressUpdate(share, 'Free Run Point', start=0, current=index, end=(pointLimit if(pointLimit is not None) else index))
		index += 1

		# Get drain and gate voltage from random distributions
		gateVoltage  = nextGateVoltage(gateVoltageMinimum, gateVoltageMaximum)
		drainVoltage = nextDrainVoltage(drainVoltageMinimum, drainVoltageMaximum)

		# Apply bias voltages
		smu_instance.rampGateVoltageTo(gateVoltage, steps=10)
		smu_instance.rampDrainVoltageTo(drainVoltage, steps=10)

		# If delayBetweenMeasurements is non-zero, wait before taking the measurement
		if(delayBetweenMeasurements > 0):
			time.sleep(delayBetweenMeasurements)

		# Take Measurement and save it
		measurement = smu_instance.takeMeasurement()

		# Send a data message
		pipes.livePlotUpdate(share, plots=
		[livePlotter.createDataSeries(plotID='transfer', 
										xValues=[measurement['V_gs']], 
										yValues=[measurement['I_d']], 
										xAxisTitle='Gate Voltage (V)', 
										yAxisTitle='Drain Current (A)', 
										yscale='linear', 
										enumerateLegend=False,
										timeseries=False),
		 livePlotter.createDataSeries(plotID='subthreshold', 
										xValues=[measurement['V_gs']], 
										yValues=[measurement['I_d']], 
										xAxisTitle='Gate Voltage (V)', 
										yAxisTitle='Drain Current (A)', 
										yscale='log', 
										enumerateLegend=False,
										timeseries=False),
		 livePlotter.createDataSeries(plotID='output', 
										xValues=[measurement['V_ds']], 
										yValues=[measurement['I_d']], 
										xAxisTitle='Drain Voltage (V)', 
										yAxisTitle='Drain Current (A)', 
										yscale='linear', 
										enumerateLegend=False,
										timeseries=False),
		])
			
	return {
		
	}



	