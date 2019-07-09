
def send(pipe, message):
	if pipe is None:
		return
	try:
		pipe.send(message)
	except Exception as e:
		print('Pipe could not send message')
		# print(e)

def send(queue, message):
	if queue is None:
		return
	try:
		if not queue.full():
			queue.put_nowait(message)
		else:
			print('Queue is full')
	except Exception as e:
		print('Queue could not put message')

def poll(pipe, timeout=0):
	if pipe is None:
		return False
	try:
		result = pipe.poll(timeout)
	except Exception as e:
		print('Pipe could not poll')
		result = False
	return result

def poll(queue, timeout=0):
	if queue is None:
		return False
	try:
		result = not queue.empty()
	except Exception as e:
		print('Pipe could not poll')
		result = False
	return result

def recv(pipe):
	if pipe is None:
		return ''
	try:
		result = pipe.recv()
	except Exception as e:
		print('Pipe could not receive')
		result = ''
	return result

def recv(queue, timeout=0):
	if queue is None:
		return None
	if queue.empty():
		return None
	try:
		if timeout > 0:
			result = queue.get(block=True, timeout=timeout)
		else:
			result = queue.get_nowait()
	except Exception as e:
		print('Queue could not get')
		print(e)
		result = None
	return result

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
	
