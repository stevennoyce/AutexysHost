
import queue

def pipeSend(pipe, message):
	if pipe is None:
		return
	try:
		pipe.send(message)
	except Exception as e:
		print('Pipe could not send message')
		# print(e)

def send(share, qName, message):
	try:
		if qName not in share:
			return
		q = share[qName]
		
		if not q.full():
			q.put_nowait(message)
		else:
			print('Queue is full')
	except Exception as e:
		print('Queue could not put message', e)

def pipePoll(pipe, timeout=0):
	if pipe is None:
		return False
	try:
		result = pipe.poll(timeout)
	except Exception as e:
		print('Pipe could not poll: ', e)
		result = False
	return result

def poll(share, qName, timeout=0):
	try:
		if qName not in share:
			return
		q = share[qName]
		
		if q.empty():
			return False
		else:
			return True
	except Exception as e:
		print('Pipe could not poll: ', e)
		return False

def pipeRecv(pipe):
	if pipe is None:
		return ''
	try:
		result = pipe.recv()
	except Exception as e:
		print('Pipe could not receive: ', e)
		result = ''
	return result

def recv(share, qName, timeout=0):
	try:
		if qName not in share:
			return
		q = share[qName]
		
		if timeout > 0:
			return q.get(block=True, timeout=timeout)
		else:
			if q.empty():
				return None
			return q.get_nowait()
	except queue.Empty as e:
		return None
	except Exception as e:
		print('Queue get exception: ', e)
	return None

def clear(share, qName):
	try:
		if qName not in share:
			return
		q = share[qName]
		
		while not q.empty():
			q.get()
	except Exception as e:
		print('Error clearing queue ', e)

def progressUpdate(share, progName, start, current, end):
	try:
		abort = False
		qName = 'QueueToUI'
		
		if share is None:
			return
		q = share.get(qName)
		
		if q is None:
			return
		
		if progName in share['procedureStopLocations']:
			abort = True
		
		send(q, {
			'type':'Progress',
			'progress': {
				progName: {
					'start': start,
					'current': current,
					'end': end
				}
			}
		})
	except Exception as e:
		print('Error updating progress: ', e)
	
	if abort:
	 	raise Exception('Recieved stop command from UI. Aborting current procedure at {}.'.format(progName))

	
