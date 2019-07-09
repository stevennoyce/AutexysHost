
import queue

def send(pipe, message):
	if pipe is None:
		return
	try:
		pipe.send(message)
	except Exception as e:
		print('Pipe could not send message')
		# print(e)

def send(q, message):
	if q is None:
		return
	try:
		if not q.full():
			q.put_nowait(message)
		else:
			print('Queue is full')
	except Exception as e:
		print('Queue could not put message')
		print(e)

def poll(pipe, timeout=0):
	if pipe is None:
		return False
	try:
		result = pipe.poll(timeout)
	except Exception as e:
		print('Pipe could not poll')
		result = False
	return result

def poll(q, timeout=0):
	if q is None:
		return False
	try:
		if q.empty():
			return False
		else:
			return True
	except Exception as e:
		print('Pipe could not poll')
		return False

def recv(pipe):
	if pipe is None:
		return ''
	try:
		result = pipe.recv()
	except Exception as e:
		print('Pipe could not receive')
		result = ''
	return result

def recv(q, timeout=0):
	if q is None:
		return None
	try:
		if timeout > 0:
			return q.get(block=True, timeout=timeout)
		else:
			if q.empty():
				return None
			return q.get_nowait()
	except queue.Empty as e:
		return None
	except Exception as e:
		print('Queue could not get')
		print(e)
	return None

# def progressUpdate(share, name, start, current, end):
# 	if((share is None) or (share['p'] is None)):
# 		return
# 	pipe = share['p']
	
# 	if name in share['procedureStopLocations']:
# 	 	raise Exception('Recieved stop command from UI. Aborting current procedure at {}.'.format(name))
	
# 	send(pipe, {
# 		'destination':'UI',
# 		'type':'Progress',
# 		'progress': {
# 			name: {
# 				'start': start,
# 				'current': current,
# 				'end': end
# 			}
# 		}
# 	})

def progressUpdate(share, name, start, current, end):
	if((share is None) or (share['p'] is None)):
		return
	q = share['QueueToUI']
	
	if name in share['procedureStopLocations']:
	 	raise Exception('Recieved stop command from UI. Aborting current procedure at {}.'.format(name))
	
	send(pipe, {
		'type':'Progress',
		'progress': {
			name: {
				'start': start,
				'current': current,
				'end': end
			}
		}
	})

def clearProgress(share):
	if((share is None) or (share['p'] is None)):
		return
	pipe = share['QueueToUI']
		
	send(pipe, {
		'type':'Clear Progress'
	})
	
