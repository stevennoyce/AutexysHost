from matplotlib import pyplot as plt
import numpy as np
from scipy import optimize

def fitBasicDeviceModel(deviceHistory, direction=0):
	"""Fits a basic device model using transconductance and threshold voltage to each experiment of the device given.
	Returns a list of transconductances, then a list of threshold voltages, and a list of r^2 values, one for each experiment passed in, as a tuple."""

	# Check Input
	if(len(deviceHistory) <= 0):
		print('No ' + str(plotType) + ' device history to plot.')
		return

	# Initialize Lists
	gm = list()
	vt = list()
	r2 = list()
	
	for exp in deviceHistory:
		try:
			vgs_data = exp['Results']['vgs_data'][direction]
			id_data = exp['Results']['id_data'][direction]

			# Apply Model
			params, covariance = optimize.curve_fit(basicDeviceModel, vgs_data, id_data)
			gm.append(params[0])
			vt.append(params[1])

			# Calculate r2 value
			sst = np.sum([(id_data[i] - np.average(id_data))**2 for i in range(len(vgs_data))])
			ssr = np.sum([(id_data[i] - basicDeviceModel(vgs_data, params[0], params[1])[i])**2 for i in range(len(vgs_data))])
			r2.append(1-ssr/sst)
		except RuntimeError:
			print("Error: Encounterd transfer curve that does not fit model")
			gm.append(0)
			vt.append(0)
			r2.append(0)

	return (gm, vt, r2)

def basicDeviceModel(vgs_data, gm, vt):
	"""Basic device model for a device using transconducance and threshold voltage.
	Returns model drain current data based on given Vgs data, transconductance, and threshold voltage."""
	return [(gm*vgs_val - gm*vt) if vgs_val < vt else 0 for vgs_val in vgs_data]