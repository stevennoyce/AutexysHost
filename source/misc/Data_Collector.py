from matplotlib import pyplot as plt
import numpy as np
import os

from utilities import DataLoggerUtility as dlu
import defaults



allDevices = ["1-2", "2-3", "3-4", "4-5", "5-6", "6-7", "7-8", "8-9", "9-10", "10-11", "11-12", "12-13", "14-15", "15-16", "16-17", "17-18", "18-19", "19-20", "21-22", "22-23", "23-24", "24-25", "25-26", "26-27", "27-28", "28-29", "29-30", "30-31", "31-32", "32-33", "34-35", "35-36", "36-37", "37-38", "38-39", "39-40", "40-41", "41-42", "42-43", "43-44", "44-45", "45-46", "47-48", "48-49", "49-50", "50-51", "51-52", "52-53", "54-55", "55-56", "56-57", "57-58", "58-59", "59-60", "60-61", "61-62", "62-63", "63-64", "64-65", "65-66"]
smallDevices = ["1-2", "4-5", "7-8", "10-11", "14-15", "17-18", "21-22", "24-25", "27-28", "30-31", "36-37", "39-40", "42-43", "45-46", "49-50", "52-53", "56-57", "59-60", "62-63", "65-66"]
mediumDevices = ["2-3", "5-6", "8-9", "11-12", "15-16", "18-19", "22-23", "25-26", "28-29", "31-32", "35-36", "38-39", "41-42", "44-45", "48-49", "51-52", "55-56", "58-59", "61-62", "64-65"]
largeDevices = ["3-4", "6-7", "9-10", "12-13", "16-17", "19-20", "23-24", "26-27", "29-30", "32-33", "34-35", "37-38", "40-41", "43-44", "47-48", "50-51", "54-55", "57-58", "60-61", "63-64"]

experiment_num = 1 # Experiment number to output CSV for

direction = 0 # forward (0) or reverse (1) sweep direction for data selection

Lower_Bound = 0 # Lower bound in data set of linear fit for transconductance
Upper_Bound = 20 # Upper bound in data set of linear fit for transconductance

# === External API ===

# Loads data from multiple devices into a map
# directory - string filepath to device folders
# devicelist - list of string device names to load data from.  Must match device folder names
# loadFileName - string name of a data file to load from all devices (Ex. GateSweep.json)
def loadDevices(directory, deviceList, loadFileName):
	data_out = dict()
	for device in deviceList:
		currentpath = os.path.join(directory, device)
		if(os.path.exists(os.path.join(currentpath, loadFileName))):
			data_out[device] = dlu.loadJSON(currentpath, loadFileName)
	return data_out

# Writes data to a CSV file for use in Excel
# directory - string filepath of folder to save into
# data - List of string lines for CSV file
# saveFileName - string name of file to write to
def saveToCSV(directory, data, saveFileName):
	file = open(os.path.join(directory, saveFileName), "w+")
	file.writelines(data)
	file.close()

# === Internal API ===

def linearFit(x, y):
	slope, intercept = np.polyfit(x, y, 1)
	fitted_data = [slope*x[i] + intercept for i in range(len(x))]
	return {'fitted_data': fitted_data,'slope':slope, 'intercept':intercept}

def saveFitPlot(vgs_data, id_data, fit, filename):
	plt.clf()
	plt.plot(vgs_data, id_data, 'b.', vgs_data[Lower_Bound:Upper_Bound], fit['fitted_data'], 'r.')
	plt.xlabel("$V_{GS}$ (V)")
	plt.ylabel("$I_{D}$ (A)")
	plt.title("Transfer Curve and Fit")
	plt.figlegend(['Measured Values', 'Fitted Model'])
	plt.savefig(filename)


# Import data from all devices
filepath = "data/Nathaniel/JoeyData/180829S1/R2C2"
allData = loadDevices(filepath, allDevices, "GateSweep.json")

# Extract transconductance and threshold voltages
VT_vals = dict()
gm_vals = dict()
for key, value in allData.items():
	VT_vals[key] = list()
	gm_vals[key] = list()
	for data in value:
		id_data = data['Results']['id_data'][direction]
		vgs_data = data['Results']['vgs_data'][direction]
		fit = linearFit(vgs_data[Lower_Bound:Upper_Bound], id_data[Lower_Bound:Upper_Bound])
		VT_vals[key].append(fit['intercept'] / fit['slope'])
		gm_vals[key].append(fit['slope'])
		saveFitPlot(vgs_data, id_data, fit, os.path.join(filepath, "Transfer_Curve_" + key + "_" + str(len(VT_vals[key]))))

# Put transconductance and threshold voltages in table
small_output = ["device, VT, gm\n"]
for device in smallDevices:
	if device in VT_vals and len(VT_vals[device]) >= experiment_num:
		small_output.append(device + ", " + str(VT_vals[device][experiment_num - 1]) + ", " + str(gm_vals[device][experiment_num - 1]) + "\n")

medium_output = ["device, VT, gm\n"]
for device in mediumDevices:
	if device in VT_vals and len(VT_vals[device]) >= experiment_num:
		medium_output.append(device + ", " + str(VT_vals[device][experiment_num - 1]) + ", " + str(gm_vals[device][experiment_num - 1]) + "\n")

large_output = ["device, VT, gm\n"]
for device in largeDevices:
	if device in VT_vals and len(VT_vals[device]) >= experiment_num:
		large_output.append(device + ", " + str(VT_vals[device][experiment_num - 1]) + ", " + str(gm_vals[device][experiment_num - 1]) + "\n")

saveToCSV(filepath, small_output, "data_gmvt_small.csv")
saveToCSV(filepath, medium_output, "data_gmvt_medium.csv")
saveToCSV(filepath, large_output, "data_gmvt_large.csv")

# Put raw data in table
output = list()
output.append("vgs, " +  str(allData['1-2'][experiment_num - 1]['Results']['vgs_data'][direction]).replace('[', '').replace(']', '') + "\n")
for key in smallDevices:
	if key in allData and len(allData[key]) >= experiment_num:
		output.append(key + ", " +  str(allData[key][experiment_num - 1]['Results']['id_data'][direction]).replace('[', '').replace(']', '') + "\n")
saveToCSV(filepath, output, "raw_data_small.csv")
output.clear()

output.append("vgs, " +  str(allData['1-2'][experiment_num - 1]['Results']['vgs_data'][direction]).replace('[', '').replace(']', '') + "\n")
for key in mediumDevices:
	if key in allData and len(allData[key]) >= experiment_num:
		output.append(key + ", " +  str(allData[key][experiment_num - 1]['Results']['id_data'][direction]).replace('[', '').replace(']', '') + "\n")
saveToCSV(filepath, output, "raw_data_medium.csv")
output.clear()

output.append("vgs, " +  str(allData['1-2'][experiment_num - 1]['Results']['vgs_data'][direction]).replace('[', '').replace(']', '') + "\n")
for key in largeDevices:
	if key in allData and len(allData[key]) >= experiment_num:
		output.append(key + ", " +  str(allData[key][experiment_num - 1]['Results']['id_data'][direction]).replace('[', '').replace(']', '') + "\n")
saveToCSV(filepath, output, "raw_data_large.csv")
output.clear()

