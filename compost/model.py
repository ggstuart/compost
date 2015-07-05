from pandas import Series, DataFrame
from compost import Dataset

class DailyAverageModel(object):
    def __init__(self, source_data, cumulative=False):
        data = Dataset(source_data, 60*60*24, cumulative).interpolate()
        source = data.measurements.diff().value[1:]
        self.result = source.mean()

    def prediction(self, index):
        return Series(self.result, index=index)

class WeekdayAverageModel(object):
    def __init__(self, source_data, cumulative=False):
        data = Dataset(source_data, 60*60*24, cumulative).interpolate()
        source = data.measurements.diff().value[1:].groupby(data.measurements[1:].index.weekday)
        self.parameters = source.mean()

    def prediction(self, index):
        return DataFrame(index=index).join(self.parameters, on=index.weekday).value


class MonthlyAverageModel(object):
    def __init__(self, source_data, cumulative=False):
        data = Dataset(source_data, 60*60*24, cumulative).interpolate()
        source = data.measurements.diff().value[1:].groupby(data.measurements[1:].index.month)
        self.parameters = source.mean()

    def prediction(self, index):
        return DataFrame(index=index).join(self.parameters, on=index.month).value
