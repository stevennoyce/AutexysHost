import multiprocessing as mp
import psutil
import sys
import os

import main
import ui

# Main could be called 'scheduler', 'dispatcher', etc.

if __name__ == '__main__':
	os.chdir(sys.path[0])
	
	pathParents = os.getcwd().split('/')
	if 'AutexysHost' in pathParents:
		os.chdir(os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source'))


# Detect whether running on Windows or Posix
def onPosix():
	try:
		import posix
		return True
	except ImportError:
		return False

def getProcessPriorityCodes():
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
	# Priority ranges from -2 to 3
	return getProcessPriorityCodes()[priority]

def changePriorityOfProcessAndChildren(pid, priority):
	# Must be called after starting the process
	# Priority ranges from -2 to 3
	priorityCode = getPriorityCode(priority)
	
	parent = psutil.Process(pid)
	parent.nice(priorityCode)
	for child in parent.children():
		child.nice(priorityCode)

def startUI(priority=0):
	pipeToUI, pipeForUI = mp.Pipe()
	uiProcess = mp.Process(target=ui.start, kwargs={'managerPipe':pipeForUI})
	uiProcess.start()
	changePriorityOfProcessAndChildren(uiProcess.pid, priority)
	return (uiProcess, pipeToUI)

def startDispatcher(schedule_file_path, priority=0):
	pipeToDispatcher, pipeForDispatcher = mp.Pipe()
	dispatcherProcess = mp.Process(target=main.main, args=(schedule_file_path, pipeForDispatcher))
	dispatcherProcess.start()
	changePriorityOfProcessAndChildren(dispatcherProcess.pid, priority)
	return (dispatcherProcess, pipeToDispatcher)

def manage():
	#pipeManagerToUI, pipeUIToManager = mp.Pipe()
	#pipeManagerToMain, pipeMainToManager = mp.Pipe()
	#pipeUIToMain, pipeMainToUI = mp.Pipe()
	
	uiProcess, pipeToUI = startUI(priority=0)	
	dispatcher = None
	
	while(True):
		# Listen to the UI pipe for 10 seconds, then yield to do other tasks
		print('Hello from Manager')
		if(pipeToUI.poll(10)):
			message = pipeToUI.recv()
			print('Manager received: "' + str(message) + '"')
						
			if(message.startswith('RUN: ')):
				if(dispatcher is None):
					schedule_file_path = message[len('RUN: '):]
					dispatcherProcess, pipeToDispatcher = startDispatcher(schedule_file_path, priority=0)
					dispatcher = {'process':dispatcherProcess, 'pipe':pipeToDispatcher}
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
		if(not uiProcess.is_alive()):
			break
	
	# Join to all of the child processes to clean them up
	uiProcess.join()
	if(dispatcher is not None):
		dispatcher['process'].join()

	
		
if __name__ == '__main__':
	manage()
