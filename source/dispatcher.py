"""This module is used to 'dispatch' or execute a particular schedule file. When the schedule file completes, the dispatcher is finished.
This module can be run from command line with an optional argument specifying the path to a schedule file. Alternatively, this module can
be run as a multiprocessing.Process and given a multiprocessing.Pipe for communication to other processes."""

# === Imports ===
import os
import sys
import platform
import time
import requests
import json
import time

# While it is tempting to import launcher here, this causes a large chain of imports that makes it impossible to avoid importing matplotlib. Also, there is no drawback to importing locally in these functions.
#import launcher
from utilities import DataLoggerUtility as dlu

if(__name__ == '__main__'):
	pathParents = os.getcwd().split('/')
	if 'AutexysHost' in pathParents:
		os.chdir(os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source'))



# === Main entry point for dispatching a schedule file ===
def dispatch(schedule_file_path=None, pipe=None):
	"""Given a schedule file path, begin executing the experiments in the schedule file, otherwise prompt the user for a schedule file."""
	
	if(schedule_file_path is not None):
		choice = schedule_file_path
	else:
		choice = input('Choose a schedule file to run: ')
	
	# File must end in '.json'
	file = choice if(choice[-5:] == '.json') else (choice + '.json')
	file = file.strip()
	
	run_file(file, pipe)
	
	send_notification_via_pushbullet(
		'Completed Main at {}'.format(time.strftime('%I:%M %p on %a')), 
		'Script has finished choice of: {}'.format(choice)
	)



def run_file(schedule_file_path, pipe=None):
	"""Given a shedule file path, open the file and step through each experiment."""
	import launcher

	schedule_index = 0

	print('Opening schedule file: ' + schedule_file_path)

	while( schedule_index < len(dlu.loadJSON(directory='', loadFileName=schedule_file_path)) ):
		if(pipe is not None):
			while(pipe.poll()):
				message = pipe.recv()
				if(message == 'STOP'):
					print('Aborting schedule file: ' + schedule_file_path)
					return
		print('Loading line #' + str(schedule_index+1) + ' in schedule file ' + schedule_file_path)
		parameter_list = dlu.loadJSON(directory='', loadFileName=schedule_file_path)

		print('Launching job #' + str(schedule_index+1) + ' of ' + str(len(parameter_list)) + ' in schedule file ' + schedule_file_path)
		print('Schedule contains ' + str(len(parameter_list) - schedule_index - 1) + ' other incomplete jobs.')
		additional_parameters = parameter_list[schedule_index].copy()
		launcher.run(additional_parameters, pipe)

		schedule_index += 1
	
	print('Closing schedule file: ' + schedule_file_path)
		
		

def send_notification_via_pushbullet(title, body):
	url = 'https://api.pushbullet.com/v2/pushes'
	access_token = 'o.jc84248QDFZCW8QJWu9DXpzaLbdwhoD7'
	data_send = {"type": "note", "title": title, "body": body}
	headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
 	
	resp = requests.post(url, data=json.dumps(data_send), headers=headers)
	
	if resp.status_code != 200:
		print('Pushbullet Notification Failed')
	else:
		print('Pushbullet Notification Succeeded')



# === User Interface ===
def devicesInRange(startContact, endContact, skip=True):
	"""Deprecated function for generating a list of devices."""
	contactList = set(range(startContact,endContact))
	if(skip):
		omitList = set(range(4,64+1,4))
		contactList = list(contactList-omitList)
	return ['{0:}-{1:}'.format(c, c+1) for c in contactList]





if(__name__ == '__main__'):
	if((len(sys.argv) > 1)):
		dispatch(schedule_file_path=sys.argv[1])
	else:
		dispatch()
