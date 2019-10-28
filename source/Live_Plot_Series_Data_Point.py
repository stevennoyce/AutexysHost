
'''
Data collected in a single iteration of a procedure, but just for
 a single series, formatted so it can be sent to the web frontend.
'''
class Live_Plot_Series_Data_Point:
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