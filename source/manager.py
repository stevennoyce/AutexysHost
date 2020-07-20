"""This module manages the connection between the UI and dispatchers. On startup, this starts the UI and can also immediately give a dispatcher
a schedule file to run, or the UI can be used to navigate schedule files and choose one to run. At any given time, this module can manage 1 UI 
process and 1 dispatcher process."""

# === Imports ===
import multiprocessing as mp
import psutil
import sys
import os

import pipes

# === Make this script runnable ===
if __name__ == '__main__':
	os.chdir(sys.path[0])
	
	pathParents = os.getcwd().split('/')
	if 'AutexysHost' in pathParents:
		os.chdir(os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source'))

# === Defaults ===
# Factory method that returns the default shared memory object that is passed throughout the UI and all Procedures.
def defaultShare():
	sharedMemoryManager = mp.Manager()
	
	share = {
		'sharedMemoryManager': sharedMemoryManager,
		
		'QueueToManager':      mp.Queue(100),
		'QueueToUI':           mp.Queue(100),
		'QueueToDispatcher':   mp.Queue(100),
		
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
def startUI(specific_port, share, priority=0):
	"""Start a Process running ui.start() and obtain a two-way Pipe for communication."""
	pipeToUI, pipeForUI = mp.Pipe()
	share['p'] = pipeForUI
	
	# Clear the UI message queue of old messages before starting a new instance
	pipes.clear(share, 'QueueToUI')
	
	uiProcess = mp.Process(target=runUI, args=(specific_port, share))
	uiProcess.start()
	# changePriorityOfProcessAndChildren(uiProcess.pid, priority)
	return {'process':uiProcess, 'pipe':pipeToUI}

def runUI(specific_port, share):
	"""A target method for running the UI that also imports the UI so the parent process does not have that dependency."""
	import ui
	ui.start(share=share, debug=False, use_reloader=False, launch_browser=True, specific_port=specific_port)



# === Dispatcher ===
def startDispatcher(scheduleFilePath, share, priority=0):
	"""Start a Process running dispatcher.dispatch(scheduleFilePath) and obtain a two-way Pipe for communication."""
	pipeToDispatcher, pipeForDispatcher = mp.Pipe()
	share['p'] = pipeForDispatcher
	
	# Clear the dispatcher message queue of old messages before starting a new instance
	pipes.clear(share, 'QueueToDispatcher')
	
	# Clear the procedure stop locations since dispatcher is just beginning
	share['procedureStopLocations'][:] = []
	
	dispatcherProcess = mp.Process(target=runDispatcher, args=(scheduleFilePath, share))
	dispatcherProcess.start()
	# changePriorityOfProcessAndChildren(dispatcherProcess.pid, priority)
	return {'process':dispatcherProcess, 'pipe':pipeToDispatcher}

def runDispatcher(scheduleFilePath, share):
	"""A target method for running the dispatcher that also imports the dispatcher so the parent process does not have that dependency."""
	import dispatcher
	dispatcher.dispatch(scheduleFilePath, share)



# === Main ===
def manage(on_startup_schedule_file=None, on_startup_port=None):
	"""Initialize a UI process and enter an event loop to handle communication with that UI. Manage the creation of dispatcher
	processes to execute schedule files and facilitate communication between the UI and the currently running dispatcher."""
		
	# Create the initial shared memory object for the UI and Dispatcher
	share = defaultShare()
	
	# Spin out the UI sub-process
	ui = startUI(on_startup_port, share, priority=0)	
	dispatcher = None
	
	# Spin out the optional "on-startup" Dispatcher sub-process
	if(on_startup_schedule_file is not None):
		dispatcher = startDispatcher(on_startup_schedule_file, share, priority=1)
	
	# === Start ===
	
	# While UI is running, enter an event loop to handle messages that request spinning out a new sub-process
	while(True):
		try:
			message = pipes.recv(share, 'QueueToManager', timeout=1)
			
			# Handle Queue messages
			if(message is not None):
				print('Manager message: ' + str(message))
				
				# Spin out a new dispatcher sub-process
				if(message.get('type') == 'Dispatch'):
					if(dispatcher is None):
						scheduleFilePath = message['scheduleFilePath']
						dispatcher = startDispatcher(scheduleFilePath, share, priority=1)
					else:
						print('Error: dispatcher is already running; wait for it to finish before starting another job.')
			
			# If the dispatcher is not running, then check and clear its messages
			if(dispatcher is None):
				while pipes.poll(share, 'QueueToDispatcher'):
					dispMessage = pipes.recv(share, 'QueueToDispatcher')
					print('Dispatcher not running, but received message: ' + str(dispMessage))
		
		except Exception as e:
			print('Manager loop exception: ', e)
		
		# Check if dispatcher is running, if not join it to explicitly end
		if((dispatcher is not None) and (not dispatcher['process'].is_alive())):
			dispatcher['process'].join()
			dispatcher = None
		
		# If dispatcher is not running and UI is dead, exit the event loop
		if((dispatcher is None) and (not ui['process'].is_alive())):
			break
	
	# === Complete ===
	
	# Join to all of the child processes to clean them up
	ui['process'].terminate()
	ui['process'].join()
	if(dispatcher is not None):
		dispatcher['process'].join()

	
		
if __name__ == '__main__':
	if len(sys.argv) > 1:
		manage(sys.argv[1])
	else:
		manage()
