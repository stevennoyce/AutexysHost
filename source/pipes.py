
def send(pipe, message):
	if pipe is None:
		return
	try:
		pipe.send(message)
	except Exception as e:
		print('Pipe could not send message')
		# print(e)

def poll(pipe, timeout=0):
	if pipe is None:
		return False
	try:
		result = pipe.poll(timeout)
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
		print('Pipe could not poll')
		result = ''
	return result

def progressUpdate(share, name, start, current, end):
	if((share is None) or (share['p'] is None)):
		return
	pipe = share['p']
		
	#if poll(pipe):
	#	message = recv(pipe)
	#	if 'type' in message and message['type'] == 'Stop':
	#		if 'stop' in message:
	#			if name in message['stop']:
	#				raise Exception('Recieved stop message from UI. Aborting current procedure.')
	
	if name in share['procedureStopLocations']:
	 	raise Exception('Recieved stop command from UI. Aborting current procedure at {}.'.format(name))
	
	send(pipe, {
		'destination':'UI',
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
	pipe = share['p']
		
	send(pipe, {
		'destination':'UI',
		'type':'Clear Progress',
	})
	
