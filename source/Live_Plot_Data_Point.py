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



# === External API (Factory Function) ===
def createLiveDataPoint(plotID, labels=[], xValues=[], yValues=[], colors=[], xAxisTitle='', yAxisTitle='', yscale='linear', plotMode='lines', enumerateLegend=False, timeseries=False):
    """ This function should be called by external classes to build a Live_Plot_Figure with the appropriate properties.
    NOTE: 'labels', 'xValues', 'yValues', and 'colors' are all arrays where each element represents a DIFFERENT trace, not
    mulitple points on the same trace. """
    
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
        traces[labels[i]] = Live_Plot_Trace(labels[i], xValues[i], yValues[i], colors[i] if(i < len(colors)) else '') 
    
    return Live_Plot_Figure(plotID, xAxisTitle, yAxisTitle, yscale, plotMode, traces)
 


# === Classes ===
class Live_Plot_Figure:
    '''
    Data collected in a single iteration of a procedure, formatted so it can be sent to the web frontend.
    Represents a single live plot.
    '''
    def __init__(self, plotID, xAxisTitle='', yAxisTitle='', yScale='linear', plotMode='lines', traces={}):
        self.plotID = plotID
        self.xAxisTitle = xAxisTitle
        self.yAxisTitle = yAxisTitle
        self.yScale = yScale
        self.plotMode = plotMode
        self.color = ''
        self.traces = traces # dictionary of Live_Plot_Traces

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
            'color': self.color,
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
    def __init__(self, traceID, xData, yData, color='', mode=''):
        self.traceID = traceID
        self.xData = xData
        self.yData = yData
        self.color = color
        self.mode = mode

    def toDict(self):
        result = {
            'traceID': self.traceID,
            'xData': self.xData,
            'yData': self.yData,
            'color': self.color,
            'mode': self.mode,
        }

        for (k, v) in result.items():
            if v == None:
                raise Exception("Cannot convert data to dictionary. The ", k, " field was never set.")
        return result