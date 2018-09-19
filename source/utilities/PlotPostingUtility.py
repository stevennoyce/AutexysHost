import base64
import requests
import glob

def postPlots(parameters):
	print('When entering postPlots(), parameters is:')
	print(parameters)
	
	try:
		plotFileNames = glob.glob(parameters['postFolder'] + '*.png')
		
		for plotFileName in plotFileNames:
			with open(plotFileName, "rb") as plotFile:
				encodedImage = base64.b64encode(plotFile.read())
			
			postURL = 'https://script.google.com/macros/s/AKfycbzflDpYVTV3NGAEEaC-hfyQTN94JhZbr75dEh_czd7XXN5mDA/exec'
			# postURL = 'http://ptsv2.com/t/ly9tz-1525197812/post'
			
			postData = {}
			postData['parameters'] = parameters
			postData['encodedImage'] = encodedImage.decode()
			postData['imageName'] = plotFileName.split('.')[0]
			
			print('Posting plot to web service...')
			# response = requests.post(postURL, data = postData)
			response = requests.post(postURL, json = postData)
			
			print('Server response is: ')
			print(response)
			print(response.text)
	
	except Exception as e:
		print('Failed to post plots')
		print(repr(e))



if __name__ == '__main__':
	parameters = {
		'waferID': 'C127',
		'chipID': 'Fake',
		'deviceID': '8-9',
		'startIndexes': {'index': 1, 'ExperimentNumber': 5},
		'runType': 'AutoGateSweep',
		'postFolder': '../CurrentPlots/',
		'figuresSaved': ['../fig1.png'],
		'postFigures': True
	}
	
	postPlots(parameters)
	
	print('Complete')
