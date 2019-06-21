# Author: Nathan Choe
# specifically for: AutoFlowStaticBias data

from utilities.MatplotlibUtility import *


plotDescription = {
	'plotCategory': 'device',
	'priority': 100,
	'dataFileDependencies': ['FlowStaticBias.json', 'GateSweep.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'colorMap':'plasma',
		'colorDefault': ['#1f77b4'],
		'color2Default': ['#009933'],
		'includeOriginOnYaxis':True,
		
		'xlabel':'$V_{{GS}}$ (V)',
		'ylabel':'Gate Maximum Difference (nA)',
		'y2label':'Noise (A)',
		'leg_vds_label':'$V_{{DS}}^{{Sweep}}$ = {:}V',
		'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V',
		'leg_vgs_change':'$V_{{GS}}^{{Incr}}$ = {:}V',
		'leg_data_min_x':'{:}V',
		'leg_data_max_x':'{:}V',
		'leg_data_min_y':'{:}',
		'leg_data_max_y':'{:}',
	},
}

def diff_list_abs(a, b):
	
	diff = []
	
	return abs(max(a) - max(b))
	
	'''
	for i in range(0, len(a)):
		diff.append(abs(a[i]-b[i]))
	return diff
	'''

def plot(deviceHistory, identifiers, mode_parameters=None):
	
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])

	
	# first, create separate arrays of gatesweeps and flowstaticbiases	
	all_gatesweeps = []
	all_flow = []
	for device in deviceHistory:
		
		if device["runType"] == "GateSweep":
			all_gatesweeps.append(device)
		elif device["runType"] == "FlowStaticBias":
			all_flow.append(device)
	
	# second, get flowstaticbias characteristics
	pumpPins = all_flow[0]["runConfigs"]["FlowStaticBias"]["pumpPins"]
	
	# Build Color Map and Color Bar
	#totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	#holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	#colors = setupColors(fig, len(all_flow), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0, colorMapEnd=0.87, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarAxisLabel='')
	colors_pins = setupColors(fig, len(all_flow), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0, colorMapEnd=0.87, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarAxisLabel='')
	#colors2 = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['color2Default'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.15, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')
	
	
	# go through all flowstaticbiases
	gateSweepCounter = 1 # ignore first test GateSweep
	flowCounter = 0
	
	max_total_diff = []
	max_total_diff_vgs = []
	for i in range(0, len(pumpPins)-1):
		max_total_diff.append(0)
		max_total_diff_vgs.append(0)
	for flow in all_flow:
		
		currentVgs = flow["runConfigs"]["FlowStaticBias"]["gateVoltageSetPoint"]
		
		control_front = all_gatesweeps[gateSweepCounter]["Results"]["id_data"][0]
		control_back = all_gatesweeps[gateSweepCounter]["Results"]["id_data"][1]
		gateSweepCounter += 1 # move onto next gatesweep, in next forloop
		for currentPin in range(0, len(pumpPins) - 1): # go through every possible control-X combinations
			pump_front = all_gatesweeps[gateSweepCounter]["Results"]["id_data"][0]
			pump_back = all_gatesweeps[gateSweepCounter]["Results"]["id_data"][1]
			
			list_abs_diff_front = diff_list_abs(control_front, pump_front)
			max_diff_front = (list_abs_diff_front)
			
			list_abs_diff_back = diff_list_abs(control_back, pump_back)
			max_diff_back = (list_abs_diff_back)
			
			tot = (max_diff_back + max_diff_front) / 2
			std = np.std([max_diff_front, max_diff_front])
			
			ax.plot([currentVgs], [tot * 1e9], color=colors_pins[flowCounter], linestyle=None, linewidth=0, marker='o', markersize=4)
			ax.errorbar([currentVgs], [tot * 1e9], yerr=std, color=colors_pins[flowCounter], linewidth=1, capsize=2, capthick=0.5, elinewidth=0.5)
			#ax.plot([currentVgs], [max_diff_back * 1e9], color=colors_pins[flowCounter], linestyle=None, linewidth=0, marker='o', markersize=4)
			gateSweepCounter += 1
			if tot > max_total_diff[currentPin]:
				max_total_diff[currentPin] = tot
				max_total_diff_vgs[currentPin] = currentVgs
		flowCounter += 1
	
	for i in max_total_diff_vgs:
		ax.axvline(x=i)
	
	includeOriginOnYaxis(ax, include=plotDescription['plotDefaults']['includeOriginOnYaxis'])
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=plotDescription['plotDefaults']['ylabel'])		
	
	return (fig, (ax,))