# === Imports ===
import io
import os
import sys
import glob
import flask
import json
import copy
import time
import numpy as np
import webbrowser
import flask_socketio
import socket
from collections import Mapping, Sequence

import defaults
import pipes

from procedures import Device_History as DH
DH.dpu.mplu.plt.switch_backend('agg')

from procedures import Chip_History as CH
CH.dpu.mplu.plt.switch_backend('agg')

from utilities import DataLoggerUtility as dlu

# === Make this script runnable ===
if __name__ == '__main__':
	os.chdir(sys.path[0])
	
	pathParents = os.getcwd().split('/')
	if 'AutexysHost' in pathParents:
		os.chdir(os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source'))

# === Constants ===
SOCKETIO_DEFAULT_IP_ADDRESS = '127.0.0.1'
UI_REFRESH_DELAY_SECONDS = 0.01

CONFIG_FILE_NAME = 'Config.json'
CONFIG_DOC_PREFIX = 'Config_Doc'
HELP_DOC_PREFIX = 'Doc'

CONFIG_DOC_SUFFIX = '.json'
HELP_DOC_SUFFIX = '.json'

# === Globals ===
share = None

# === Defaults ===
default_makePlot_parameters = {
	'minExperiment': None,
	'maxExperiment': None,
	'minRelativeIndex': 0,
	'maxRelativeIndex': float('inf'),
	'specificPlot': '',
	'plotSaveName': '',
	'dataFolder': None,
	'saveFolder': None,
	'saveFigures': False,
	'showFigures': True,
	'plot_mode_parameters': None
}
default_data_path = '../../AutexysData/'

# === Paths ===
workspace_data_path = default_data_path

index_html_directory_path = 'ui/' 		       if(not getattr(sys, 'frozen', False)) else (os.path.join(sys._MEIPASS, 'ui/'))
config_path               = 'config/'          if(not getattr(sys, 'frozen', False)) else (os.path.join(sys._MEIPASS, 'config/'))
documentation_path        = 'documentation/'   if(not getattr(sys, 'frozen', False)) else (os.path.join(sys._MEIPASS, 'documentation/'))
readme_path = os.path.join(documentation_path, 'README.md') 
help_path   = os.path.join(documentation_path, 'help/')

# === Flask ===
# Define custom delimiters for template rendering to not collide with Vue
class CustomFlask(flask.Flask):
	jinja_options = flask.Flask.jinja_options.copy()
	jinja_options.update(dict(
		block_start_string='<%',
		block_end_string='%>',
		variable_start_string='%%',
		variable_end_string='%%',
		comment_start_string='<#',
		comment_end_string='#>',
	))

app = CustomFlask(__name__, static_url_path='', template_folder=index_html_directory_path)

# Disable caching of static files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.config['SECRET_KEY'] = 'secretkey'
socketio = flask_socketio.SocketIO(app)



# === SocketIO ===
# Infinite loop for a background thread to handle UI messages that show up in the 'share' global shared memory object
def managerMessageForwarder():
	global share
	
	while(True):
		while pipes.poll(share, 'QueueToUI'):
			message = pipes.recv(share, 'QueueToUI')
			socketio.emit('Server Message', message)
		socketio.sleep(UI_REFRESH_DELAY_SECONDS)

# Create UI handler thread when socketio is connected
managerMessageForwarderthread = None
@socketio.on('connect')
def connect():
	global managerMessageForwarderthread                                                               
	if(managerMessageForwarderthread is None):
		managerMessageForwarderthread = socketio.start_background_task(target=managerMessageForwarder)

@socketio.on('Client Notification')
def custom_connection_notification(json):
	print('[UI]: Received socketio notification: ' + str(json))



# === Home Page ===
@app.route('/')
@app.route('/index')
@app.route('/ui/index')
@app.route('/ui/index.html')
def index():
	# Obtain a list of components within the components folder and sub-folders
	components = glob.glob(index_html_directory_path + '/components/**/*.html', recursive=True)
	
	# Get rid of the initial 'ui/' since paths should be relative from template folder
	components = [c[len(index_html_directory_path):] for c in components]
	
	# Make sure we use forward slashes no matter what system we are on
	components = [c.replace('\\', '/') for c in components]
	
	return flask.render_template('index.html', components=components)

@app.route('/ui/<path:path>')
def sendResourceFilesFromCorrectDirectory(path):
	return flask.send_from_directory(index_html_directory_path, path)
	
	
	
# === ===
# Disable server-side caching
@app.after_request
def add_header(response):
	response.cache_control.max_age = 0
	response.cache_control.no_store = True
	if('Cache-Control' not in response.headers):
		response.headers['Cache-Control'] = 'no-store'
	return response



# === Webbrowser ===
def findFirstOpenPort(startPort=1, blacklist=[5000]):
	for port in range(startPort, 8081):
		if(port not in blacklist):
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
				try:
					sock.bind((SOCKETIO_DEFAULT_IP_ADDRESS, port))
					sock.close()
					print('[UI]: Port {} is available.'.format(port))
					return port
				except Exception as e:
					print('[UI]: Port {} is not available.'.format(port))
				
def launchBrowser(url):
	socketio.sleep(2)
	print('[UI]: Opening Web Browser with URL: "{}"'.format(url))
	webbrowser.open_new(url)



# === Main ===
def start(share={}, debug=True, use_reloader=True, specific_port=None):
	makeShareGlobal(share)
	
	if('AutexysUIRunning' in os.environ):
		print('Reload detected. Not opening browser.')
		print('Still running on port {}'.format(os.environ['AutexysUIPort']))
	else:
		port = specific_port if(specific_port is not None) else findFirstOpenPort(startPort=5000)
		print('[UI]: Serving port {}'.format(port))
	
		os.environ['AutexysUIRunning'] = 'True'
		os.environ['AutexysUIPort'] = str(port)
		
		launch_browser = (specific_port is None)
		if(launch_browser):
			url = 'http://'+ SOCKETIO_DEFAULT_IP_ADDRESS +':{:}/ui/index.html'.format(port)
			socketio.start_background_task(launchBrowser, url)
	
	# app.run(debug=True, threaded=False, port=int(os.environ['AutexysUIPort']))
	socketio.run(app, debug=debug, port=int(os.environ['AutexysUIPort']), use_reloader=use_reloader)

def makeShareGlobal(localShare):
	global share
	share = localShare	





# ========== Begin Custom Server API ==========
# Everything from here onwards is a user-defined server function that is specific to this application.





# === JSON Formatting ===
def jsonvalid(obj):
	return json.dumps(replaceInfNan(obj))

def replaceInfNan(obj):
	if isinstance(obj, float):
		if np.isnan(obj):
			return None
		if obj == float('inf'):
			return 1e99
		if obj == -float('inf'):
			return -1e99
		return obj
	elif isinstance(obj, str):
		return obj
	elif isinstance(obj, bytes):
		return obj
	elif isinstance(obj, Sequence):
		return [replaceInfNan(item) for item in obj]
	elif isinstance(obj, Mapping):
		return dict((key, replaceInfNan(value)) for key, value in obj.items())
	else:
		return obj



# === System Info ===
@app.route('/setWorkspaceDataFolderPath', methods=['POST'])
def setWorkspaceDataFolderPath():
	path = flask.request.get_json(force=True)
	
	# Sets workspace data folder path for the entire UI portion of the Python Server (browsing data, loading plots, saving schedule files, etc). But, does NOT affect data saving for experiments run by the Python Server, that is still handled directly by dispatcher.py and launcher.py
	global workspace_data_path
	workspace_data_path = path
	
	return jsonvalid({"success": True})
		
@app.route('/<user>/addUser.json')
def addUser(user):
	dlu.makeFolder(os.path.join(workspace_data_path, user))
	return jsonvalid({"success": True})

@app.route('/paths.json')
def paths():
	sourceAbsPath = os.path.abspath(os.path.dirname(__file__))
	return jsonvalid({'sourceAbsPath': sourceAbsPath})



# === System Parameters ===
@app.route('/defaultParameters.json')
def defaultParameters():
	return jsonvalid(defaults.get())

@app.route('/defaultParametersDescription.json')
def defaultParametersDescription():
	return jsonvalid(defaults.full())

@app.route('/defaultEssentialParameters.json')
def defaultEssentialParameters():
	return jsonvalid(defaults.full_essentials())

@app.route('/defaultIdentifiers.json')
def defaultIdentifiers():
	return jsonvalid(defaults.full_identifiers())
	
	
	
# === Measurement System Connection Status ===
@app.route('/availableMeasurementSystems.json')
def availableMeasurementSystems():	
	print('[UI]: Requesting Updated Connection Status...')
	pipes.send(share, 'QueueToStatusChecker', {'type':'ConnectionStatusRequest'})
	print('[UI]: Status request has been sent.')
	return jsonvalid({"success": True})
	
@app.route('/connectToMeasurementSystem', methods=['POST'])
def connectToMeasurementSystem():
	system = flask.request.get_json(force=True)
	print('[UI]: Requesting New Connection Established...')
	pipes.send(share, 'QueueToStatusChecker', {'type':'Connect', 'system':system})
	print('[UI]: Connection request has been sent.')
	return jsonvalid({"success": True})

@app.route('/disconnectFromMeasurementSystem.json')
def disconnectFromMeasurementSystem():
	print('[UI]: Requesting Disconnection...')
	pipes.send(share, 'QueueToStatusChecker', {'type':'Disconnect'})
	print('[UI]: Disconnection request has been sent.')
	return jsonvalid({"success": True})



# === Measurement System Configuration ===
@app.route('/loadMeasurementSystemConfiguration/<systemType>')
def loadMeasurementSystemConfiguration(systemType):
	path = os.path.join(config_path, systemType)
	
	# Load the system-specific config file
	config_file = {}
	loadedJSON = dlu.loadJSON(path, CONFIG_FILE_NAME)
	for json in loadedJSON:
		config_file.update(json)
	
	# Load all of the custom info docs for this system
	config_docs = []
	for filename in getConfigurationFilenames(systemType):
		loadedJSON = dlu.loadJSON(path, filename)
		for json in loadedJSON:
			config_docs.append(json)

	return jsonvalid({'config': config_file, 'docs': config_docs})

def getConfigurationFilenames(systemType):
	filenames = []
	path = os.path.join(config_path, systemType)
	if(os.path.exists(path)):
		directoryListings = os.listdir(path)
		# directoryListings in arbitrary order
		for listing in directoryListings:
			if(len(listing) >= len(CONFIG_DOC_PREFIX)) and (listing[0:len(CONFIG_DOC_PREFIX)] == CONFIG_DOC_PREFIX) and (listing[-len(CONFIG_DOC_SUFFIX):] == CONFIG_DOC_SUFFIX):
				filenames.append(listing)
		filenames.sort(key=lambda listing : int(listing[len(CONFIG_DOC_PREFIX):-len(CONFIG_DOC_SUFFIX)]))
	return filenames



# === Browser ===
@app.route('/users.json')
def users():
	paths = glob.glob(os.path.join(workspace_data_path, '*/'))
	names = [os.path.basename(os.path.dirname(p)) for p in paths]
	return jsonvalid(names)

@app.route('/<user>/projects.json')
def projects(user):
	paths = glob.glob(os.path.join(workspace_data_path, user, '*/'))
	names = [os.path.basename(os.path.dirname(p)) for p in paths]
	
	projects = [{'name': n} for n in names]
	
	return jsonvalid(projects)

@app.route('/<user>/<project>/wafers.json')
def wafers(user, project):
	paths = glob.glob(os.path.join(workspace_data_path, user, project, '*/'))
	names = [os.path.basename(os.path.dirname(p)) for p in paths if((os.path.basename(os.path.dirname(p)) != 'schedules') or (len(glob.glob(os.path.join(p, '*/'))) > 0))]
	modificationTimes = [os.path.getmtime(p) for p in paths]
	sizes = [recursiveFileSize(p) for p in paths]
	chipCounts = [len(glob.glob(p + '/*/')) for p in paths]
	
	indexFileLists = [glob.glob(p + '/**/index.json', recursive=True) for p in paths]
	indexObjectLists = [[dlu.loadJSONIndex(os.path.dirname(indexFile)) for indexFile in indexFileList] for indexFileList in indexFileLists]
	indexCounts = [sum([(i['index'] if 'index' in i else 0) for i in indexObjectList]) for indexObjectList in indexObjectLists]
	experimentCounts = [sum([(i['experimentNumber'] if 'experimentNumber' in i else 0) for i in indexObjectList]) for indexObjectList in indexObjectLists]
	
	abreviatedPaths = ['Workspace' + os.sep + str(user) + os.sep + str(project) + os.sep + str(n) + os.sep for n in names]
	
	wafers = [{'name': n, 'path': p, 'modificationTime': m, 'size': s, 'chipCount': c, 'indexCount': ic, 'experimentCount': ec} for n, p, m, s, c, ic, ec in zip(names, abreviatedPaths, modificationTimes, sizes, chipCounts, indexCounts, experimentCounts)]
	
	return jsonvalid(wafers)

@app.route('/<user>/<project>/<wafer>/chips.json')
def chips(user, project, wafer):
	paths = glob.glob(os.path.join(workspace_data_path, user, project, wafer, '*/'))
	names = [os.path.basename(os.path.dirname(p)) for p in paths]
	modificationTimes = [os.path.getmtime(p) for p in paths]
	sizes = [recursiveFileSize(p) for p in paths]
	
	subPathsList = [glob.glob(p + '/*/') for p in paths]
	deviceCounts = [len(subPaths) for subPaths in subPathsList]
	
	indexObjectLists = [[dlu.loadJSONIndex(p) for p in subPaths] for subPaths in subPathsList]
	indexCounts = [sum([(i['index'] if 'index' in i else 0) for i in indexObjectList]) for indexObjectList in indexObjectLists]
	experimentCounts = [sum([(i['experimentNumber'] if 'experimentNumber' in i else 0) for i in indexObjectList]) for indexObjectList in indexObjectLists]
	
	abreviatedPaths = ['Workspace' + os.sep + str(user) + os.sep + str(project) + os.sep + str(wafer) + os.sep + str(n) + os.sep for n in names]
	
	chips = [{'name': n, 'path': p, 'modificationTime': m, 'size': s, 'deviceCount': d, 'indexCount': ic, 'experimentCount': ec} for n, p, m, s, d, ic, ec in zip(names, abreviatedPaths, modificationTimes, sizes, deviceCounts, indexCounts, experimentCounts)]
	
	return jsonvalid(chips)

@app.route('/<user>/<project>/<wafer>/<chip>/devices.json')
def devices(user, project, wafer, chip):
	paths = glob.glob(os.path.join(workspace_data_path, user, project, wafer, chip, '*/'))
	names = [os.path.basename(os.path.dirname(p)) for p in paths]
	modificationTimes = [os.path.getmtime(p+'ParametersHistory.json') if os.path.exists(p+'ParametersHistory.json') else os.path.getmtime(p) for p in paths]
	sizes = [recursiveFileSize(p) for p in paths]
	
	indexObjects = [dlu.loadJSONIndex(p) for p in paths]
	indexCounts = [i['index'] for i in indexObjects]
	experimentCounts = [i['experimentNumber'] for i in indexObjects]
	
	abreviatedPaths = ['Workspace' + os.sep + str(user) + os.sep + str(project) + os.sep + str(wafer) + os.sep + str(chip) + os.sep + str(n) + os.sep for n in names]
	
	devices = [{'name': n, 'path': p, 'modificationTime': m, 'size': s, 'indexCount': ic, 'experimentCount': ec} for n, p, m, s, ic, ec in zip(names, abreviatedPaths, modificationTimes, sizes, indexCounts, experimentCounts)]
	
	return jsonvalid(devices)

@app.route('/<user>/<project>/<wafer>/<chip>/<device>/experiments.json')
def experiments(user, project, wafer, chip, device):	
	folder = os.path.join(workspace_data_path, user, project, wafer, chip, device)
	
	paths = glob.glob(os.path.join(folder, '*/'))
	names = [os.path.basename(os.path.dirname(p)) for p in paths]
	
	# Load all found experiment folders and make a dictionary of experiments
	experimentDictionary = {}
	for name in names:
		if(defaults.EXPERIMENT_FOLDER_PREFIX in name and name.replace(defaults.EXPERIMENT_FOLDER_PREFIX, '').isdigit()):
			experimentDictionary[int(name.replace(defaults.EXPERIMENT_FOLDER_PREFIX, ''))] = None
	
	# Load parameters history
	try:
		parametersHistory = dlu.loadJSON(folder, 'ParametersHistory.json')
	except:
		parametersHistory = []

	# For every experiment that has a "ParametersHistory.json", add that to the information to the dictionary of experiments
	for experimentParameters in parametersHistory:
		experimentDictionary[experimentParameters['startIndexes']['experimentNumber']] = experimentParameters
	
	for experimentNumber in experimentDictionary.keys():
		# If an experiment had no "ParametersHistory.json", load the last known data entry for that experiment and use it to reconstruct as much info as possible
		experimentFolder = os.path.join(folder, defaults.EXPERIMENT_FOLDER_PREFIX + str(experimentNumber))
		experimentFiles = glob.glob(os.path.join(experimentFolder, '*.json'))
		
		if(experimentDictionary[experimentNumber] is None):
			lastDataEntryParameters = None
			for dataFile in experimentFiles:
				dataParameters = dlu.loadJSON(experimentFolder, os.path.basename(dataFile))[-1]
				if((lastDataEntryParameters is None) or (dataParameters['index'] > lastDataEntryParameters['index'])):
					lastDataEntryParameters = dataParameters
			del lastDataEntryParameters['Results']
			lastDataEntryParameters['endIndexes'] = dict(lastDataEntryParameters['startIndexes'])
			lastDataEntryParameters['endIndexes']['index'] = lastDataEntryParameters['index']
			lastDataEntryParameters['endIndexes']['experimentNumber'] = lastDataEntryParameters['experimentNumber']
			lastDataEntryParameters['parametersHistoryGenerated'] = True
			experimentDictionary[experimentNumber] = lastDataEntryParameters
		
		# Get the possible plots for this experiment and save that with the parameters 
		parameter_identifiers = getIdentifierParameters(user, project, wafer, chip, device)
		experimentDictionary[experimentNumber]['possiblePlots'] = DH.plotsForExperiments(parameter_identifiers, minExperiment=experimentNumber, maxExperiment=experimentNumber)
		
		experimentDictionary[experimentNumber]['dataFolderSpecific'] = experimentFolder
		experimentDictionary[experimentNumber]['dataFolderSpecificAbs'] = os.path.abspath(experimentFolder)
		experimentDictionary[experimentNumber]['dataFiles'] = [os.path.basename(f) for f in experimentFiles]
		
	# Finally, extract all of the experiments from the dictionary that we built and return the list of their parameters
	experiments = [experimentDictionary[key] for key in sorted(experimentDictionary.keys())]
	
	return jsonvalid(experiments)

@app.route('/<user>/<projectFilter>/<waferFilter>/<chipFilter>/<deviceFilter>/<category>/recentActivity.json')
def recentActivity(user, projectFilter, waferFilter, chipFilter, deviceFilter, category):
	basename = lambda path: os.path.basename(os.path.dirname(path))
	
	# Create a regex for each directory for glob
	projects_included = '*/' if(projectFilter is None or projectFilter == 'undefined') else ('{:}/'.format(projectFilter))
	wafers_included   = '*/' if(waferFilter   is None or waferFilter   == 'undefined') else ('{:}/'.format(waferFilter))
	chips_included    = '*/' if(chipFilter    is None or chipFilter    == 'undefined') else ('{:}/'.format(chipFilter))
	devices_included  = '*/' if(deviceFilter  is None or deviceFilter  == 'undefined') else ('{:}/'.format(deviceFilter))
				
	# Get list of all projects, wafers, chips, devices for this user. Each element in the list is a dictionary containing the relevant identifiers, plus its modification time.
	projects  =                         [{'modified':os.path.getmtime(p), 'project': basename(p)}                                                                       for p in glob.glob(os.path.join(workspace_data_path, user, projects_included))]
	wafers    = [(elem) for sublist in [[{'modified':os.path.getmtime(w), 'project': item['project'], 'wafer':basename(w)}                                              for w in glob.glob(os.path.join(workspace_data_path, user, item['project'], wafers_included))]                               for item in projects] for elem in sublist] if(category not in ['project']) else None
	chips     = [(elem) for sublist in [[{'modified':os.path.getmtime(c), 'project': item['project'], 'wafer':item['wafer'], 'chip':basename(c)}                        for c in glob.glob(os.path.join(workspace_data_path, user, item['project'], item['wafer'], chips_included))]                 for item in wafers]   for elem in sublist] if(category not in ['project', 'wafer']) else None
	devices   = [(elem) for sublist in [[{'modified':os.path.getmtime(d), 'project': item['project'], 'wafer':item['wafer'], 'chip':item['chip'], 'device':basename(d)} for d in glob.glob(os.path.join(workspace_data_path, user, item['project'], item['wafer'], item['chip'], devices_included))] for item in chips]    for elem in sublist] if(category not in ['project', 'wafer', 'chip']) else None
	
	# Choose which list to report as the recent activity list
	if(wafers is None):	
		recentActivity = projects
	elif(chips is None):
		recentActivity = [elem for elem in wafers if(elem['wafer'] != 'schedules')]
	elif(devices is None):
		recentActivity = chips
	else:
		recentActivity = devices
	
	# Add 'user' tag to every entry
	for item in recentActivity:
		item['user'] = user
		
	return jsonvalid(recentActivity)

@app.route('/<user>/<project>/indexes.json')
def indexes(user, project):
	indexObject = {}
	
	waferPaths = glob.glob(os.path.join(workspace_data_path, user, project, '*/'))
	waferNames = [os.path.basename(os.path.dirname(p)) for p in waferPaths]
	
	for waferPath, waferName in zip(waferPaths, waferNames):
		indexObject[waferName] = {}
		chipPaths = glob.glob(waferPath + '/*/')
		chipNames = [os.path.basename(os.path.dirname(p)) for p in chipPaths]
		
		for chipPath, chipName in zip(chipPaths, chipNames):
			indexObject[waferName][chipName] = {}
			devicePaths = glob.glob(chipPath + '/*/index.json')
			deviceNames = [os.path.basename(os.path.dirname(p)) for p in devicePaths]
			
			for devicePath, deviceName in zip(devicePaths, deviceNames):
				indexObject[waferName][chipName][deviceName] = dlu.loadJSONIndex(os.path.dirname(devicePath))
	
	return jsonvalid(indexObject)

def recursiveFileSize(directory):
	total_size = os.path.getsize(directory)
	for folder in os.listdir(directory):
		subpath = os.path.join(directory, folder)
		if(os.path.isfile(subpath)):
			total_size += os.path.getsize(subpath)
		else:
			total_size += recursiveFileSize(subpath)
	return total_size

def getIdentifierParameters(user, project, wafer, chip, device=None):
	parameter_identifiers = {'dataFolder':workspace_data_path, 'Identifiers':{'user':user,'project':project,'wafer':wafer,'chip':chip,'device':device}} 	
	return parameter_identifiers
	
	
	
# === Data Export ===
@app.route('/saveCSV/<user>/<project>/<wafer>/<chip>/<device>/<experiment>/data.csv')
def saveCSV(user, project, wafer, chip, device, experiment):
	# Find all '.json' files saved for this experiment
	path = os.path.join(workspace_data_path, user, project, wafer, chip, device, defaults.EXPERIMENT_FOLDER_PREFIX + experiment)
	fileNames = [os.path.basename(p) for p in glob.glob(os.path.join(path, '*.json'))]
	
	# Load data from all '.json' files
	deviceHistories = [dlu.loadJSON(path, fileName) for fileName in fileNames]
	
	# Create data saving objects
	proxy = io.StringIO()
	filebuf = io.BytesIO()
	
	# Save into StringIO 
	dlu.saveCSV(deviceHistories, proxy)
	
	# Convert from StringIO to BytesIO
	filebuf.write(proxy.getvalue().encode('utf-8'))
	proxy.close()
	
	filebuf.seek(0)
	return flask.send_file(filebuf, attachment_filename=defaults.DATA_EXPORT_NAME)



# === Plots ===
def getPlotSettings(plotType, filebuf, minExperiment, maxExperiment, includeChipSummarySettings=False, includeDeviceSummarySettings=False, includeCacheBust=False):
	# === Setup ===
	# Get default plot settings, plus any modifications specified by the UI
	plotSettings = copy.deepcopy(default_makePlot_parameters)
	receivedPlotSettings = json.loads(flask.request.args.get('plotSettings'))
	print('[UI]: Loaded plot settings: ' + str(receivedPlotSettings))
	
	# Make nicknames for any plot setting modifications specified by the UI
	primaryPlotSettings = receivedPlotSettings['primary']
	modePlotSettings = receivedPlotSettings['mode_parameters']
	chipSummarySettings = receivedPlotSettings['chip']
	deviceSummarySettings = receivedPlotSettings['device']
	
	# === Update Settings ===
	# Update dynamic arguments to DeviceHistory.makePlots() call
	for dynamicArgument in primaryPlotSettings.keys():
		plotSettings[dynamicArgument] = primaryPlotSettings[dynamicArgument]
	if(includeChipSummarySettings):
		for dynamicArgument in chipSummarySettings.keys():
			plotSettings[dynamicArgument] = chipSummarySettings[dynamicArgument]
	if(includeDeviceSummarySettings):
		for dynamicArgument in deviceSummarySettings.keys():
			plotSettings[dynamicArgument] = deviceSummarySettings[dynamicArgument]
	
	# Set all fixed arguments to DeviceHistory.makePlots() call
	if plotSettings['minExperiment'] == None:
		plotSettings['minExperiment'] = minExperiment
	if plotSettings['maxExperiment'] == None:
		plotSettings['maxExperiment'] = maxExperiment
	plotSettings['plotSaveName'] = filebuf
	plotSettings['dataFolder'] = workspace_data_path
	plotSettings['saveFolder'] = None
	plotSettings['saveFigures'] = True
	plotSettings['showFigures'] = False
	plotSettings['specificPlot'] = plotType
	if(includeCacheBust):
		plotSettings['cacheBust'] = flask.request.args.get('cb')
	
	# Set mode parameters for DeviceHistory.makePlots() call
	if(plotSettings['plot_mode_parameters'] is None):
		plotSettings['plot_mode_parameters'] = {}
	for dynamicModeParameter in modePlotSettings.keys():
		plotSettings['plot_mode_parameters'][dynamicModeParameter] = modePlotSettings[dynamicModeParameter]
	
	#afmPath = json.loads(flask.request.args.get('afmPath'))
	# mode parameter 'AFMImagePath'
	#if(plotType == 'AFMdeviationsImage'):
	#	if(plotSettings['plot_mode_parameters'] == None):
	#		plotSettings['plot_mode_parameters'] = {}
	#	plotSettings['plot_mode_parameters']['afm_image_path'] = afmPath
	
	return plotSettings

@app.route('/plots/<user>/<project>/<wafer>/<chip>/<device>/<experiment>/<plotType>')
def sendExperimentPlot(user, project, wafer, chip, device, experiment, plotType):
	# Make a new file object to save the image for this plot
	filebuf = io.BytesIO()
	
	# Get all arguments for the DeviceHistory.makePlots() function call
	plotSettings = getPlotSettings(plotType, filebuf, minExperiment=int(experiment), maxExperiment=int(experiment), includeCacheBust=True)
	
	# === Plot ===
	DH.makePlots(user, project, wafer, chip, device, **plotSettings)
	# plt.savefig(filebuf, transparent=True, dpi=pngDPI, format='png')
	filebuf.seek(0)
	return flask.send_file(filebuf, attachment_filename='plot.png')
	
@app.route('/devicePlots/<user>/<project>/<wafer>/<chip>/<device>/<plotType>')
def sendDevicePlot(user, project, wafer, chip, device, plotType):
	# Make a new file object to save the image for this plot
	filebuf = io.BytesIO()
	
	# Get all arguments for the DeviceHistory.makePlots() function call
	plotSettings = getPlotSettings(plotType, filebuf, minExperiment=0, maxExperiment=float('inf'), includeDeviceSummarySettings=True)
	plotSettings['loadOnlyMostRecentExperiments'] = True
	
	# === Plot ===
	DH.makePlots(user, project, wafer, chip, device, **plotSettings)
	filebuf.seek(0)
	return flask.send_file(filebuf, attachment_filename='plot.png')
	
@app.route('/chipPlots/<user>/<project>/<wafer>/<chip>/<plotType>')
def sendChipPlot(user, project, wafer, chip, plotType):
	# Make a new file object to save the image for this plot
	filebuf = io.BytesIO()
	
	# Get all arguments for the ChipHistory.makePlots() function call
	plotSettings = getPlotSettings(plotType, filebuf, minExperiment=0, maxExperiment=float('inf'), includeChipSummarySettings=True)
	plotSettings['numberOfRecentExperiments'] = (plotSettings['numberOfRecentIndexes']) if('numberOfRecentIndexes' in plotSettings) else (1)
	
	# === Plot ===
	CH.makePlots(user, project, wafer, chip, **plotSettings)
	filebuf.seek(0)
	return flask.send_file(filebuf, attachment_filename='plot.png')

@app.route('/<user>/<project>/<wafer>/<chip>/<device>/availableDevicePlots.json')
def availableDevicePlots(user, project, wafer, chip, device):
	parameter_identifiers = getIdentifierParameters(user, project, wafer, chip, device)
	plots = DH.plotsForExperiments(parameter_identifiers, maxPriority=999, linkingFile=None)
	return jsonvalid(plots)
	
@app.route('/<user>/<project>/<wafer>/<chip>/availableChipPlots.json')
def availableChipPlots(user, project, wafer, chip):
	parameter_identifiers = getIdentifierParameters(user, project, wafer, chip)
	plots = CH.plotsForExperiments(parameter_identifiers)
	return jsonvalid(plots)

@app.route('/parameterPlots/<user>/<project>/<fileName>/<standardSchedule>/')
def sendParameterPlot(user, project, fileName, standardSchedule):
	scheduleObjects = []
	if(standardSchedule == 'true'):
		scheduleObjects = loadStandardSchedule(fileName)
	else:
		scheduleObjects = loadSchedule(user, project, fileName)
	parameters = json.loads(scheduleObjects)[0]
	
	filebuf = io.BytesIO()
	mode_parameters = {'plotSaveName': filebuf, 'saveFigures': True, 'showFigures': False}
	
	DH.dpu.makeParameterPlot(parameters['runType']['default'], defaults.extractDefaults(parameters), mode_parameters=mode_parameters)
	filebuf.seek(0)
	return flask.send_file(filebuf, attachment_filename='plot.png')

	

# === Benchtop ===
@app.route('/setBenchtopVoltage/<channel>/<voltage>/')
def setBenchtopVoltage(channel, voltage):
	pipes.send(share, 'QueueToDispatcher', {'type':'SetVoltage', 'channel': int(channel), 'voltage': float(voltage)})
	return jsonvalid({"success":True})
	
@app.route('/setBenchtopRefreshRate/<refresh_rate>/')
def setBenchtopRefreshRate(refresh_rate):
	pipes.send(share, 'QueueToDispatcher', {'type':'SetRefreshRate', 'refresh_rate': float(refresh_rate)})
	return jsonvalid({"success":True})



# === Schedule Files (Schecule Builder and Experiment Runner) ===
@app.route('/saveSchedule/<user>/<project>/<fileName>', methods=['POST'])
def saveSchedule(user, project, fileName):
	receivedJobs = flask.request.get_json(force=True)
	
	# with open(os.path.join(workspace_data_path, user, project, 'schedules/', fileName + '.json'), 'w') as f:
	# 	f.write(json.dumps(receivedJobs))
	
	dlu.makeEmptyJSONFile(os.path.join(workspace_data_path, user, project, 'schedules/'), fileName)
	for job in receivedJobs:
		dlu.saveJSON(os.path.join(workspace_data_path, user, project, 'schedules/'), fileName, defaults.extractDefaults(job), incrementIndex=False)
	print('[UI]: Saved schedule file.')
	
	return jsonvalid({"success":True})

@app.route('/loadSchedule/<user>/<project>/<fileName>.json')
def loadSchedule(user, project, fileName):
	scheduleData = dlu.loadJSON(os.path.join(workspace_data_path, user, project, 'schedules/'), fileName + '.json')
	expandedScheduleData = [defaults.full_with_added(job) for job in scheduleData]
	print('[UI]: Loaded schedule file.')
	return jsonvalid(expandedScheduleData)

@app.route('/loadBriefSchedule/<user>/<project>/<fileName>.json')
def loadBriefSchedule(user, project, fileName):
	scheduleData = dlu.loadJSON(os.path.join(workspace_data_path, user, project, 'schedules/'), fileName + '.json')
	expandedScheduleData = [defaults.full_with_only(job) for job in scheduleData]
	return jsonvalid(expandedScheduleData)

@app.route('/loadStandardSchedule/<fileName>.json')
def loadStandardSchedule(fileName):
	expandedScheduleData = [defaults.full_schedule(fileName)]
	return jsonvalid(expandedScheduleData)

@app.route('/loadBriefStandardSchedule/<fileName>.json')
def loadBriefStandardSchedule(fileName):
	expandedScheduleData = [defaults.full_brief_schedule(fileName)]
	return jsonvalid(expandedScheduleData)

@app.route('/dispatchSchedule/<user>/<project>/<fileName>.json')
def dispatchSchedule(user, project, fileName):
	scheduleFilePath = os.path.join(workspace_data_path, user, project, 'schedules', fileName + '.json')
	print('[UI]: Requesting Dispatcher Run...')
	pipes.send(share, 'QueueToManager', {'type':'Dispatch', 'dispatcher_command': scheduleFilePath, 'workspace_data_path': workspace_data_path})
	print('[UI]: Run request has been sent.')
	return jsonvalid({"success": True})

@app.route('/dispatchRunType/<runType>.json')
def dispatchRunType(runType):
	print('[UI]: Requesting Dispatcher Run...')
	pipes.send(share, 'QueueToManager', {'type':'Dispatch', 'dispatcher_command': runType, 'workspace_data_path': workspace_data_path})
	print('[UI]: Run request has been sent.')
	return jsonvalid({"success": True})

@app.route('/stopDispatcher')
def stopDispatcher():
	print('[UI]: Requesting Dispatcher Abort...')
	pipes.send(share, 'QueueToDispatcher', {'type':'Stop'})
	print('[UI]: Abort request has been sent.')
	return jsonvalid({"success": True})

@app.route('/standardScheduleNames.json')
def listStandardScheduleNames():
	return jsonvalid(list(defaults.full_schedules().keys()))

@app.route('/userDefinedScheduleNames.json')
def loadUserDefinedScheduleNames():
	getSubDirectories = lambda directory: [os.path.basename(os.path.dirname(g)) for g in glob.glob(directory + '/*/')]
	
	scheduleNames = {}
	
	for userName in getSubDirectories(workspace_data_path):
		scheduleNames[userName] = {}
		for projectName in getSubDirectories(os.path.join(workspace_data_path, userName)):
			schedulePaths = glob.glob(os.path.join(workspace_data_path, userName, projectName, 'schedules/*.json'))
			scheduleNames[userName][projectName] = [os.path.basename(schedule).split('.')[0] for schedule in schedulePaths]
	
	return jsonvalid(scheduleNames)



# === README ===
@app.route('/readme.md')
def getReadMe():
	with open(readme_path, 'r') as f:
		return f.read()



# === Notes ===
@app.route('/addNote/<user>/<project>/<wafer>/<chip>/<device>/<experimentNumber>', methods=['POST'])
def addNote(user, project, wafer, chip, device, experimentNumber):
	noteAddition = flask.request.get_json(force=True)
	parameter_identifiers = getIdentifierParameters(user, project, wafer, chip, device)
	path = dlu.getExperimentDirectory(dlu.getDeviceDirectory(parameter_identifiers), experimentNumber)
	
	dlu.appendText(path, defaults.NOTES_FILE_NAME, noteAddition['noteAddition'])
	print('[UI]: Saved changes to Note.')
	
	return jsonvalid({"success": True})
	
@app.route('/getNote/<user>/<project>/<wafer>/<chip>/<device>/<experimentNumber>')	
def getNote(user, project, wafer, chip, device, experimentNumber):
	parameter_identifiers = getIdentifierParameters(user, project, wafer, chip, device)
	path = dlu.getExperimentDirectory(dlu.getDeviceDirectory(parameter_identifiers), experimentNumber)
	
	text = dlu.loadText(path, defaults.NOTES_FILE_NAME)
	
	return jsonvalid({"text":text})

@app.route('/clearNote/<user>/<project>/<wafer>/<chip>/<device>/<experimentNumber>')	
def clearNote(user, project, wafer, chip, device, experimentNumber):
	parameter_identifiers = getIdentifierParameters(user, project, wafer, chip, device)
	path = dlu.getExperimentDirectory(dlu.getDeviceDirectory(parameter_identifiers), experimentNumber)
	
	dlu.overwriteText(path, defaults.NOTES_FILE_NAME, '')
	print('[UI]: Cleared Note.')
	
	return jsonvalid({"success": True})



# === Documentation ===
@app.route('/addDocumentation/<indexToAdd>')
def addDocumentation(indexToAdd):
	incrementFilenameNumbersFrom(indexToAdd, 1)
	dlu.makeEmptyJSONFile(help_path, HELP_DOC_PREFIX + str(indexToAdd) + HELP_DOC_SUFFIX)
	return jsonvalid({"success": True})

@app.route('/removeDocumentation/<indexToDelete>')
def removeDocumentation(indexToDelete):
	dlu.deleteJSONFile(help_path, HELP_DOC_PREFIX + indexToDelete + HELP_DOC_SUFFIX)
	incrementFilenameNumbersFrom(int(indexToDelete) + 1, -1)
	return jsonvalid({"success": True})

@app.route('/loadDocumentation')
def loadDocumentation():
	documentationData = []

	for filename in getDocumentationFilenames():
		loadedJSON = dlu.loadJSON(help_path, filename)
		for json in loadedJSON:
			documentationData.append(json)

	return jsonvalid(documentationData)

@app.route('/saveDocumentation/<fileName>', methods=['POST'])
def saveDocumentation(fileName):
	receivedDocumentation = flask.request.get_json(force=True)

	dlu.makeEmptyJSONFile(help_path, HELP_DOC_PREFIX + fileName + HELP_DOC_SUFFIX)
	dlu.saveJSON(help_path, HELP_DOC_PREFIX + fileName + HELP_DOC_SUFFIX, receivedDocumentation, incrementIndex=False)

	return jsonvalid({"success": True})

@app.route('/swapDocumentationFilenames/<index1>/<index2>')
def swapDocumentationFilenames(index1, index2):
	swapFilenames(HELP_DOC_PREFIX + index1 + HELP_DOC_SUFFIX, HELP_DOC_PREFIX + index2 + HELP_DOC_SUFFIX)
	return jsonvalid({"success": True})

def getDocumentationFilenames():
	filenames = []
	if(os.path.exists(help_path)):
		directoryListings = os.listdir(help_path)
		# directoryListings in arbitrary order
		for listing in directoryListings:
			if(len(listing) >= len(HELP_DOC_PREFIX)) and (listing[0:len(HELP_DOC_PREFIX)] == HELP_DOC_PREFIX) and (listing[-len(HELP_DOC_SUFFIX):] == HELP_DOC_SUFFIX):
				filenames.append(listing)
		filenames.sort(key=lambda listing : int(listing[len(HELP_DOC_PREFIX):-len(HELP_DOC_SUFFIX)]))
	return filenames

def incrementFilenameNumbersFrom(startIndex, increment):
	originalFilenames = getDocumentationFilenames()
	tempFilenames = []
	for originalFilename in originalFilenames:
		numericalSuffix = int(originalFilename[len(HELP_DOC_PREFIX):-len(HELP_DOC_SUFFIX)])
		if numericalSuffix >= int(startIndex):
			if numericalSuffix + increment < 0:
				print("Warning - assigning a documentation file a negative index")
			newSuffix = str(numericalSuffix + increment)
			tempFilename = "TDoc" + newSuffix + HELP_DOC_SUFFIX
			tempFilenames.append(tempFilename)
			os.rename(os.path.join(help_path, originalFilename), os.path.join(help_path, tempFilename))

	for tempFilename in tempFilenames:
		os.rename(os.path.join(help_path, tempFilename), os.path.join(help_path, tempFilename[1:]))

def swapFilenames(file1, file2):
	os.rename(os.path.join(help_path, file1), os.path.join(help_path, "T" + file1))
	os.rename(os.path.join(help_path, file2), os.path.join(help_path, file1))
	os.rename(os.path.join(help_path, "T" + file1), os.path.join(help_path, file2))



# === AFM ===
@app.route('/AFMFilesInTimestampRange/<startTime>/<endTime>/associatedAFMs.json')
def AFMFilesInTimestampRange(startTime, endTime):
	from utilities import AFMReader
	
	startTime = float(startTime)
	endTime = float(endTime)
	
	avg_timestamp = startTime + (endTime - startTime)/2
	
	image_path = AFMReader.bestMatchAFMRegistry(workspace_data_path, targetTimestamp=avg_timestamp)
	
	if (image_path is not None):
		metaData = AFMReader.getAFMMetaData(image_path)
		
		return jsonvalid({'bestMatch':{**metaData, 'image_path':image_path}})
	
	return jsonvalid({})

@app.route('/updateAFMRegistry')
def updateAFMRegistry():
	from utilities import AFMReader
	
	AFMReader.updateAFMRegistry(workspace_data_path)
	
	return jsonvalid({"success":True})
	


if __name__ == '__main__':
	start(debug=False, use_reloader=True, specific_port=None)




