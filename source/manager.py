import multiprocessing as mp
import psutil

import main
import ui

# Main could be called 'scheduler', 'dispatcher', etc.

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
	uiProcess = mp.Process(target=ui.start, args=())
	uiProcess.start()
	changePriorityOfProcessAndChildren(uiProcess.pid, priority)
	return (uiProcess, pipeToUI)

def startDispatcher(schedule_file_path, priority=0):
	pipeToDispatcher, pipeForDispatcher = mp.Pipe()
	dispatcherProcess = mp.Process(target=main.main, args=(schedule_file_path, pipeForDispatcher))
	dispatcherProcess.start()
	changePriorityOfProcessAndChildren(dispatcherProcess.pid, priority)
	return (dispatcherProcess, pipeToDispatcher)

def main():
	#pipeManagerToUI, pipeUIToManager = mp.Pipe()
	#pipeManagerToMain, pipeMainToManager = mp.Pipe()
	#pipeUIToMain, pipeMainToUI = mp.Pipe()
	
	uiProcess, pipeToUI = startUI(priority=0)
	dispatchers = []
	
	while(True):
		# Listen to the UI pipe for 10 seconds, then yield to do other tasks
		if(pipeToUI.poll(10)):
			message = pipeToUI.recv()
			
			if(message.startswith('RUN:')):
				schedule_file_path = message[len('RUN:'):]
				dispatcherProcess, pipeToDispatcher = startDispatcher(schedule_file_path, priority=0)
				dispatchers.append({'process':dispatcherProcess, 'pipe':pipeToDispatcher})
			elif(message == 'STOP'):
				for dispatcher in dispatchers:
					dispatcher['pipe'].send('STOP')
		
		# Check if dispatchers are running, if not join them to explicitly end them
		for dispatcher in dispatchers:
			if(not dispatcher['process'].is_alive()):
				dispatcher['process'].join()
		
		# Check that UI is still running, if not exit the event loop
		if(not uiProcess.is_alive()):
			break
	
	# Join to all of the child processes to clean them up
	uiProcess.join()
	for dispatcher in dispatchers:
		dispatcher['process'].join()
		
	
		
if __name__ == '__main__':
	main()
	
