import time

# === Basic Queue Communication ===
def send(share, qName, message):
	if share is None: # Prevent null exceptions
		return
	try:
		if qName not in share:
			return
		q = share[qName]
		
		# Send "message" to "qName" Queue
		if(not q.full()):
			q.put_nowait(message)
		else:
			print('Queue is full')
	
	except Exception as e:
		print(f"Queue put exception: {e}")

def poll(share, qName):
	if share is None: # Prevent null exceptions
		return False
	try:
		if qName not in share:
			return False
		q = share[qName]
		
		# Poll "qName" Queue
		if(q.empty()):
			return False
		else:
			return True
	
	except Exception as e:
		print(f"Queue poll exception: {e}")
		return False

def recv(share, qName, timeout=0):
	if share is None: # Prevent null exceptions
		return
	try:
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
	
	except Exception as e:
		if(timeout > 0):
			print(f"Queue get exception: {e}")
		return None

def clear(share, qName):
	if share is None: # Prevent null exceptions
		return
	try:
		if qName not in share:
			return
		q = share[qName]
		
		# Clear "qName" Queue
		while(not q.empty()):
			q.get()
	
	except Exception as e:
		print(f"Queue clearing exception: {e}")



# === Progress Updates ===
class AbortError(Exception):
	"""Error type for a progress update that needs to trigger the abort sequence."""
	pass

def progressUpdate(share, progressName, start, current, end, barType='Procedure', enableAbort=False, extraInfo=''):
	try:
		# Prevent null exceptions
		if(share is None):
			return

		# Send a progress-type message to the UI
		send(share, 'QueueToUI', {
				'type':'Progress',
				'progress': {
					'name': progressName,
					'barType': barType,
					'start': start,
					'current': current,
					'end': end,
					'timestamp':time.time()
				},
				'info': extraInfo,
			}
		)		
	# Handle generic exceptions	
	except Exception as e:
		print('Progress update exception: ', e)
	
	if(enableAbort):
	 	checkAbortStatus(share)

def checkAbortStatus(share):
	if(abortStatus(share)):
		raise AbortError('Aborting current procedure.')

def abortStatus(share):
	return poll(share, 'QueueToDispatcher')



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
		
		
		
		