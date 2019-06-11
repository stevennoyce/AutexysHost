"""This module manages the connection between the UI and dispatchers. On startup, this starts the UI and can also immediately give a dispatcher
a schedule file to run, or the UI can be used to navigate schedule files and choose one to run. At any given time, this module can manage 1 UI 
process and 1 dispatcher process."""

import multiprocessing as mp
import psutil
import sys
import os

import pipes

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

def startUI(share, priority=0):
	"""Start a Process running ui.start() and obtain a two-way Pipe for communication."""
	pipeToUI, pipeForUI = mp.Pipe()
	share['p'] = pipeForUI
	uiProcess = mp.Process(target=runUI, args=(share,))
	uiProcess.start()
	# changePriorityOfProcessAndChildren(uiProcess.pid, priority)
	return {'process':uiProcess, 'pipe':pipeToUI}

def runUI(share):
	"""A target method for running the UI that also imports the UI so the parent process does not have that dependency."""
	import ui
	ui.start(share=share, use_reloader=False)

def startDispatcher(schedule_file_path, share, priority=0):
	"""Start a Process running dispatcher.dispatch(schedule_file_path) and obtain a two-way Pipe for communication."""
	pipeToDispatcher, pipeForDispatcher = mp.Pipe()
	share['p'] = pipeForDispatcher
	dispatcherProcess = mp.Process(target=runDispatcher, args=(schedule_file_path, share))
	dispatcherProcess.start()
	# changePriorityOfProcessAndChildren(dispatcherProcess.pid, priority)
	return {'process':dispatcherProcess, 'pipe':pipeToDispatcher}

def runDispatcher(schedule_file_path, share):
	"""A target method for running the dispatcher that also imports the dispatcher so the parent process does not have that dependency."""
	import dispatcher
	dispatcher.dispatch(schedule_file_path, share)

def manage(on_startup_schedule_file=None):
	"""Initialize a UI process and enter an event loop to handle communication with that UI. Manage the creation of dispatcher
	processes to execute schedule files and facilitate communication between the UI and the currently running dispatcher."""
	
	sharedMemoryManager = mp.Manager()
	sharedDict = sharedMemoryManager.dict({'dispatcherRunning':False})
	sharedList = sharedMemoryManager.list([])
	
	share = {
		'd': sharedDict,
		'l': sharedList
	}
	
	ui = startUI(share, priority=0)	
	dispatcher = None
	
	if(on_startup_schedule_file is not None):
		dispatcher = startDispatcher(on_startup_schedule_file, share, priority=1)
	
	while(True):
		pipesList = [e['pipe'] for e in [ui, dispatcher] if e is not None]
		mp.connection.wait(pipesList, timeout=0.1)
		
		try:
			if(pipes.poll(ui['pipe'])):
				message = ui['pipe'].recv()
				print('Manager received from UI: "' + str(message) + '"')
				
				if(message.startswith('RUN: ')):
					if(dispatcher is None):
						schedule_file_path = message[len('RUN: '):]
						dispatcher = startDispatcher(schedule_file_path, share, priority=1)
					else:
						print('Error: dispatcher is already running; wait for it to finish before starting another job.')
				elif(message == 'STOP'):
					if(dispatcher is not None):
						pipes.send(dispatcher['pipe'], 'STOP')
					else:
						print('Dispatcher has already stopped.')
		except Exception as e:
			print('Error managing UI')
		
		try:
			if dispatcher is None:
				pass
			else:
				if(pipes.poll(dispatcher['pipe'])):
					message = dispatcher['pipe'].recv()
					print('Manager received from Dispatcher: "' + str(message) + '"')
					
					if 'destination' in message:
						# Forward messages that are intended for the UI to the UI
						if message['destination'] == 'UI':
							print('Forwarding message from Dispatcher to UI')
							pipes.send(ui['pipe'], message)
		except Exception as e:
			print('Error managing Dispatcher')
		
		# Check if dispatcher is running, if not join it to explicitly end
		if((dispatcher is not None) and (not dispatcher['process'].is_alive())):
			dispatcher['process'].join()
			dispatcher = None
		
		# Check that UI is still running, if not exit the event loop
		if(not ui['process'].is_alive()):
			break
	
	# Join to all of the child processes to clean them up
	ui['process'].terminate()
	ui['process'].join()
	if(dispatcher is not None):
		dispatcher['process'].join()

	
		
if __name__ == '__main__':
	if(len(sys.argv) > 1):
		manage(sys.argv[1])
	else:
		manage()
