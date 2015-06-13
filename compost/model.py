from pandas import Series
from compost import Dataset

class DailyAverageModel(object):
    def __init__(self, source_data, cumulative=False):
        data = Dataset(source_data, 60*60*24, cumulative).interpolate()
        source = data.measurements.diff().value[1:]
        self.result = source.mean()

    def prediction(self, index):
        return Series(self.result, index=index)
