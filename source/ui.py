import io
import os
import sys
import glob
import flask
import json
import copy
import time
import numpy
import webbrowser
import threading
import flask_socketio

import defaults
import pipes

from procedures import Device_History as DH
DH.dpu.mplu.plt.switch_backend('agg')

from procedures import Chip_History as CH
CH.dpu.mplu.plt.switch_backend('agg')

from utilities import DataLoggerUtility as dlu

if __name__ == '__main__':
	os.chdir(sys.path[0])
	
	pathParents = os.getcwd().split('/')
	if 'AutexysHost' in pathParents:
		os.chdir(os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source'))


# Globals
share = None

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)


from collections import Mapping, Sequence

def replaceInfNan(obj):
	if isinstance(obj, float):
		if numpy.isnan(obj):
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

def jsonvalid(obj):
	return json.dumps(replaceInfNan(obj))

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

app = CustomFlask(__name__, static_url_path='', template_folder='ui')

# Disable caching of static files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.config['SECRET_KEY'] = 'secretkey'
socketio = flask_socketio.SocketIO(app)

@app.route('/')
@app.route('/index')
@app.route('/ui/index')
@app.route('/ui/index.html')
def index():
	# Obtain a list of components within the components folder and sub-folders
	components = glob.glob('ui/components/**/*.html', recursive=True)
	
	# Get rid of the initial 'ui/' since paths should be relative from template folder
	components = [c[len('ui/'):] for c in components]
	
	# Make sure we use forward slashes no matter what system we are on
	components = [c.replace('\\', '/') for c in components]
	
	return flask.render_template('index.html', components=components)

@app.route('/ui/<path:path>')
def sendStaticUI(path):
	return flask.send_from_directory('ui', path)

@app.route('/static/<path:path>')
def sendStatic(path):
	return flask.send_from_directory('../', path)

default_makePlot_parameters = {
	'minExperiment': None,
	'maxExperiment': None,
	'minRelativeIndex': 0,
	'maxRelativeIndex': 1e10,
	'specificPlot': '',
	'plotSaveName': '',
	'dataFolder': None,
	'saveFolder': None,
	'saveFigures': False,
	'showFigures': True,
	'plot_mode_parameters': None
}

default_data_path = '../../AutexysData/'
default_documentation_path = '../../AutexysData/documentation'

@app.route('/plots/<user>/<project>/<wafer>/<chip>/<device>/<experiment>/<plotType>')
def sendPlot(user, project, wafer, chip, device, experiment, plotType):
	experiment = int(experiment)
	
	plotSettings = copy.deepcopy(default_makePlot_parameters)
	receivedPlotSettings = json.loads(flask.request.args.get('plotSettings'))
		
	#afmPath = json.loads(flask.request.args.get('afmPath'))
	#plotSettings.update(receivedPlotSettings)
	
	print('Plot settings updated: ' + str(receivedPlotSettings))
	
	primaryPlotSettings = receivedPlotSettings['primary']
	modePlotSettings = receivedPlotSettings['mode_parameters']
	
	filebuf = io.BytesIO()
	
	# Update arguments to DeviceHistory.makePlots() call
	for dynamicArgument in primaryPlotSettings.keys():
		plotSettings[dynamicArgument] = primaryPlotSettings[dynamicArgument]
	
	# Set all fixed arguments to DeviceHistory.makePlots() call
	if plotSettings['minExperiment'] == None:
		plotSettings['minExperiment'] = experiment
	if plotSettings['maxExperiment'] == None:
		plotSettings['maxExperiment'] = experiment
	plotSettings['specificPlot'] = ''
	plotSettings['plotSaveName'] = filebuf
	plotSettings['dataFolder'] = None
	plotSettings['saveFolder'] = None
	plotSettings['saveFigures'] = True
	plotSettings['showFigures'] = False
	plotSettings['specificPlot'] = plotType
	plotSettings['cacheBust'] = flask.request.args.get('cb')
	
	# Set mode parameters for DeviceHistory.makePlots() call
	if(plotSettings['plot_mode_parameters'] is None):
		plotSettings['plot_mode_parameters'] = {}
	for dynamicModeParameter in modePlotSettings.keys():
		plotSettings['plot_mode_parameters'][dynamicModeParameter] = modePlotSettings[dynamicModeParameter]
	
	
	# mode parameter 'AFMImagePath'
	#if(plotType == 'AFMdeviationsImage'):
	#	if(plotSettings['plot_mode_parameters'] == None):
	#		plotSettings['plot_mode_parameters'] = {}
	#	plotSettings['plot_mode_parameters']['afm_image_path'] = afmPath
	
	DH.makePlots(user, project, wafer, chip, device, **plotSettings)
	# plt.savefig(mode_parameters['plotSaveName'], transparent=True, dpi=pngDPI, format='png')
	filebuf.seek(0)
	return flask.send_file(filebuf, attachment_filename='plot.png')

# @app.route('/defaultPlotSettings.json')
# def defaultPlotSettings():
# 	settings = 
# 	return json.dumps(settings)

@app.route('/users.json')
def users():
	paths = glob.glob(os.path.join(default_data_path, '*/'))
	names = [os.path.basename(os.path.dirname(p)) for p in paths]
	return json.dumps(names)

@app.route('/<user>/projects.json')
def projects(user):
	paths = glob.glob(os.path.join(default_data_path, user, '*/'))
	names = [os.path.basename(os.path.dirname(p)) for p in paths]
	
	projects = [{'name': n} for n in names]
	
	return jsonvalid(projects)

@app.route('/<user>/<project>/indexes.json')
def indexes(user, project):
	indexObject = {}
	
	waferPaths = glob.glob(os.path.join(default_data_path, user, project, '*/'))
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

@app.route('/<user>/<project>/wafers.json')
def wafers(user, project):
	paths = glob.glob(os.path.join(default_data_path, user, project, '*/'))
	names = [os.path.basename(os.path.dirname(p)) for p in paths]
	modificationTimes = [os.path.getmtime(p) for p in paths]
	sizes = [os.path.getsize(p) for p in paths]
	chipCounts = [len(glob.glob(p + '/*/')) for p in paths]
	
	indexFileLists = [glob.glob(p + '/**/index.json', recursive=True) for p in paths]
	indexObjectLists = [[dlu.loadJSONIndex(os.path.dirname(indexFile)) for indexFile in indexFileList] for indexFileList in indexFileLists]
	indexCounts = [sum([(i['index'] if 'index' in i else 0) for i in indexObjectList]) for indexObjectList in indexObjectLists]
	experimentCounts = [sum([(i['experimentNumber'] if 'experimentNumber' in i else 0) for i in indexObjectList]) for indexObjectList in indexObjectLists]
	
	wafers = [{'name': n, 'path': p, 'modificationTime': m, 'size': s, 'chipCount': c, 'indexCount': ic, 'experimentCount': ec} for n, p, m, s, c, ic, ec in zip(names, paths, modificationTimes, sizes, chipCounts, indexCounts, experimentCounts)]
	
	return jsonvalid(wafers)

@app.route('/<user>/<project>/<wafer>/chips.json')
def chips(user, project, wafer):
	paths = glob.glob(os.path.join(default_data_path, user, project, wafer, '*/'))
	names = [os.path.basename(os.path.dirname(p)) for p in paths]
	modificationTimes = [os.path.getmtime(p) for p in paths]
	sizes = [os.path.getsize(p) for p in paths]
	
	subPathsList = [glob.glob(p + '/*/') for p in paths]
	deviceCounts = [len(subPaths) for subPaths in subPathsList]
	
	indexObjectLists = [[dlu.loadJSONIndex(p) for p in subPaths] for subPaths in subPathsList]
	indexCounts = [sum([(i['index'] if 'index' in i else 0) for i in indexObjectList]) for indexObjectList in indexObjectLists]
	experimentCounts = [sum([(i['experimentNumber'] if 'experimentNumber' in i else 0) for i in indexObjectList]) for indexObjectList in indexObjectLists]
	
	chips = [{'name': n, 'path': p, 'modificationTime': m, 'size': s, 'deviceCount': d, 'indexCount': ic, 'experimentCount': ec} for n, p, m, s, d, ic, ec in zip(names, paths, modificationTimes, sizes, deviceCounts, indexCounts, experimentCounts)]
	
	return jsonvalid(chips)

@app.route('/<user>/<project>/<wafer>/<chip>/devices.json')
def devices(user, project, wafer, chip):
	paths = glob.glob(os.path.join(default_data_path, user, project, wafer, chip, '*/'))
	names = [os.path.basename(os.path.dirname(p)) for p in paths]
	modificationTimes = [os.path.getmtime(p+'ParametersHistory.json') if os.path.exists(p+'ParametersHistory.json') else os.path.getmtime(p) for p in paths]
	sizes = [os.path.getsize(p+'ParametersHistory.json') if os.path.exists(p+'ParametersHistory.json') else os.path.getsize(p) for p in paths]
	
	indexObjects = [dlu.loadJSONIndex(p) for p in paths]
	indexCounts = [i['index'] for i in indexObjects]
	experimentCounts = [i['experimentNumber'] for i in indexObjects]
	
	devices = [{'name': n, 'path': p, 'modificationTime': m, 'size': s, 'indexCount': ic, 'experimentCount': ec} for n, p, m, s, ic, ec in zip(names, paths, modificationTimes, sizes, indexCounts, experimentCounts)]
	
	return jsonvalid(devices)

@app.route('/<user>/<project>/<wafer>/<chip>/availableChipPlots.json')
def availableChipPlots(user, project, wafer, chip):
	plots = CH.plotsForExperiments(default_data_path, user, project, wafer, chip)
	return jsonvalid(plots)



@app.route('/chipPlots/<user>/<project>/<wafer>/<chip>/<plotType>')
def sendChipPlot(user, project, wafer, chip, plotType):
	plotSettings = copy.deepcopy(default_makePlot_parameters)
	receivedPlotSettings = json.loads(flask.request.args.get('plotSettings'))
	#afmPath = json.loads(flask.request.args.get('afmPath'))
	#plotSettings.update(receivedPlotSettings)
	
	print('Plot settings updated: ' + str(receivedPlotSettings))
	
	filebuf = io.BytesIO()
	
	primaryPlotSettings = receivedPlotSettings['primary']
	modePlotSettings = receivedPlotSettings['mode_parameters']
	chipPlotSettings = receivedPlotSettings['chip']
	
	# Update arguments to DeviceHistory.makePlots() call
	for dynamicArgument in primaryPlotSettings.keys():
		plotSettings[dynamicArgument] = primaryPlotSettings[dynamicArgument]
	for dynamicArgument in chipPlotSettings.keys():
		plotSettings[dynamicArgument] = chipPlotSettings[dynamicArgument]
	
	# Set all fixed arguments to DeviceHistory.makePlots() call
	if plotSettings['minExperiment'] == None:
		plotSettings['minExperiment'] = 0
	if plotSettings['maxExperiment'] == None:
		plotSettings['maxExperiment'] = float('inf')
	plotSettings['specificPlot'] = ''
	plotSettings['plotSaveName'] = filebuf
	plotSettings['dataFolder'] = None
	plotSettings['saveFolder'] = None
	plotSettings['saveFigures'] = True
	plotSettings['showFigures'] = False
	plotSettings['specificPlot'] = plotType
	
	# Set mode parameters for DeviceHistory.makePlots() call
	if(plotSettings['plot_mode_parameters'] is None):
		plotSettings['plot_mode_parameters'] = {}
	for dynamicModeParameter in modePlotSettings.keys():
		plotSettings['plot_mode_parameters'][dynamicModeParameter] = modePlotSettings[dynamicModeParameter]
	
	CH.makePlots(user, project, wafer, chip, **plotSettings)
	filebuf.seek(0)
	return flask.send_file(filebuf, attachment_filename='plot.png')

@app.route('/<user>/<project>/<wafer>/<chip>/<device>/experiments.json')
def experiments(user, project, wafer, chip, device):	
	folder = os.path.join(default_data_path, user, project, wafer, chip, device)
	
	paths = glob.glob(os.path.join(folder, '*/'))
	names = [os.path.basename(os.path.dirname(p)) for p in paths]
	
	# Load all found experiment folders and make a dictionary of experiments
	experimentDictionary = {}
	for name in names:
		if('Ex' in name and name.replace('Ex', '').isdigit()):
			experimentDictionary[int(name.replace('Ex', ''))] = None
	
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
		experimentFolder = os.path.join(folder, 'Ex' + str(experimentNumber))
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
		parameter_identifiers = {'dataFolder':default_data_path, 'Identifiers':{'user':user,'project':project,'wafer':wafer,'chip':chip,'device':device}}
		experimentDictionary[experimentNumber]['possiblePlots'] = DH.plotsForExperiments(parameter_identifiers, minExperiment=experimentNumber, maxExperiment=experimentNumber)
		
		experimentDictionary[experimentNumber]['dataFolderSpecific'] = experimentFolder
		experimentDictionary[experimentNumber]['dataFolderSpecificAbs'] = os.path.abspath(experimentFolder)
		experimentDictionary[experimentNumber]['dataFiles'] = [os.path.basename(f) for f in experimentFiles]
		
	# Finally, extract all of the experiments from the dictionary that we built and return the list of their parameters
	experiments = [experimentDictionary[key] for key in sorted(experimentDictionary.keys())]
	
	return jsonvalid(experiments)


@app.route('/parametersDescription.json')
def parametersDescription():
	# return flask.jsonify(defaults.default_parameters_description)
	return jsonvalid(defaults.default_parameters)

@app.route('/defaultParameters.json')
def defaultParameters():
	return jsonvalid(defaults.get())

@app.route('/defaultEssentialParameters.json')
def defaultEssentialParameters():
	return jsonvalid(defaults.full_essentials())

@app.route('/deleteDocumentation/<fileName>')
def deleteDocumentation(fileName):
	dlu.deleteFile(default_documentation_path + '/', fileName + ".json")
	return jsonvalid({'success': True})

@app.route('/loadAllDocumentation')
def loadAllDocumentation():
	documentationData = dlu.loadAllJSONFilesInDirectory(default_documentation_path)
	return jsonvalid(documentationData)

@app.route('/saveDocumentation/<fileName>', methods=['POST'])
def saveDocumentation(fileName):
	receivedDocumentation = flask.request.get_json(force=True)

	dlu.emptyFile(default_documentation_path + '/', fileName + ".json")
	dlu.saveJSON(default_documentation_path + '/', fileName + ".json", receivedDocumentation, incrementIndex=False)

	return jsonvalid({'success': True})

@app.route('/saveSchedule/<fileName>', methods=['POST'])
def saveSchedule(fileName):
	# receivedJobs = json.loads(flask.request.args.get('jobs'))
	receivedJobs = flask.request.get_json(force=True)
	
	# with open(os.path.join(default_data_path, user, project, 'schedules/', fileName + '.json'), 'w') as f:
	# 	f.write(json.dumps(receivedJobs))
	
	dlu.emptyFile(os.path.join(default_data_path, user, project, 'schedules/'), fileName)
	for job in receivedJobs:
		dlu.saveJSON(os.path.join(default_data_path, user, project, 'schedules/'), fileName, defaults.extractDefaults(job), incrementIndex=False)
	
	return jsonvalid({'success':True})

@app.route('/loadSchedule/<user>/<project>/<fileName>.json')
def loadSchedule(user, project, fileName):
	scheduleData = dlu.loadJSON(os.path.join(default_data_path, user, project, 'schedules/'), fileName + '.json')
	
	expandedScheduleData = []
	for job in scheduleData:
		expandedScheduleData.append(defaults.full_with_added(job))
	
	return jsonvalid(expandedScheduleData)

@app.route('/loadBriefSchedule/<user>/<project>/<fileName>.json')
def loadBriefSchedule(user, project, fileName):
	scheduleData = dlu.loadJSON(os.path.join(default_data_path, user, project, 'schedules/'), fileName + '.json')
	
	expandedScheduleData = []
	for job in scheduleData:
		expandedScheduleData.append(defaults.full_with_only(job))
	
	return jsonvalid(expandedScheduleData)

def getSubDirectories(directory):
	return [os.path.basename(os.path.dirname(g)) for g in glob.glob(directory + '/*/')]

@app.route('/dispatchSchedule/<user>/<project>/<fileName>.json')
def dispatchSchedule(user, project, fileName):
	scheduleFilePath = os.path.join(default_data_path, user, project, 'schedules', fileName + '.json')
	eprint('UI Sending RUN:')
	pipes.send(share, 'QueueToManager', {'type':'Dispatch', 'scheduleFilePath': scheduleFilePath})
	eprint('UI Sent RUN:')
	return jsonvalid({'success': True})

@app.route('/stopAtNextJob')
def stopAtNextJob():
	eprint('UI stopping at next job')
	pipes.send(share, 'QueueToDispatcher', {'type':'Stop', 'stop':'Dispatcher Job'})
	
	return jsonvalid({'success': True})

def getSubDirectories(directory):
		return [os.path.basename(os.path.dirname(g)) for g in glob.glob(directory + '/*/')]

@app.route('/scheduleNames.json')
def loadScheduleNames():
	scheduleNames = {}
	
	for userName in getSubDirectories(default_data_path):
		userDirectory = userName
		scheduleNames[userName] = {}
		for projectName in getSubDirectories(os.path.join(default_data_path, userDirectory)):
			projectDirectory = os.path.join(userDirectory, projectName)
			schedulePaths = glob.glob(os.path.join(default_data_path, userName, projectName, 'schedules/*.json'))
			scheduleNames[userName][projectName] = [os.path.basename(schedule).split('.')[0] for schedule in schedulePaths]
	
	return jsonvalid(scheduleNames)

@app.route('/AFMFilesInTimestampRange/<startTime>/<endTime>/associatedAFMs.json')
def AFMFilesInTimestampRange(startTime, endTime):
	from utilities import AFMReader
	
	startTime = float(startTime)
	endTime = float(endTime)
	
	avg_timestamp = startTime + (endTime - startTime)/2
	
	image_path = AFMReader.bestMatchAFMRegistry(default_data_path, targetTimestamp=avg_timestamp)
	
	if (image_path is not None):
		metaData = AFMReader.getAFMMetaData(image_path)
		
		return jsonvalid({'bestMatch':{**metaData, 'image_path':image_path}})
	
	return jsonvalid({})

@app.route('/addToNote', methods=['POST'])
def addToNote():
	experiment = flask.request.get_json(force=True)
	experimentNumber = experiment['startIndexes']['experimentNumber']
	noteAddition = experiment['noteAddition']
	path = dlu.getExperimentDirectory(experiment, experimentNumber)
	
	dlu.appendTextToFile(path, 'Note.txt', noteAddition)
	
	return jsonvalid({'success': True})


@app.route('/addToCorrection', methods=['POST'])
def addToCorrection():	
	folder = os.path.join(default_data_path, user, project, wafer, chip, device, 'Ex' + experimentNumber)
	
	correction = flask.request.get_json(force=True)

@app.route('/paths.json')
def paths():
	sourceAbsPath = os.path.abspath(os.path.dirname(__file__))
	
	return jsonvalid({'sourceAbsPath': sourceAbsPath})

@app.route('/saveCSV/<user>/<project>/<wafer>/<chip>/<device>/<experiment>/data.csv')
def saveCSV(user, project, wafer, chip, device, experiment):
	plotSettings = copy.deepcopy(default_makePlot_parameters)
	receivedPlotSettings = json.loads(flask.request.args.get('plotSettings'))
	#afmPath = json.loads(flask.request.args.get('afmPath'))
	plotSettings.update(receivedPlotSettings)
	
	path = os.path.join(default_data_path, user, project, wafer, chip, device, 'Ex' + experiment)
	fileNames = [os.path.basename(p) for p in glob.glob(os.path.join(path, '*.json'))]
	
	proxy = io.StringIO()
	
	deviceHistories = [dlu.loadJSON(path, fileName) for fileName in fileNames]
	dlu.saveCSV(deviceHistories, proxy)
	
	filebuf = io.BytesIO()
	filebuf.write(proxy.getvalue().encode('utf-8'))
	
	filebuf.seek(0)
	proxy.close()
	
	return flask.send_file(filebuf, attachment_filename='data.csv')

@app.route('/updateAFMRegistry')
def updateAFMRegistry():
	from utilities import AFMReader
	
	AFMReader.updateAFMRegistry(default_data_path)
	
	return jsonvalid({'success':True})


@app.route('/getJSONData/<user>/<project>/<wafer>/<chip>/<device>/<experiment>/data.json')
def getJSONData(user, project, wafer, chip, device, experiment):
	plotSettings = copy.deepcopy(default_makePlot_parameters)
	receivedPlotSettings = json.loads(flask.request.args.get('plotSettings'))
	#afmPath = json.loads(flask.request.args.get('afmPath'))
	plotSettings.update(receivedPlotSettings)
	
	path = os.path.join(default_data_path, user, project, wafer, chip, device, 'Ex' + experiment)
	
	deviceHistory = dlu.loadJSON(path, 'GateSweep.json')
	
	return jsonvalid(deviceHistory)

@app.route('/readme.md')
def getReadMe():
	with open('../README.md', 'r') as f:
		return f.read()


# Disable server side caching
@app.after_request
def add_header(response):
	response.cache_control.max_age = 0
	response.cache_control.no_store = True
	if 'Cache-Control' not in response.headers:
		response.headers['Cache-Control'] = 'no-store'
	return response


import socket

def findFirstOpenPort(startPort=1):
	for port in range(startPort, 8081):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
			try:
				print('Trying port {}'.format(port))
				sock.bind(('127.0.0.1', port))
				sock.close()
				return port
			except Exception as e:
				print('Port {} is not available'.format(port))

def managerMessageForwarder():
	global share
	
	while True:
		while pipes.poll(share, 'QueueToUI'):
			message = pipes.recv(share, 'QueueToUI')
			# message = share['QueueToUI'].get()
			socketio.emit('Server Message', message)
		
		socketio.sleep(0.01)

@socketio.on('my event')
def handle_my_custom_event(json):
	print('in my event, received json: ' + str(json))

managerMessageForwarderthread = None
@socketio.on('connect')
def connect():
	global managerMessageForwarderthread                                                               
	if managerMessageForwarderthread is None:
		managerMessageForwarderthread = socketio.start_background_task(target=managerMessageForwarder)
		pass

def launchBrowser(url):
	socketio.sleep(2)
	print('URL is "{}"'.format(url))
	webbrowser.open_new(url)

def makeShareGlobal(localShare):
	global share
	share = localShare

def start(share={}, debug=True, use_reloader=True):
	makeShareGlobal(share)
	
	if 'AutexysUIRunning' in os.environ:
		print('Reload detected. Not opening browser.')
		print('Still running on port {}'.format(os.environ['AutexysUIPort']))
		
	else:
		port = findFirstOpenPort(startPort=5000)
		print('Using port {}'.format(port))
		
		url = 'http://127.0.0.1:{}/ui/index.html'.format(port)
		
		os.environ['AutexysUIRunning'] = 'True'
		os.environ['AutexysUIPort'] = str(port)
		
		print('Opening browser...')
		socketio.start_background_task(launchBrowser, url)
	
	# app.run(debug=True, threaded=False, port=int(os.environ['AutexysUIPort']))
	socketio.run(app, debug=debug, port=int(os.environ['AutexysUIPort']), use_reloader=use_reloader)



if __name__ == '__main__':
	start()




