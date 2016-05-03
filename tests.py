import unittest
from datetime import timedelta, datetime
from random import randint, random
from pandas import DataFrame, date_range#, Index
from numpy import nan


from compost import Dataset, ShortDatasetError, SubMinuteTimestepError
from compost import SavingCalculation, DailyAverageModel


class TestDatasetCreation(unittest.TestCase):
    """tests for error states in constructor"""
    def setUp(self):
        index = date_range('1/1/2015', periods=365)
        self.df = DataFrame(list(range(len(index))), index=index, columns=['value'])

    def test_sub_minute(self):
        self.assertRaises(SubMinuteTimestepError, Dataset, self.df, 30, cumulative=False)

    def test_sub_minute_edge(self):
        self.assertRaises(SubMinuteTimestepError, Dataset, self.df, 59, cumulative=False)

    def test_sub_minute_negative(self):
        self.assertRaises(SubMinuteTimestepError, Dataset, self.df, -4, cumulative=False)

    def test_sub_minute_one_and_a_bit(self):
        self.assertRaises(SubMinuteTimestepError, Dataset, self.df, 64, cumulative=False)

    def test_minute_ok(self):
        try:
            Dataset(self.df, 60, cumulative=False)
        except SubMinuteTimestepError:
            self.fail("Dataset(df, 60) raised SubMinuteTimestepError!")


class TestPerfectData(unittest.TestCase):
    """what happens with nice data"""

    def setUp(self):
        index = date_range('1/1/2015', periods=365)
        self.df = DataFrame(list(range(len(index))), index=index, columns=['value'])
        self.dataset = Dataset(self.df, 60*60*24, cumulative=False)

    def test_validates(self):
        self.assertTrue(self.dataset.validate())

    def test_partial_validates(self):
        """cut the data up and it still works"""
        d = Dataset(self.df.head(100), 60*60*24, cumulative=False)
        self.assertTrue(d.validate())

    def test_short_raises(self):
        """single value datasets raise an error"""
        d = Dataset(self.df.head(1), 60*60*24, cumulative=False)
        self.assertRaises(ShortDatasetError, d.validate)

    def test_interpolate_skipped(self):
        d2 = self.dataset.interpolate()
        self.assertEqual(self.dataset, d2)


class InterpolatedDataTests(object):
    """common tests for data that needs work"""

    def test_validation_fails(self):
        self.assertFalse(self.dataset.validate())

    def test_interpolate_validates(self):
        d1 = self.dataset.interpolate()
        self.assertTrue(d1.validate())

    def test_interpolate_maintains_total(self):
        d1 = self.dataset.interpolate()
        self.assertEqual(self.dataset.total(), d1.total())


class TestLowResData(InterpolatedDataTests, unittest.TestCase):
    """what happens with e.g. weekly data"""
    def setUp(self):
        index = date_range('1/1/2015', periods=5, freq="7D")
        df = DataFrame(list(range(len(index))), index=index, columns=['value'])
        self.dataset = Dataset(df, 60*60*24, cumulative=False)
        super(TestLowResData, self).setUp()

class TestCumulativeLowResData(InterpolatedDataTests, unittest.TestCase):
    """what happens with e.g. weekly cumulative data"""
    def setUp(self):
        index = date_range('1/1/2015', periods=5, freq="7D")
        df = DataFrame(list(range(len(index))), index=index, columns=['value'])
        self.dataset = Dataset(df, 60*60*24, cumulative=True)
        super(TestCumulativeLowResData, self).setUp()

class TestMissingLowResData(InterpolatedDataTests, unittest.TestCase):
    """what happens when weekly data has missing values?"""

    def setUp(self):
        index = date_range('1/1/2015', periods=52, freq="7D")
        df = DataFrame(list(range(len(index))), index=index, columns=['value'])[index.month != 5]
        self.dataset = Dataset(df, 60*60*24, cumulative=False)
        super(TestMissingLowResData, self).setUp()

class TestMissingCumulativeLowResData(InterpolatedDataTests, unittest.TestCase):
    """what happens when cumulative weekly data has missing values?"""

    def setUp(self):
        index = date_range('1/1/2015', periods=52, freq="7D")
        df = DataFrame(list(range(len(index))), index=index, columns=['value'])[index.month != 5]
        self.dataset = Dataset(df, 60*60*24, cumulative=True)
        super(TestMissingCumulativeLowResData, self).setUp()


class TestHighResData(InterpolatedDataTests, unittest.TestCase):
    """what happens with e.g. 15-minutely data"""

    def setUp(self):
        index = date_range('1/1/2015', periods=4*24*365, freq="15Min")
        df = DataFrame(list(range(len(index))), index=index, columns=['value'])
        self.dataset = Dataset(df, 60*60*24, cumulative=False)
        super(TestHighResData, self).setUp()

class TestCumulativeHighResData(InterpolatedDataTests, unittest.TestCase):
    """what happens with e.g. 15-minutely cumulative data"""

    def setUp(self):
        index = date_range('1/1/2015', periods=4*24*365, freq="15Min")
        df = DataFrame(list(range(len(index))), index=index, columns=['value'])
        self.dataset = Dataset(df, 60*60*24, cumulative=True)
        super(TestCumulativeHighResData, self).setUp()

class TestMissingHighResData(InterpolatedDataTests, unittest.TestCase):
    """what happens when 15-minutely data has missing values?"""

    def setUp(self):
        index = date_range('1/1/2015', periods=4*24*365, freq="15Min")
        df = DataFrame(list(range(len(index))), index=index, columns=['value'])[index.day != 5]
        self.dataset = Dataset(df, 60*60*24, cumulative=False)
        super(TestMissingHighResData, self).setUp()

class TestMissingCumulativeHighResData(InterpolatedDataTests, unittest.TestCase):
    """what happens when cumulative 15-minutely data has missing values?"""

    def setUp(self):
        index = date_range('1/1/2015', periods=4*24*365, freq="15Min")
        df = DataFrame(list(range(len(index))), index=index, columns=['value'])[index.day != 5]
        self.dataset = Dataset(df, 60*60*24, cumulative=True)
        super(TestMissingCumulativeHighResData, self).setUp()


# class TestHighResWithMissingData(unittest.TestCase):
#     """what happens when 15-minutely data has missing values?"""
#
#     def setUp(self):
#         index = date_range('1/1/2015', periods=4*24*365, freq="15Min")
#         self.df = DataFrame(list(range(len(index))), index=index, columns=['value'])[index.day >= 3]
#         self.dataset1 = Dataset(self.df, 60*60*24)
#         self.dataset2 = Dataset(self.df, 60*60*24, cumulative=True)

    # def test_validation_fails(self):
    #     self.assertFalse(self.dataset1.validate())
    #
    # def test_interpolate_validates(self):
    #     d1 = self.dataset1.interpolate()
    #     d2 = self.dataset2.interpolate()
    #     self.assertTrue(d1.validate())
    #     self.assertTrue(d2.validate())
    #
    # def test_interpolate_maintains_total(self):
    #     # print(self.dataset1.measurements.head(5))
    #     d1 = self.dataset1.interpolate()
    #     # print(d1.measurements.head(5))
    #     d2 = self.dataset2.interpolate()
    #     self.assertEqual(self.dataset1.measurements.value.sum(), d1.measurements.value.sum())
    #     self.assertEqual(self.dataset2.measurements.diff().value.sum(), d2.measurements.diff().value.sum())

# class TestDatasetValidation(unittest.TestCase):
#
#     def setUp(self):
#         index = date_range('1/1/2015', periods=365)
#         self.df = DataFrame(list(range(365)), index=index, columns=['value'])
#
#     def test_missing(self):
#         d = Dataset(self.df[self.df.index.day != 1], 60*60*24)
#         self.assertFalse(d.validate())
#
#     def test_bad_resolution(self):
#         d = Dataset(self.df[self.df.index.day != 1], 60*60*12)
#         self.assertFalse(d.validate())
#
#
# class TestDatasetInterpolation(unittest.TestCase):
#
#     def setUp(self):
#         index = date_range('1/1/2015', periods=366)
#         self.df = DataFrame(list(range(366)), index=index, columns=['value'])
#
#
#     def test_low_resolution(self):
#         d1 = Dataset(self.df, 60*60*12)
#         d2 = d1.interpolate()
#         self.assertTrue(d2.validate())
#
#     def test_high_resolution(self):
#         d1 = Dataset(self.df, 60*60*48)
#         d2 = d1.interpolate()
#         self.assertTrue(d2.validate())
#
#     def test_high_resolution_cumulative(self):
#         d1 = Dataset(self.df, 60*60*48, cumulative=True)
#         d2 = d1.interpolate()
#         self.assertTrue(d2.validate())
#
#     def test_missing_data(self):
#         df = self.df[self.df.index.day != 5]    #cut out some data
#         d1 = Dataset(df, 60*60*48)
#         d2 = d1.interpolate()
#         self.assertTrue(d2.validate())
#
#     def test_randomised_index(self):
#         index = Index([i + timedelta(seconds=randint(-100,100)) for i in self.df.index])
#         self.df.index = index
#         d1 = Dataset(self.df, 60*60*48)
#         d2 = d1.normalise()
#         self.assertTrue(d2.validate())
#

class TestSavingCalculation(unittest.TestCase):
    def setUp(self):
        index = date_range('1/1/2015', periods=4*24*365, freq="15Min")
        self.df = DataFrame([random() for i in range(len(index))], index=index, columns=['value'])[index.day != 5]

    def test_something(self):
        class DateRange(object):
            def __init__(self, start, end):
                self.start_date = start
                self.end_date = end
        baseline = DateRange(datetime(2015,1,1), datetime(2015,4,30))
        competition = DateRange(datetime(2015,5,1), datetime(2015,8,31))
        sc = SavingCalculation(self.df, DailyAverageModel, competition, baseline, cumulative=False)
        savings = sc.savings()

if __name__ == "__main__":
    # from pandas import __version__
    # print(__version__)
    # exit()
    unittest.main()
