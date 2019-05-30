# === Imports ===
import time
import numpy as np
import threading

from utilities import DataLoggerUtility as dlu



# === Main ===
def run(parameters, smu_systems, isSavingResults=True):
	# Print the starting message
	print('Beginning AFM-assisted measurements.')
	runAFM(parameters, smu_systems, isSavingResults)	
	# return jsonData



# === Data Collection ===
def runAFM(parameters, smu_systems, isSavingResults=True):
	# Duke label 184553 is 'USB0::0x0957::0x8E18::MY51141244::INSTR' - use for device drain (CH1) and gate (CH2)
	# Duke Label 184554 is 'USB0::0x0957::0x8E18::MY51141241::INSTR' - use for AFM channels x (CH1) and y (CH2)
	
	# Get shorthand name to easily refer to configuration and SMUs
	afm_parameters = parameters['runConfigs']['SGMControl']
	smu_device = smu_systems['deviceSMU']
	smu_secondary = smu_systems['secondarySMU']
	vds = afm_parameters['drainVoltageSetPoint']
	vgs = afm_parameters['gateVoltageSetPoint']
	
	# Set SMU NPLC
	smu_device.setNPLC(1)
	smu_secondary.setNPLC(1)
	
	# Set a low compliance current for startup
	smu_device.setComplianceCurrent(10e-9)
	
	smu_device.setBinaryDataTransfer(True)
	smu_secondary.setBinaryDataTransfer(True)
	
	# Turn the device channels on and wait for system capacitances to charge
	print('Turning device channels on and waiting for equilibration')
	smu_device.turnChannelsOn()
	for i in range(5):
		print(smu_device.takeMeasurement())
		time.sleep(0.1)
	
	# Turn the voltage measurement channels on and wait
	print('Turning voltage measurement channels on')
	smu_secondary.turnChannelsOn()
	time.sleep(0.1)
	
	# Set SMU compliance to setpoints
	print('Setting device compliance to setpoint')
	smu_device.setComplianceCurrent(afm_parameters['complianceCurrent'])
	time.sleep(0.1)
	
	print('Setting voltage measurement compliance to setpoint')
	smu_secondary.setComplianceVoltage(afm_parameters['complianceVoltage'])
	time.sleep(0.1)
	
	print('Waiting for specified delay time before applying voltages')
	time.sleep(afm_parameters['delayBeforeApplyingVoltages'])
	
	# Apply Vgs and Vds to the device
	print('Ramping drain to source voltage')
	smu_device.rampDrainVoltageTo(vds, steps=40)
	print('Ramping gate to source voltage')
	smu_device.rampGateVoltageTo(vgs, steps=40)
	
	# Take a measurement to update the SMU visual displays
	smu_device.takeMeasurement()
	smu_secondary.takeMeasurement()
	
	# Setup hardware triggers
	smu_device.enableHardwareArmReception(2)
	smu_secondary.enableHardwareArmReception(2)
	
	# input('Press enter to begin the measurement...')
	
	# Compute time per trace, pass (aka 2 traces) and line (aka topology pass + nap pass), as well as the approx number of points to collect per pass
	passTime = 1/afm_parameters['scanRate']
	traceTime = passTime/2
	lineTime = 2*traceTime
	if(afm_parameters['napOn']):
		lineTime = lineTime*2
	measurementTime = traceTime*afm_parameters['tracesToMeasure']
	passPoints = int(afm_parameters['deviceMeasurementSpeed']*measurementTime*1.02 + 2)
	
	# print('Waiting for 4 line times to ensure that previous scan has completed')
	# time.sleep(4*lineTime)
	
	# Choose the amount of time it takes for the SMU to measure one point
	interval = 1/afm_parameters['deviceMeasurementSpeed']
	
	passPoints2 = 1*passPoints
	interval2 = 1*interval
	if False:
		passPoints2 = min(passPoints, 100*afm_parameters['tracesToMeasure'])
		interval2 = max(interval, int(measurementTime/passPoints2))
	
	# Prepare the SMUs to collect data in sweep mode
	sleep_time1 = smu_device.setupSweep(vds, vds, vgs, vgs, passPoints, triggerInterval=interval)
	sleep_time2 = smu_secondary.setupSweep(0, 0, 0, 0, passPoints2, triggerInterval=interval2)
	
	# If desired, wait for the AFM to reach the end of a scan before beginning
	if(afm_parameters['startOnFrameSwitch']):
		waitForFrameSwitch(smu_secondary, lineTime)
	
	for scan in range(afm_parameters['scans']):
		print('Starting scan {} of {}'.format(scan+1, afm_parameters['scans']))
		
		meanYs = []
		deltaMeanYs = []
		
		smu_device.setTimeout(timeout_ms=int(120e3))
		smu_secondary.setTimeout(timeout_ms=int(120e3))
		
		for line in range(afm_parameters['lines']):
			print('Starting line {} of {} (scan {} of {})'.format(line+1, afm_parameters['lines'], scan+1, afm_parameters['scans']))
			
			if line == 1:
				smu_device.setTimeout(timeout_ms=int(4*lineTime*1e3))
				smu_secondary.setTimeout(timeout_ms=int(4*lineTime*1e3))
			
			results = runAFMline(parameters, smu_systems, sleep_time1, sleep_time2)
			
			# Detect line timeout
			if results['Raw']['timestamps_device'] is None or results['Raw']['timestamps_smu2'] is None:
				print('Ending scan due to line timeout')
				break
			
			# Determine frame switch
			if False:
				meanY = np.mean(results['Raw']['smu2_v1_data'])
				meanYs.append(meanY)
				if len(meanYs) > 1:
					deltaMeanYs.append(meanYs[-1] - meanYs[-2])
				if len(meanYs) > 6:
					if (deltaMeanYs[-1]*np.median(deltaMeanYs) < 0) and (deltaMeanYs[-2]*np.median(deltaMeanYs) < 0):
						print('Ending scan due to detected frame reversal')
						print(meanYs)
						print(deltaMeanYs)
						print(np.median(deltaMeanYs))
						break
			
			# Copy parameters and add in the test results
			parameters['Computed'] = results['Computed']
			parameters['Computed']['scan'] = int(scan)
			jsonData = dict(parameters)
			jsonData['Results'] = results['Raw']
			jsonData['Results']['scan'] = int(scan)
			
			# Save results as a JSON object
			if(isSavingResults):
				print('Saving JSON: ' + str(dlu.getDeviceDirectory(parameters)))
				# Spin a new thread to save the data in the background
				threading.Thread(target=dlu.saveJSON,
					args=(dlu.getDeviceDirectory(parameters), afm_parameters['saveFileName'], jsonData, 'Ex'+str(parameters['startIndexes']['experimentNumber']))
				).start()
	
	# smu_device.turnChannelsOff()



def runAFMline(parameters, smu_systems, sleep_time1, sleep_time2):
	# Get shorthand name to easily refer to configuration and SMUs
	afm_parameters = parameters['runConfigs']['SGMControl']
	smu_device = smu_systems['deviceSMU']
	smu_secondary = smu_systems['secondarySMU']
	
	# Arm the instruments
	# smu_device.arm()
	# smu_secondary.arm()
	
	smu_device.initSweep()
	smu_secondary.initSweep()
	
	startTime = time.time()
	print('Waiting for nap trigger')
	
	# Sleep for a portion of the time it takes for the data to be collected
	# time.sleep(0.5*min(sleep_time1, sleep_time2))
	
	# Request data from the SMUs
	results_device = smu_device.endSweep(includeVoltages=False)
	results_secondary = smu_secondary.endSweep(includeCurrents=False)
	
	endTime = time.time()
	
	# Adjust timestamps to be in realtime values
	timestamps_device = [endTime + t for t in results_device['timestamps']] if results_device['timestamps'] is not None else None
	timestamps_smu2 = [endTime + t for t in results_secondary['timestamps']] if results_secondary['timestamps'] is not None else None
	
	XVoltageKey = 'Vds_data'
	YVoltageKey = 'Vgs_data'
	
	if afm_parameters['XYCableSwap']:
		XVoltageKey, YVoltageKey = YVoltageKey, XVoltageKey
	
	return {
		'Raw':{
			# 'vds_data':	results_device['Vds_data'],
			'id_data':	results_device['Id_data'],
			# 'vgs_data':	results_device['Vgs_data'],
			'ig_data':	results_device['Ig_data'],
			'timestamps_device': timestamps_device,
			'smu2_v1_data':	results_secondary[YVoltageKey],
			# 'smu2_i1_data':	results_secondary['Id_data'],
			'smu2_v2_data':	results_secondary[XVoltageKey],
			# 'smu2_i2_data':	results_secondary['Ig_data'],
			'timestamps_smu2': timestamps_smu2
		},
		'Computed':{
			
		}
	}

if(__name__=='__main__'):
	print('Running SGM Control as Main')
	
	if sys.argv[2] == 'start':
		print('Setting up')

	