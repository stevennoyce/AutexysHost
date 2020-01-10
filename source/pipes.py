# === Imports ===
import time
import queue



# === Basic Queue Communication ===
def send(share, qName, message):
	try:
		# Prevent null exceptions
		if share is None:
			return 
		if qName not in share:
			return
		q = share[qName]
		
		# Send "message" to "qName" Queue
		if(not q.full()):
			q.put_nowait(message)
		else:
			print('Queue is full')
	
	# Handle generic exceptions	
	except Exception as e:
		print('Queue put exception: ', e)

def poll(share, qName):
	try:
		# Prevent null exceptions
		if qName not in share:
			return False
		q = share[qName]
		
		# Poll "qName" Queue
		if(q.empty()):
			return False
		else:
			return True
	
	# Handle generic exceptions	
	except Exception as e:
		print('Queue poll exception: ', e)
		return False

def recv(share, qName, timeout=0):
	try:
		# Prevent null exceptions
		if qName not in share:
			return
		q = share[qName]
		
		# Recv message from "qName" Queue
		if(timeout > 0):
			return q.get(block=True, timeout=timeout)
		else:
			if(q.empty()):
				return None
			return q.get_nowait()
	
	# Handle empty Queue			
	except queue.Empty as e:
		return None
	
	# Handle generic exceptions	
	except Exception as e:
		print('Queue get exception: ', e)

def clear(share, qName):
	try:
		# Prevent null exceptions
		if qName not in share:
			return
		q = share[qName]
		
		# Clear "qName" Queue
		while(not q.empty()):
			q.get()
	
	# Handle generic exceptions	
	except Exception as e:
		print('Queue clearing exception: ', e)



# === Progress Updates ===
class AbortError(Exception):
	"""Error type for a progress update that needs to trigger the abort sequence."""
	pass

def progressUpdate(share, progName, start, current, end, barType='Procedure', enableAbort=False):
	try:
		# Prevent null exceptions
		if(share is None):
			return

		# Send a progress-type message to the UI
		send(share, 'QueueToUI', {
				'type':'Progress',
				'progress': {
					'name': progName,
					'barType': barType,
					'start': start,
					'current': current,
					'end': end,
					'timestamp':time.time()
				}
			}
		)
		
		# Check for abort signals
		abort = (enableAbort and poll(share, 'QueueToDispatcher'))
				
	# Handle generic exceptions	
	except Exception as e:
		print('Progress update exception: ', e)
	
	if(abort):
	 	raise AbortError('Aborting current procedure at {}.'.format(progName))



# === Live-Plot Updates ===
def livePlotUpdate(share, plots):
	try:
		# Prevent null exceptions
		if(share is None):
			return
		
		# Send a data-type message to the UI
		send(share, 'QueueToUI', {
				'type':'Data',
				'plots': [plot.toDict() for plot in plots]
			}
		)

	# Handle generic exceptions	
	except Exception as e:
		print('Live-plot update exception: ', e)

def jobNumberUpdate(share, number):
	try:
		# Prevent null exceptions
		if(share is None):
			return
			
		# Send a jobnumber-type message to the UI
		send(share, 'QueueToUI', {
				'type':'JobNumberUpdate',
				'number':number
			}
		)

	# Handle generic exceptions	
	except Exception as e:
		print('Job-number update exception: ', e)

def deviceNumberUpdate(share, number):
	try:
		# Prevent null exceptions
		if(share is None):
			return

		# Send a devicenumber-type message to the UI
		send(share, 'QueueToUI', {
				'type':'DeviceNumberUpdate',
				'number':number
			}
		)

	# Handle generic exceptions	
	except Exception as e:
		print('Device-number update exception: ', e)
		
		
		
		