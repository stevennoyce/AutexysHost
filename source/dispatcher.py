"""This module is used to 'dispatch' or execute a particular schedule file. When the schedule file completes, the dispatcher is finished.
This module can be run from command line with an optional argument specifying the path to a schedule file. Alternatively, this module can
be run as a multiprocessing.Process and given a multiprocessing.Pipe for communication to other processes."""

import json
import logging
import os
import sys
import time

import launcher
import pipes
from utilities import DataLoggerUtility as dlu



# === Main entry point for dispatching a schedule file ===
def dispatch(input_command, workspace_data_path=None, connection_status=None, share=None):
	"""Given an input command that is a valid schedule file path, begin executing the experiments in the schedule file, otherwise treat the input as a runType and attempt to launch it directly."""
	
	setup_logging(log_directory=workspace_data_path)
	
	try:
		is_file = str(input_command).strip().endswith('.json')
		
		if(is_file):
			print(f"[D] Dispatcher starting a schedule file.")
			schedule_file_path = str(input_command).strip()
			run_file(schedule_file_path, workspace_data_path, connection_status, share)
		else:
			print(f"[D] Dispatcher starting a specific runType. ({input_command})")
			additional_parameters = {'runType':input_command}
			launcher.run(additional_parameters, workspace_data_path, connection_status, share)
	except Exception as e:
		logging.exception(f'[D] Error: {e}')
		raise

def run_file(schedule_file_path, workspace_data_path=None, connection_status=None, share=None):
	"""Given a shedule file path, open the file and step through each experiment."""
	schedule_index = 0
	
	print(f"[D] Opening schedule file: {schedule_file_path}")
	
	# While loop specifically chosen to allow the schedule file to grow/shrink during runtime
	while( schedule_index < len(dlu.loadJSON(directory='', loadFileName=schedule_file_path)) ):
		# Re-load the entire schedule file
		print(f"[D] Loading line #{schedule_index+1} in schedule file {schedule_file_path}")
		parameter_list = dlu.loadJSON(directory='', loadFileName=schedule_file_path)

		print(f"[D] Launching job #{schedule_index+1} of {len(parameter_list)} in schedule file {schedule_file_path}")
		additional_parameters = parameter_list[schedule_index].copy()

		pipes.jobNumberUpdate(share, schedule_index)
		pipes.progressUpdate(share, 'Job', start=0, current=schedule_index, end=len(parameter_list), barType='Dispatcher')
		pipes.send(share, 'QueueToUI', {'type':'DispatcherIdentifiers', 'identifiers':additional_parameters.get('Identifiers','')})
		
		launcher.run(additional_parameters, workspace_data_path, connection_status, share)
		
		schedule_index += 1
		pipes.progressUpdate(share, 'Job', start=0, current=schedule_index, end=len(parameter_list), barType='Dispatcher')
	
	print(f"Closing schedule file: {schedule_file_path}")

def setup_logging(log_directory, log_file='system.log'):
	log_file_path = os.path.join(log_directory, log_file) if((log_directory is not None) and (log_file is not None)) else None
	logging.basicConfig(filename=log_file_path, format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s')



if(__name__ == '__main__'):
	if((len(sys.argv) == 0)):
		print('Dispatcher was unable to run without a valid command-line input.')
		sys.exit()
	dispatch(input_command=sys.argv[1])


