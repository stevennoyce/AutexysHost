"""A utility that generates sequences of numbers that represent a particular voltage waveform."""

import numpy as np
import math

# Generates a sequence of constant values.
def constValues(value, points):
	return (int(points)*[value])

# Generages a sequence that linearly ramps from start to end.
def rampValues(start, end, points):
	return np.linspace(start, end, points).tolist()

# Generates a sequence that linearly ramps from start to end, and back to start.
def sweepValues(start, end, points):
	data = rampValues(start, end, points/2)
	return [data, list(reversed(data))]

# Generates a sequence of discrete steps from start to end. The steps are not necessarily abrupt but instead consist of a ramp and hold.
def stepValues(start, end, increments, pointsPerRamp, pointsPerHold):
	if(increments == 0):
		return rampValues(start, end, pointsPerRamp)
		
	data = rampValues(start, end/increments, pointsPerRamp)
	data += constValues(end/increments, pointsPerHold)
	for i in range(1, increments):
		data += rampValues(i*end/increments, (i+1)*end/increments, pointsPerRamp)
		data += constValues((i+1)*end/increments, pointsPerHold)
	return data

# Generates a sequence that transitions sinusoidally from start to end. 
def sineValues(start, end, points):
	amplitude = (end - start)/2
	sequence = [start + amplitude*(1 - math.cos(x * math.pi / (points-1))) for x in range(points)]
	return sequence

# Generates a sequence that alternates every other point between a linear ramp from 0 to maximum and a linear ramp from 0 to -maximum.
def alternatingSweepValues(maximum, points):
	positives = sweepValues(0, maximum, points/2)
	positives = positives[0] + positives[1]
	negatives = sweepValues(0, -maximum, points/2)
	negatives = negatives[0] + negatives[1]
	data = positives + negatives
	data[::2] = positives
	data[1::2] = negatives
	return [data[1:int(len(data)/2)], data[int(len(data)/2):-1]]

# Generates a sequence that linearly ramps from start to end. 
# Every point is duplicated "duplicates" number of times.
def rampValuesWithDuplicates(start, end, points, duplicates):
	data = np.linspace(start, end, points/duplicates).tolist()
	return sorted(duplicates*data)
	
# Generates a sequence that linearly ramps from start to end, and back to start. 
# Every point is duplicated "duplicates" number of times.
def sweepValuesWithDuplicates(start, end, points, duplicates, ramps=2):
	data = rampValuesWithDuplicates(start, end, points/2, duplicates)
	if(ramps == 1):
		return [data]
	elif(ramps == 2):
		return [data, list(reversed(data))]
	else:
		values = []
		for i in range(ramps):
			values.append(data)
			data = list(reversed(data))
		return values
	
# Generates a sequence that alternates every other point between a linear ramp from 0 to maximum and a linear ramp from 0 to -maximum.
# Every point is duplicated "duplicates" number of times.	
def alternatingSweepValuesWithDuplicates(maximum, points, duplicates):
	data = alternatingSweepValues(maximum, points/duplicates)
	duplicated_lists = [data[0] + data[1]] * duplicates
	data = (data[0] + data[1]) * duplicates
	for d in range(duplicates):
		data[d::duplicates] = duplicated_lists[d]
	return [data[:int(len(data)/2)], data[int(len(data)/2):]]

# Generate a sequence shaped like a waveform where values is a list of values to reach and points is a list of transition lengths between values.
# The sequence will add more points in the transitions so that the difference between two points <= maxStep.
def waveformValues(waveform, values, points, maxStep):
	if(waveform == 'square'):
		return squareWaveValues(values, points, maxStep)
	elif(waveform == 'triangle'):
		return triangleWaveValues(values, points, maxStep)
	elif(waveform == 'sine'):
		return sineWaveValues(values, points, maxStep)
	else:
		raise NotImplementedError('Unknown waveform: "' + str(waveform) + '"')

# Generate a sequence shaped like a square wave, where values is a list of step heights and points is a list of plateau lengths.
# The sequence will add more points in the transitions between squares so that the difference between two points <= maxStep.
def squareWaveValues(values, points, maxStep):
	sequence = []
	for i in range(min(len(values), len(points))):
		segment = constValues(values[i], points[i])
		if((i > 0) and (maxStep > 0) and (abs(values[i] - values[i-1]) > maxStep)):
			bridge = np.linspace(values[i-1], values[i], max(3, math.ceil(abs(values[i] - values[i-1])/maxStep)+1))
			bridge = bridge[1:-1]
			sequence.extend(bridge)
		sequence.extend(segment)
	return sequence
	
# Generate a sequence shaped like a triangle wave, where values is a list of peak heights and points is a list of ramp lengths.
# The sequence will add more points in the transitions between peaks so that the difference between two points <= maxStep.
def triangleWaveValues(values, points, maxStep):
	sequence = []
	for i in range(min(len(values) - 1, len(points))):
		segment = rampValues(values[i], values[i+1], max(2, points[i]))
		if(abs(segment[0] - segment[1]) > maxStep):
			segment = np.linspace(values[i], values[i+1], max(3, math.ceil(abs(values[i] - values[i+1])/maxStep)+1))
		
		if(i > 0):
			sequence.extend(segment[1:])
		else:
			sequence.extend(segment)
	return sequence
		
# Generate a sequence shaped like a sine wave, where values is a list of peak heights and points is a list of curve lengths.
# The sequence will add more points in the transitions between peaks so that the difference between two points <= maxStep.				
def sineWaveValues(values, points, maxStep):
	sequence = []
	for i in range(min(len(values) - 1, len(points))):
		segment = sineValues(values[i], values[i+1], max(2, points[i]))
		max_difference = max([abs(segment[i] - segment[i+1]) for i in range(len(segment) - 1)])
		while(max_difference > maxStep):
			# This scheme was chosen to try to converge quickly on a number of points that works without being excessive
			points[i] = math.ceil((points[i]+1)*max_difference/maxStep)
			segment = sineValues(values[i], values[i+1], max(2, points[i]))
			max_difference = max([abs(segment[i] - segment[i+1]) for i in range(len(segment) - 1)])
		sequence.extend(segment)
	return sequence
	
		
	

