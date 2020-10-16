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



# === Nathaniel's Custhom Dispatchers ===
def dispatch_continuously(schedule_file_path, totalTime=10800, delayTime=300, pipe=None):
	startTime = time.time()
	while(time.time() < startTime + totalTime):
		dispatchTime = time.time()
		dispatch(schedule_file_path=schedule_file_path)
		dispatchTime = time.time() - dispatchTime
		print("Delaying " + str(delayTime - dispatchTime) + " seconds")
		time.sleep(delayTime - dispatchTime)

def dispatch_cycler(schedule_file_path, pipe=None):
	allDevices = ["1-2", "2-3", "3-4", "4-5", "5-6", "6-7", "7-8", "8-9", "9-10", "10-11", "11-12", "12-13", "14-15", "15-16", "16-17", "17-18", "18-19", "19-20", "21-22", "22-23", "23-24", "24-25", "25-26", "26-27", "27-28", "28-29", "29-30", "30-31", "31-32", "33-34", "34-35", "35-36", "36-37", "37-38", "38-39", "40-41", "41-42", "42-43", "43-44", "45-46", "46-47", "47-48", "48-49", "49-50", "50-51", "52-53", "53-54", "54-55", "55-56", "57-58", "58-59", "59-60", "60-61", "61-62", "62-63"]
	startDevice = "62-63"
	
	currentDevice = startDevice
	for device in allDevices:
		input('\n\nChange to device ' + str(device))
		# Edit schedule file and save new version in temp location
		with open(schedule_file_path) as in_file:
			with open('temp.txt', 'w') as out_file:
				out_file.write(in_file.read().replace(currentDevice, device))
		# Overwrite schedule file		
		with open(schedule_file_path, 'w') as out_file:
			with open('temp.txt') as in_file:
				out_file.write(in_file.read())
		currentDevice = device
		dispatch(schedule_file_path=schedule_file_path)
		


if(__name__ == '__main__'):
	if((len(sys.argv) > 1)):
		dispatch(input_command=sys.argv[1])
	else:
		print('Dispatcher was unable to run without a valid command-line input.')
	
	
	
