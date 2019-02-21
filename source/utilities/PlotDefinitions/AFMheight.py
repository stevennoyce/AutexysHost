from utilities.MatplotlibUtility import *
from procedures import AFM_Control as afm_ctrl
from utilities import AFMReader as afm_reader

import time
import numpy as np

plotDescription = {
	'plotCategory': 'device',
	'priority': 530,
	'dataFileDependencies': ['AFMControl.json'],
	'plotDefaults': {
		'figsize':(4,3),
		'colorMap':'plasma'
	},
}

from utilities.PlotDefinitions import AFMdeviationsImage

def plot(deviceHistory, identifiers, mode_parameters=None):
	return AFMdeviationsImage.plot(deviceHistory, identifiers, mode_parameters, 
		showBackgroundAFMImage=True,
		showSMUData=False,
		interpolateNans=True,
	)

if(__name__=='__main__'):
	pass
