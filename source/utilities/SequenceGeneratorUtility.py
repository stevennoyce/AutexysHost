import numpy as np

def constValues(value, points):
	return (int(points)*[value])

def rampValues(start, end, points):
	return np.linspace(start, end, points).tolist()

def sweepValues(start, end, points):
	data = rampValues(start, end, points/2)
	return [data, list(reversed(data))]

def stepValues(start, end, increments, pointsPerRamp, pointsPerHold):
	if(increments == 0):
		return rampValues(start, end, pointsPerRamp)
		
	data = rampValues(start, end/increments, pointsPerRamp)
	data += constValues(end/increments, pointsPerHold)
	for i in range(1, increments):
		data += rampValues(i*end/increments, (i+1)*end/increments, pointsPerRamp)
		data += constValues((i+1)*end/increments, pointsPerHold)
	return data

def alternatingSweepValues(maximum, points):
	positives = sweepValues(0, maximum, points/2)
	positives = positives[0] + positives[1]
	negatives = sweepValues(0, -maximum, points/2)
	negatives = negatives[0] + negatives[1]
	data = positives + negatives
	data[::2] = positives
	data[1::2] = negatives
	return [data[1:int(len(data)/2)], data[int(len(data)/2):-1]]

def rampValuesWithDuplicates(start, end, points, duplicates):
	data = np.linspace(start, end, points/duplicates).tolist()
	return sorted(duplicates*data)

def sweepValuesWithDuplicates(start, end, points, duplicates):
	data = rampValuesWithDuplicates(start, end, points/2, duplicates)
	return [data, list(reversed(data))]

def alternatingSweepValuesWithDuplicates(maximum, points, duplicates):
	data = alternatingSweepValues(maximum, points/duplicates)
	duplicated_lists = [data[0] + data[1]] * duplicates
	data = (data[0] + data[1]) * duplicates
	for d in range(duplicates):
		data[d::duplicates] = duplicated_lists[d]
	return [data[:int(len(data)/2)], data[int(len(data)/2):]]


