from .dataset import Dataset
from .model import DailyAverageModel

class SavingCalculation(object):
    """calculate savings between two periods based on a simple consumption model"""

    def __init__(self, measurements, test_period, baseline, cumulative):
        d = Dataset(measurements, 60*60*24, cumulative).interpolate()
        df = d.data
        self.data = df
        self.baseline_data = df[(df.index<=baseline.end_date) & (df.index>=baseline.start_date)]
        self.test_data = df[(df.index<=test_period.end_date) & (df.index>=test_period.start_date)]
        self.baseline_model = DailyAverageModel(self.baseline_data, False)

    def model(self):
        return self.baseline_model.prediction(self.baseline_data.index)

    def prediction(self):
        return self.baseline_model.prediction(self.test_data.index)

    def savings(self):
        return self.prediction() - self.test_data['value']
