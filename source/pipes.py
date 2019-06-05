
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
