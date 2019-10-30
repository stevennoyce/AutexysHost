from pandas._libs import json
import time

# === Static Variables ===
def activePlots():
    return activePlots.counter
activePlots.counter = 1

def incrementActivePlots():
    activePlots.counter += 1

def startTime():
    if(startTime.timestamp == None):
        startTime.timestamp = time.time()
    return startTime.timestamp
startTime.timestamp = None



# === Factory Functions ===
def createDataSeries(plotID, labels=[], xValues=[], yValues=[], xAxisTitle='', yAxisTitle='', yscale='log', enumerateLegend=False, timeseries=False):
    # Add numbers to series labels based on the current number of active plots
    if(enumerateLegend):
        for i in range(len(labels)):
            labels[i] = labels[i] + ' {:}'.format(activePlots())
    
    # Adjust time-series data so it starts at t = 0
    if(timeseries):
        for i in range(len(xValues)):
            xValues[i] = xValues[i] - startTime()
    
    # Create a series-data-point for each series
    seriesList = []
    for i in range(min(len(labels), len(xValues), len(yValues))):
        seriesList.append(Live_Plot_Series_Data_Point(labels[i], xValues[i], yValues[i]))
    
    return Live_Plot_Data_Point(plotID, xAxisTitle, yAxisTitle, yscale, seriesList)
 
def createDataPoint(plotID, label, xValue, yValue, xAxisTitle='', yAxisTitle='', yscale='log', enumerateLegend=False, timeseries=False):
    return createDataSeries(plotID, labels=[label], xValues=[xValue], yValues=[yValue], xAxisTitle=xAxisTitle, yAxisTitle=yAxisTitle, yscale=yscale, enumerateLegend=enumerateLegend, timeseries=timeseries)



# === Classes ===
class Live_Plot_Data_Point:
    '''
    Data collected in a single iteration of a procedure, formatted so it can be sent to the web frontend.
    Represents a single live plot.
    '''
    def __init__(self, plotID, xAxisTitle, yAxisTitle, yScale, seriesList):
        self.plotID = plotID
        self.xAxisTitle = xAxisTitle
        self.yAxisTitle = yAxisTitle
        self.yScale = yScale
        self.seriesList = seriesList # list of Live_Plot_Series_Data_Points

    def toDict(self):
        '''
        Call before sending to web frontend. Includes checking for unset fields.
        '''

        dict = {
            'plotID': self.plotID,
            'xAxisTitle': self.xAxisTitle,
            'yAxisTitle': self.yAxisTitle,
            'yScale': self.yScale,
            'seriesList': [series.toDict() for series in self.seriesList]
        }

        for k, v in dict.items():
            if v == None:
                raise Exception("Cannot convert data to dictionary. The ", k, " field was never set.")
        return dict
        


class Live_Plot_Series_Data_Point:
    '''
    Data collected in a single iteration of a procedure, but just for
     a single series, formatted so it can be sent to the web frontend.
    '''
    def __init__(self, seriesName, xData, yData):
        self.seriesName = seriesName
        self.xData = xData
        self.yData = yData

    def toDict(self):
        dict = {
            'seriesName': self.seriesName,
            'xData': self.xData,
            'yData': self.yData
        }

        for (k, v) in dict.items():
            if v == None:
                raise Exception("Cannot convert data to dictionary. The ", k, " field was never set.")
        return dict