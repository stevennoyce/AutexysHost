"""This module manages the connection between the UI and dispatchers. On startup, this starts the UI and can also immediately give a dispatcher
a schedule file to run, or the UI can be used to navigate schedule files and choose one to run. At any given time, this module can manage 1 UI 
process and 1 dispatcher process."""

# === Imports ===
import multiprocessing as mp
import psutil
import sys
import os

import pipes



# === Defaults ===
# Factory method that returns the default shared memory object that is passed throughout the UI and all Procedures.
def defaultShare():
	sharedMemoryManager = mp.Manager()
	
	share = {
		'sharedMemoryManager': sharedMemoryManager,
		
		'QueueToManager':      mp.Queue(100),
		'QueueToUI':           mp.Queue(100),
		'QueueToDispatcher':   mp.Queue(100),
		'QueueToStatusChecker':mp.Queue(100),
		
		'procedureStopLocations': sharedMemoryManager.list([])
		
		#'d': sharedMemoryManager.dict({'dispatcherRunning':False}),
		#'l': sharedMemoryManager.list([]),
	}
	
	return share



# === Process Priorities ===
def onPosix():
	"""Detect whether running on Windows or Posix."""
	try:
		import posix
		return True
	except ImportError:
		return False

def getProcessPriorityCodes():
	"""Get a dictionary of OS-dependent process priority codes."""
	priorities = {}
	if onPosix():
		# -20 to 20, -20 being highest priority
		priorities[-2] = 18
		priorities[-1] = 9
		priorities[0]  = 0
		priorities[1]  = -9
		priorities[2]  = -18
		priorities[3]  = -20
	else:
		priorities[-2] = psutil.IDLE_PRIORITY_CLASS
		priorities[-1] = psutil.BELOW_NORMAL_PRIORITY_CLASS
		priorities[0]  = psutil.NORMAL_PRIORITY_CLASS
		priorities[1]  = psutil.ABOVE_NORMAL_PRIORITY_CLASS
		priorities[2]  = psutil.HIGH_PRIORITY_CLASS
		priorities[3]  = psutil.REALTIME_PRIORITY_CLASS
	return priorities

def getPriorityCode(priority):
	"""Priority ranges from -2 to 3. Get a valid OS-dependent process priority code."""
	return getProcessPriorityCodes()[priority]

def changePriorityOfProcessAndChildren(pid, priority):
	"""Must be called after starting a process. Change the priority of the process with a given PID and all of its child processes."""
	priorityCode = getPriorityCode(priority)
	
	parent = psutil.Process(pid)
	parent.nice(priorityCode)
	for child in parent.children():
		child.nice(priorityCode)



# === UI ===
def startUI(specific_port, share):
	"""Start a Process running ui.start() and use shared Queues for communication."""
	
	# Clear the UI message queue of old messages before starting a new instance
	pipes.clear(share, 'QueueToUI')
	
	uiProcess = mp.Process(target=runUI, args=(specific_port, share))
	uiProcess.start()
	return uiProcess

def runUI(specific_port, share):
	"""A target method for running the UI that also imports the UI so the parent process does not have that dependency."""
	import ui
	ui.start(share=share, debug=False, use_reloader=False, specific_port=specific_port)



# === Dispatcher ===
def startDispatcher(dispatcher_command, workspace_data_path, share, connection_status=None):
	"""Start a Process running dispatcher.dispatch(dispatcher_command) and use shared Queues for communication."""
	
	# Clear the dispatcher message queue of old messages before starting a new instance
	pipes.clear(share, 'QueueToDispatcher')
	
	# Clear the procedure stop locations since dispatcher is just beginning
	share['procedureStopLocations'][:] = []
	
	dispatcherProcess = mp.Process(target=runDispatcher, args=(dispatcher_command, workspace_data_path, share, connection_status))
	dispatcherProcess.start()
	return dispatcherProcess

def runDispatcher(dispatcher_command, workspace_data_path, share, connection_status=None):
	"""A target method for running the dispatcher that also imports the dispatcher so the parent process does not have that dependency."""
	import dispatcher
	dispatcher.dispatch(dispatcher_command, workspace_data_path, connection_status, share)



# === Measurement System Connection Status ===
def startStatusChecker(share):
	"""Start a Process running the local runStatusChecker function and use shared Queues for communication."""
	
	# Clear the Status Checker message queue of old messages before starting a new instance
	pipes.clear(share, 'QueueToStatusChecker')
	
	statusCheckerProcess = mp.Process(target=runStatusChecker, args=(share,))
	statusCheckerProcess.start()
	return statusCheckerProcess
	
def runStatusChecker(share):
	# These functions that contain calls to the smu drivers should not be run directly by manager.py, so they are only defined locally for this thread.
	from drivers import SourceMeasureUnit as smu
	
	# Keep track of the most recent connection status. Need to track it here so that we don't have to ask the Manager what the previous status was.
	connection_status = None
	
	def updateConnectionStatus(share, previous_status=None):
		updated_status = smu.updateConnectionStatus(previous_status)
		pipes.send(share, 'QueueToManager', {'type':'ConnectionStatus', 'status': updated_status})
		print('[CHECKER]: Sent updated connection status to the Manager.')
		return updated_status

	def connectToMeasurementSystem(share, system):
		requested_status = None
		if(smu.testConnection(system)):
			requested_status = {'connected_system': system}
		return updateConnectionStatus(share, requested_status)
	
	while(True):
		message = pipes.recv(share, 'QueueToStatusChecker') #, timeout=1)
		
		if(message is not None):
			print('[CHECKER]: received message: ' + str(message))
		
			# Check the current status of connected measurement systems, and report this to the Manager
			if(message.get('type') == 'ConnectionStatusRequest'):
				connection_status = updateConnectionStatus(share, connection_status)
			
			# Try to connect to the requested measurement system, and report the resulting success/failure to the Manager
			if(message.get('type') == 'Connect'):
				connection_status = connectToMeasurementSystem(share, dict(message['system']))
			
			# Disconnect from the current measurement system, and notify the Manager when done
			if(message.get('type') == 'Disconnect'):
				connection_status = updateConnectionStatus(share)



# === Main ===
def manage(on_startup_port=None, on_startup_schedule_file=None, on_startup_workspace_data_path=None):
	"""Initialize a UI process and enter an event loop to handle communication with that UI. Manage the creation of dispatcher
	processes to execute schedule files and facilitate communication between the UI and the currently running dispatcher."""
		
	# Create the initial shared memory object for the UI and Dispatcher
	share = defaultShare()
	
	# Create a local memory structure for tracking the latest updated connection status
	connection_status = None
	
	# Spin out the UI sub-process
	ui = startUI(on_startup_port, share)	
	dispatcher = None
	status_checker = startStatusChecker(share)
	
	# Spin out the optional "on-startup" Dispatcher sub-process
	if(on_startup_schedule_file is not None):
		dispatcher = startDispatcher(on_startup_schedule_file, on_startup_workspace_data_path, share)
	
	# === Start ===
	
	# While UI is running, enter an event loop to handle messages that request spinning out a new sub-process
	while(True):
		try:
			message = pipes.recv(share, 'QueueToManager', timeout=1)
			
			# Handle Queue messages
			if(message is not None):
				print('[MANAGER]: revieved message: ' + str(message))
				
				# Spin out a new dispatcher sub-process
				if(message.get('type') == 'Dispatch'):
					if(dispatcher is None):
						dispatcher_command = message['dispatcher_command']
						workspace_data_path = message['workspace_data_path']
						dispatcher = startDispatcher(dispatcher_command, workspace_data_path, share, connection_status)
					else:
						print('[MANAGER]: Error: dispatcher is already running; wait for it to finish before starting another job.')
			
				# Receive updated connection status from the status_checker sub-process, save it and forward that info to the UI
				if(message.get('type') == 'ConnectionStatus'):
					connection_status = message['status']	
					pipes.send(share, 'QueueToUI', message)
					print('[MANAGER]: Sent updated connection status to the UI.')		
					
			
			# If the dispatcher is not running, then check and clear its messages
			if(dispatcher is None):
				while pipes.poll(share, 'QueueToDispatcher'):
					dispMessage = pipes.recv(share, 'QueueToDispatcher')
					print('[MANAGER]: Dispatcher not running, but received message: ' + str(dispMessage))
		
		except Exception as e:
			print('[MANAGER]: loop exception: ', e)
		
		# Check if dispatcher is running, if not join it to explicitly end
		if((dispatcher is not None) and (not dispatcher.is_alive())):
			dispatcher.join()
			dispatcher = None
			pipes.send(share, 'QueueToUI', {'type':'DispatcherStatus', 'status':{'running':False}})
		
		# If dispatcher is not running and UI is dead, exit the event loop
		if((dispatcher is None) and (not ui.is_alive())):
			break
	
	# === Complete ===
	
	# Join to all of the child processes to clean them up
	ui.terminate()
	ui.join()
	if(dispatcher is not None):
		dispatcher.join()
	status_checker.terminate()
	status_checker.join()

	
		
if __name__ == '__main__':
	if len(sys.argv) > 1:
		on_startup_port = sys.argv[1]
		manage(on_startup_port)
	else:
		manage()
