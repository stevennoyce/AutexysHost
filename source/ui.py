import io
import os
import sys
import glob
import flask
import json
import copy
import time
import webbrowser
from matplotlib import pyplot as plt
import defaults
from procedures import Device_History as DH
from utilities import DataLoggerUtility as dlu

if __name__ == '__main__':
	os.chdir(sys.path[0])
	
	pathParents = os.getcwd().split('/')
	if 'AutexysHost' in pathParents:
		os.chdir(os.path.join(os.path.abspath(os.sep), *pathParents[0:pathParents.index('AutexysHost')+1], 'source'))


# Globals
pipeToManager = None

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)


from collections import Mapping, Sequence

def replaceInfNan(obj):
	if isinstance(obj, float):
		if obj == float('nan'):
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


app = flask.Flask(__name__, static_url_path='', static_folder='ui')

@app.route('/')
def root():
	return flask.redirect('/ui/index.html')

@app.route('/ui/<path:path>')
def sendStatic(path):
	return flask.send_from_directory('ui', path)

default_makePlot_parameters = {
	'startExperimentNumber': None,
	'endExperimentNumber': None,
	'specificPlot': '',
	'figureSize': None,
	'dataFolder': None,
	'saveFolder': None,
	'plotSaveName': '',
	'saveFigures': False,
	'showFigures': True,
	'sweepDirection': 'both',
	'plotInRealTime': True,
	'startRelativeIndex': 0,
	'endRelativeIndex': 1e10,
	'plot_mode_parameters': None
}

default_data_path = '../../AutexysData/'

@app.route('/plots/<user>/<project>/<wafer>/<chip>/<device>/<experiment>/<plotType>')
def sendPlot(user, project, wafer, chip, device, experiment, plotType):
	experiment = int(experiment)
	
	plotSettings = copy.deepcopy(default_makePlot_parameters)
	receivedPlotSettings = json.loads(flask.request.args.get('plotSettings'))
	plotSettings.update(receivedPlotSettings)
	
	filebuf = io.BytesIO()
	
	if plotSettings['startExperimentNumber'] == None:
		plotSettings['startExperimentNumber'] = experiment
	
	if plotSettings['endExperimentNumber'] == None:
		plotSettings['endExperimentNumber'] = experiment
	
	plotSettings['plotSaveName'] = filebuf
	plotSettings['saveFigures'] = True
	plotSettings['showFigures'] = False
	plotSettings['specificPlot'] = plotType
	
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
	# modificationTimes = [os.path.getmtime(p) for p in paths]
	modificationTimes = [os.path.getmtime(p+'ParametersHistory.json') if os.path.exists(p+'ParametersHistory.json') else os.path.getmtime(p) for p in paths]
	# sizes = [os.path.getsize(p) for p in paths]
	sizes = [os.path.getsize(p+'ParametersHistory.json') if os.path.exists(p+'ParametersHistory.json') else os.path.getsize(p) for p in paths]
	
	indexObjects = [dlu.loadJSONIndex(p) for p in paths]
	indexCounts = [i['index'] for i in indexObjects]
	experimentCounts = [i['experimentNumber'] for i in indexObjects]
	
	devices = [{'name': n, 'path': p, 'modificationTime': m, 'size': s, 'indexCount': ic, 'experimentCount': ec} for n, p, m, s, ic, ec in zip(names, paths, modificationTimes, sizes, indexCounts, experimentCounts)]
	
	return jsonvalid(devices)

@app.route('/<user>/<project>/<wafer>/<chip>/<device>/experiments.json')
def experiments(user, project, wafer, chip, device):
	folder = os.path.join(default_data_path, user, project, wafer, chip, device)
	files = glob.glob(folder + '*.json')
	fileNames = [os.path.basename(f) for f in files]
	
	parameters = dlu.loadJSON(folder, 'ParametersHistory.json')
	parameter_identifiers = {'dataFolder':default_data_path, 'Identifiers':{'user':user,'project':project,'wafer':wafer,'chip':chip,'device':device}}
	
	for i in range(len(parameters)):
		possiblePlots = DH.plotsForExperiments(parameter_identifiers, minExperiment=parameters[i]['startIndexes']['experimentNumber'], maxExperiment=parameters[i]['startIndexes']['experimentNumber'])
		parameters[i]['possiblePlots'] = possiblePlots
	
	# experiments = [{'name': n, 'path': p, 'modificationTime': m, 'size': s} for n, p, m, s in zip(names, paths, modificationTimes, sizes)]
	
	return jsonvalid(parameters)
	
	# return flask.Response(jsonvalid(parameters, allow_nan=False), mimetype='application/json')

@app.route('/parametersDescription.json')
def parametersDescription():
	# return flask.jsonify(defaults.default_parameters_description)
	return jsonvalid(defaults.default_parameters)

@app.route('/defaultParameters.json')
def defaultParameters():
	return jsonvalid(defaults.get())

@app.route('/saveSchedule/<user>/<project>/<fileName>', methods=['POST'])
def saveSchedule(user, project, fileName):
	# receivedJobs = json.loads(flask.request.args.get('jobs'))
	receivedJobs = flask.request.get_json(force=True)
	
	# with open(os.path.join(default_data_path, user, project, 'schedules/', fileName + '.json'), 'w') as f:
	# 	f.write(json.dumps(receivedJobs))
	
	dlu.emptyFile(os.path.join(default_data_path, user, project, 'schedules/'), fileName)
	for job in receivedJobs:
		dlu.saveJSON(os.path.join(default_data_path, user, project, 'schedules/'), fileName, defaults.extractDefaults(job), incrementIndex=False)
	
	return jsonvalid({'success':True})

@app.route('/scheduleFiles/<user>/<project>/<fileName>.json')
def loadSchedule(user, project, fileName):
	scheduleData = dlu.loadJSON(os.path.join(default_data_path, user, project, 'schedules/'), fileName + '.json')
	
	expandedScheduleData = []
	for job in scheduleData:
		expandedScheduleData.append(defaults.full_with_added(job))
	
	return jsonvalid(expandedScheduleData)

def getSubDirectories(directory):
	return [os.path.basename(os.path.dirname(g)) for g in glob.glob(directory + '/*/')]

@app.route('/dispatchSchedule/<user>/<project>/<fileName>.json')
def dispatchSchedule(user, project, fileName):
	scheduleFilePath = os.path.join(default_data_path, user, project, 'schedules', fileName + '.json')
	eprint('UI Sending RUN:')
	pipeToManager.send('RUN: ' + scheduleFilePath)
	eprint('UI Sent RUN:')
	return jsonvalid({'success': True})

@app.route('/stopAtNextJob')
def stopAtNextJob():
	eprint('UI stopping at next job')
	pipeToManager.send('STOP')
	
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

# @app.after_request
# def add_header(response):
# 	# response.cache_control.max_age = 300
#	# response.cache_control.no_store = True
#	# if 'Cache-Control' not in response.headers:
#		# response.headers['Cache-Control'] = 'no-store'
#	return response


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


def start(managerPipe=None):
	global pipeToManager
	pipeToManager = managerPipe
	
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
		webbrowser.open_new(url)
	
	app.run(debug=True, threaded=False, port=int(os.environ['AutexysUIPort']))


if __name__ == '__main__':
	start()




