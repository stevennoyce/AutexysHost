from pandas._libs import json

from Live_Plot_Series_Data_Point import Live_Plot_Series_Data_Point

'''
Data collected in a single iteration of a procedure, formatted so it can be sent to the web frontend.
Represents a single live plot.
'''
class Live_Plot_Data_Point:
    def __init__(self, plotID, xAxisTitle, yAxisTitle, yScale, seriesList):
        self.plotID = plotID
        self.xAxisTitle = xAxisTitle
        self.yAxisTitle = yAxisTitle
        self.yScale = yScale
        self.seriesList = seriesList # list of Live_Plot_Series_Data_Points

    '''
    Call before sending to web frontend. Includes checking for unset fields.
    '''
    def toDict(self):
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

    '''
    Factory method particularly for Gate_Sweep and Drain_Sweep, but can be used elsewhere too.
    '''
    @staticmethod
    def createDefaultCurrentPlot(plotID, xAxisTitle, xValue, drainCurrent, gateCurrent, legendNumber):
        seriesList = [Live_Plot_Series_Data_Point('Drain Current {} [A]'.format(legendNumber + 1), xValue, drainCurrent), Live_Plot_Series_Data_Point('Gate Current {} [A]'.format(legendNumber + 1), xValue, gateCurrent)]
        return Live_Plot_Data_Point(plotID, xAxisTitle, 'Current [A]', 'log', seriesList)