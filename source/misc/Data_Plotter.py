from utilities import DataLoggerUtility as dlu
from utilities import DataPlotterUtility as dpu
from matplotlib import pyplot as plt
import defaults

# Chip Specifier
waferID = 'C139'
chipID = 'D'
deviceID = '1'

# Model Fit Specifier for Data Range
Transconductance_Lower_Bound = 0
Transconductance_Upper_Bound = 18

# Read data from file
allData = dlu.loadJSON('data0/' + waferID + '/' + chipID + '/' + deviceID + '/', 'GateSweep.json')

# Graph and calculate transconductance and threshold voltage
output = ['gm, VT\n']
for run_num in range(0, len(allData)):
	jsonData = allData[run_num]
	parameters = dict(defaults.default_parameters)
	id_data = jsonData['Results']['id_data'][0]
	vgs_data = jsonData['Results']['vgs_data'][0]
	fit = dpu.linearFit(vgs_data[Transconductance_Lower_Bound:Transconductance_Upper_Bound], id_data[Transconductance_Lower_Bound:Transconductance_Upper_Bound]);
	VT = fit['intercept'] / fit['slope']
	output.append(str(fit['slope']) + ', ' + str(VT) + "\n")
	plt.plot(vgs_data, id_data, 'b.', vgs_data[Transconductance_Lower_Bound:Transconductance_Upper_Bound], fit['fitted_data'], 'r.')
	plt.xlabel("$V_{GS}$ (V)")
	plt.ylabel("$I_{D}$ (A)")
	plt.title("Transfer Curve and Fit")
	plt.figlegend(['Measured Values', 'Fitted Model'])
	saveName = "CurrentPlots/" + waferID + "_" + chipID + "_" + deviceID + "_Run" + str(run_num) + "_Transfer_Curve"
	plt.savefig(saveName)
	plt.clf()

# Output data as CSV file
file = open("CurrentPlots/" + waferID + "_" + chipID + "_" + deviceID + "_Transconductance_Threshold.csv", "w+")
file.writelines(output)
file.close()


