from pandas._libs import json
import time

# === Static Variables ===
# Track the number of different traces on a plot created with the factory functions below
def activePlots():
    return activePlots.counter
activePlots.counter = 1

def incrementActivePlots():
    activePlots.counter += 1

# Track the start time of a plot created with the factory functions below
def startTime():
    if(startTime.timestamp == None):
        startTime.timestamp = time.time()
    return startTime.timestamp
startTime.timestamp = None



# === Factory Functions ===
def createDataSeries(plotID, labels=[], xValues=[], yValues=[], xAxisTitle='', yAxisTitle='', yscale='log', plotMode='lines', enumerateLegend=False, timeseries=False):
    # Add numbers to series labels based on the current number of active plots
    if(enumerateLegend):
        for i in range(len(labels)):
            labels[i] = labels[i] + ' {:}'.format(activePlots())
    
    # Adjust time-series data so it starts at t = 0
    if(timeseries):
        for i in range(len(xValues)):
            xValues[i] = xValues[i] - startTime()
    
    # Create a Live_Plot_Trace for each index of the labels/xValues/yValues arrays
    traces = {}
    for i in range(min(len(labels), len(xValues), len(yValues))):
        traces[labels[i]] = Live_Plot_Trace(labels[i], xValues[i], yValues[i])
    
    return Live_Plot_Figure(plotID, xAxisTitle, yAxisTitle, yscale, plotMode, traces)
 
def createDataPoint(plotID, label, xValue, yValue, xAxisTitle='', yAxisTitle='', yscale='log', enumerateLegend=False, timeseries=False):
    return createDataSeries(plotID, labels=[label], xValues=[xValue], yValues=[yValue], xAxisTitle=xAxisTitle, yAxisTitle=yAxisTitle, yscale=yscale, enumerateLegend=enumerateLegend, timeseries=timeseries)



# === Classes ===
class Live_Plot_Figure:
    '''
    Data collected in a single iteration of a procedure, formatted so it can be sent to the web frontend.
    Represents a single live plot.
    '''
    def __init__(self, plotID, xAxisTitle, yAxisTitle, yScale, plotMode, traces):
        self.plotID = plotID
        self.xAxisTitle = xAxisTitle
        self.yAxisTitle = yAxisTitle
        self.yScale = yScale
        self.plotMode = plotMode
        self.traces = traces # list of Live_Plot_Traces

    def toDict(self):
        '''
        Call before sending to web frontend. Includes checking for unset fields.
        '''

        result = {
            'plotID': self.plotID,
            'xAxisTitle': self.xAxisTitle,
            'yAxisTitle': self.yAxisTitle,
            'yScale': self.yScale,
            'plotMode': self.plotMode,
            'traces': {},
        }
        
        for traceID, trace in self.traces.items():
            result['traces'][traceID] = trace.toDict()

        for k, v in result.items():
            if v == None:
                raise Exception("Cannot convert data to dictionary. The ", k, " field was never set.")
        return result
        


class Live_Plot_Trace:
    '''
    Data collected in a single iteration of a procedure, but just for
     a single series, formatted so it can be sent to the web frontend.
    '''
    def __init__(self, traceID, xData, yData):
        self.traceID = traceID
        self.xData = xData
        self.yData = yData

    def toDict(self):
        result = {
            'traceID': self.traceID,
            'xData': self.xData,
            'yData': self.yData
        }

        for (k, v) in result.items():
            if v == None:
                raise Exception("Cannot convert data to dictionary. The ", k, " field was never set.")
        return result