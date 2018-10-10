# === Imports ===
import os
import sys
import platform
import time
import requests
import json
import time

import launcher
from utilities import DataLoggerUtility as dlu

if(__name__ == '__main__'):
	pathParents = os.getcwd().split('/')
	if 'AutexysHost' in pathParents:
		os.chdir(os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source'))



# === Main ===
def listen(pipe):
	print('Dispatcher is ready to run jobs.')
	
	while(True):
		command = pipe.recv()
		print('Dispatcher recieved "' + str(command) + '"')
		
		if(command.startswith('RUN:')):
			schedule_file_path = command[len('RUN:'):]
			main(schedule_file_path)		
		elif(command == 'EXIT'):
			break
		
	print('Dispatcher is ending communication.')
		
	
	
def main(schedule_file_path=None):
	if((__name__ == '__main__') and (len(sys.argv) > 1)):
		choice = sys.argv[1]
	elif(schedule_file_path is not None):
		choice = schedule_file_path
	else:
		choice = input('Choose a schedule file to run: ')
	
	# File must end in '.json'
	file = choice if(choice[-5:] == '.json') else (choice + '.json')
	
	run_file(file)
	
	send_notification_via_pushbullet(
		'Completed Main at {}'.format(time.strftime('%I:%M %p on %a')), 
		'Script has finished choice of: {}'.format(choice)
	)



def run_file(schedule_file_path):
	schedule_index = 0

	print('Opening schedule file: ' + schedule_file_path)

	while( schedule_index < len(dlu.loadJSON(directory='', loadFileName=schedule_file_path)) ):
		
		print('Loading line #' + str(schedule_index+1) + ' in schedule file ' + schedule_file_path)
		parameter_list = dlu.loadJSON(directory='', loadFileName=schedule_file_path)

		print('Launching job #' + str(schedule_index+1) + ' of ' + str(len(parameter_list)) + ' in schedule file ' + schedule_file_path)
		print('Schedule contains ' + str(len(parameter_list) - schedule_index - 1) + ' other incomplete jobs.')
		additional_parameters = parameter_list[schedule_index].copy()
		launcher.run(additional_parameters)

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
# Print a nicely formatted dictionary.
def print_dict(dictionary, numtabs):
	keys = list(dictionary.keys())
	for i in range(len(keys)):
		if(isinstance(dictionary[keys[i]], dict)):
			print(" '" + str(keys[i])+ "': {")
			print_dict(dictionary[keys[i]], numtabs+1)
		else:
			print(numtabs*'\t'+'  ' + str(keys[i]) + ': ' + str(dictionary[keys[i]]))

def devicesInRange(startContact, endContact, skip=True):
	contactList = set(range(startContact,endContact))
	if(skip):
		omitList = set(range(4,64+1,4))
		contactList = list(contactList-omitList)
	return ['{0:}-{1:}'.format(c, c+1) for c in contactList]





if(__name__ == '__main__'):
	main()
