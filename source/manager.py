"""This module manages the connection between the UI and dispatchers. On startup, this starts the UI and can also immediately give a dispatcher
a schedule file to run, or the UI can be used to navigate schedule files and choose one to run. At any given time, this module can manage 1 UI 
process and 1 dispatcher process."""

import multiprocessing as mp
import psutil
import sys
import os

import dispatcher
import ui

if __name__ == '__main__':
	os.chdir(sys.path[0])
	
	pathParents = os.getcwd().split('/')
	if 'AutexysHost' in pathParents:
		os.chdir(os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source'))


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

def startUI(priority=0):
	"""Start a Process running ui.start() and obtain a two-way Pipe for communication."""
	pipeToUI, pipeForUI = mp.Pipe()
	uiProcess = mp.Process(target=ui.start, kwargs={'managerPipe':pipeForUI})
	uiProcess.start()
	changePriorityOfProcessAndChildren(uiProcess.pid, priority)
	return {'process':uiProcess, 'pipe':pipeToUI}

def startDispatcher(schedule_file_path, priority=0):
	"""Start a Process running dispatcher.dispatch(schedule_file_path) and obtain a two-way Pipe for communication."""
	pipeToDispatcher, pipeForDispatcher = mp.Pipe()
	dispatcherProcess = mp.Process(target=dispatcher.dispatch, args=(schedule_file_path, pipeForDispatcher))
	dispatcherProcess.start()
	changePriorityOfProcessAndChildren(dispatcherProcess.pid, priority)
	return {'process':dispatcherProcess, 'pipe':pipeToDispatcher}

def manage(on_startup_schedule_file=None):
	"""Initialize a UI process and enter an event loop to handle communication with that UI. Manage the creation of dispatcher
	processes to execute schedule files and facilitate communication between the UI and the currently running dispatcher."""
	
	ui = startUI(priority=0)	
	dispatcher = None
	
	if(on_startup_schedule_file is not None):
		dispatcher = startDispatcher(on_startup_schedule_file, priority=0)
	
	while(True):
		# Listen to the UI pipe for 10 seconds, then yield to do other tasks
		print('Hello from Manager')
		if(ui['pipe'].poll(10)):
			message = ui['pipe'].recv()
			print('Manager received: "' + str(message) + '"')
						
			if(message.startswith('RUN: ')):
				if(dispatcher is None):
					schedule_file_path = message[len('RUN: '):]
					dispatcher = startDispatcher(schedule_file_path, priority=0)
				else:
					print('Error: dispatcher is already running; wait for it to finish before starting another job.')
			elif(message == 'STOP'):
				if(dispatcher is not None):
					dispatcher['pipe'].send('STOP')
				else:
					print('Dispatcher has already stopped.')
		
		# Check if dispatcher is running, if not join it to explicitly end
		if((dispatcher is not None) and (not dispatcher['process'].is_alive())):
			dispatcher['process'].join()
			dispatcher = None
		
		# Check that UI is still running, if not exit the event loop
		if(not ui['process'].is_alive()):
			break
	
	# Join to all of the child processes to clean them up
	ui['process'].join()
	if(dispatcher is not None):
		dispatcher['process'].join()

	
		
if __name__ == '__main__':
	if(len(sys.argv) > 1):
		manage(sys.argv[1])
	else:
		manage()
