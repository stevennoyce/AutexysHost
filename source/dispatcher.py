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
import logging

import pipes
import launcher
from utilities import DataLoggerUtility as dlu

if(__name__ == '__main__'):
	pathParents = os.getcwd().split('/')
	if 'AutexysHost' in pathParents:
		os.chdir(os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source'))



# === Main entry point for dispatching a schedule file ===
def dispatch(input_command, workspace_data_path=None, connection_status=None, share=None):
	"""Given an input command that is a valid schedule file path, begin executing the experiments in the schedule file, otherwise treat the input as a runType and attempt to launch it directly."""
	
	setup_logging(log_directory=workspace_data_path)
	
	try:
		# Check if the input is a file
		isFile = input_command[-5:] == '.json'
		
		if(isFile):
			print('Dispatcher received a schedule file input.')
			schedule_file_path = input_command
			schedule_file_path = schedule_file_path.strip()
		
			run_file(schedule_file_path, workspace_data_path, connection_status, share)
		else:
			print('Dispatcher received a runType input.')
			runType = input_command
			additional_parameters = {'runType':runType}
			launcher.run(additional_parameters, workspace_data_path, connection_status, share)
	except Exception as e:
		logging.exception('Error: ' + str(e))
		raise
		
	
	send_notification_via_pushbullet(
		'Completed Main at {}'.format(time.strftime('%I:%M %p on %a')), 
		'Script has finished choice of: {}'.format(input_command)
	)



def run_file(schedule_file_path, workspace_data_path=None, connection_status=None, share=None):
	"""Given a shedule file path, open the file and step through each experiment."""
	schedule_index = 0
	
	print('Opening schedule file: ' + str(schedule_file_path))
	
	while( schedule_index < len(dlu.loadJSON(directory='', loadFileName=schedule_file_path)) ):
		# Re-load the entire schedule file
		print('Loading line #' + str(schedule_index+1) + ' in schedule file ' + schedule_file_path)
		parameter_list = dlu.loadJSON(directory='', loadFileName=schedule_file_path)

		# Print launch message for the current line of the schedule file
		print('Launching job #' + str(schedule_index+1) + ' of ' + str(len(parameter_list)) + ' in schedule file ' + schedule_file_path)
		additional_parameters = parameter_list[schedule_index].copy()

		# Notify the UI that a new job is about to start
		pipes.jobNumberUpdate(share, schedule_index)

		# Update dispatcher progress bar
		pipes.progressUpdate(share, 'Job', start=0, current=schedule_index, end=len(parameter_list), barType='Dispatcher', extraInfo=additional_parameters['Identifiers'] if('Identifiers' in additional_parameters) else '')
		
		launcher.run(additional_parameters, workspace_data_path, connection_status, share)
		schedule_index += 1
		
		# Update dispatcher progress bar
		pipes.progressUpdate(share, 'Job', start=0, current=schedule_index, end=len(parameter_list), barType='Dispatcher', extraInfo=additional_parameters['Identifiers'] if('Identifiers' in additional_parameters) else '')
	
	print('Closing schedule file: ' + str(schedule_file_path))
	


def setup_logging(log_directory, log_file='system.log'):
	log_file_path = os.path.join(log_directory, log_file) if((log_directory is not None) and (log_file is not None)) else None
	logging.basicConfig(filename=log_file_path, format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s')
		


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
		dispatch(input_command=sys.argv[1])
	else:
		print('Dispatcher was unable to run without a valid command-line input.')
	
	
	
