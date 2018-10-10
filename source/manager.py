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

if __name__ == '__main__':
	# parent_conn, child_conn = mp.Pipe()
	# p = mp.Process(target=f, args=(child_conn,))
	# p.start()
	
	pipeManagerToUI, pipeUIToManager = mp.Pipe()
	pipeManagerToMain, pipeMainToManager = mp.Pipe()
	pipeUIToMain, pipeMainToUI = mp.Pipe()
	
	uiProcess = mp.Process(target=ui.start, args=())
	uiProcess.start()
	
	changePriorityOfProcessAndChildren(uiProcess.pid, 0)
	
	dispatcherProcess = mp.Process(target=main.main, args=())
	dispatcherProcess.start()
	
	changePriorityOfProcessAndChildren(dispatcherProcess.pid, 0)
	
	print(parent_conn.recv())
	dispatcherProcess.join()
	
