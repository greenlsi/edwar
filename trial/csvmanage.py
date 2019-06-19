import pandas as pd
import os
from trial.eda_explorer.load_files import get_user_input, loadData_E4


def get_input(prompt):
    get_user_input(prompt)


def get_seconds_and_microseconds(pandas_time):
    return pandas_time.seconds + pandas_time.microseconds * 1e-6


def get_date(pandas_time):
    day = pandas_time.day
    month = pandas_time.month
    year = pandas_time.year
    return day, month, year


'''
def load_acc(my_file, interpolate):
    try:
        results = pd.read_csv(my_file, header=None)
        start_time = pd.to_datetime(float(results.iloc[0][0]), unit="s")
        sample_rate = float(results.iloc[1][0])
        results = results[2:]

        results.index = results.index-2
        results.columns = ['x', 'y', 'z']
        # print('start time: {}'.format(start_time))
        # print('sample rate: {}'.format(sample_rate))
        results = interpolate_data(results, sample_rate, start_time, interpolate, 0)

        return results
    except IOError:
        raise IOError('File {} not Found'.format(my_file))
    except Exception:
        raise Exception('Unexpected error in reading {}'.format(my_file))


def load_results(my_file, interpolate):
    try:
        results = pd.read_csv(my_file, header=None)
        start_time = pd.to_datetime(float(results.iloc[0][0]), unit="s")
        sample_rate = float(results.iloc[1][0])
        results = results[2:]
        results.index = results.index-2
        results.columns = ['EDA']
        # print('start time: {}'.format(start_time))
        # print('sample rate: {}'.format(sample_rate))
        results = interpolate_data(results, sample_rate, start_time, interpolate, 1)
        return results
    except IOError:
        raise IOError('File {} not Found'.format(my_file))
    except OSError:
        raise IOError('System File {} wrong/not Found'.format(my_file))
    except Exception:
        raise Exception('Unexpected error in reading {}'.format(my_file))
'''


def _load_hr(filepath):
    # Load data
    hr_data = pd.read_csv(filepath)

    # Get the startTime and sample rate
    start_time = pd.to_datetime(float(hr_data.columns[0]), unit="s")
    sample_rate = float(hr_data.iloc[0][0])
    if sample_rate != 1:
        raise ValueError("HR sample rate expected 1 Hz but sampled at {}".format(sample_rate))
    hr_data = hr_data[hr_data.index != 0]
    hr_data.index = hr_data.index - 1

    # Reset the data frame assuming expected_sample_rate
    hr_data.columns = ["HR"]

    # Make sure data has a sample rate of 8Hz
    hr_data.index = pd.date_range(start=start_time, periods=len(hr_data), freq='1S')
    hr_data = hr_data.resample("125L").mean()

    # Interpolate all empty values
    hr_data.loc[:, "HR"] = hr_data.interpolate()
    return hr_data


def _load_bvp(filepath):
    # Load data
    bvp_data = pd.read_csv(filepath)

    # Get the startTime and sample rate
    start_time = pd.to_datetime(float(bvp_data.columns[0]), unit="s")
    sample_rate = float(bvp_data.iloc[0][0])
    if sample_rate != 64:
        raise ValueError("BVP sample rate expected 1 Hz but sampled at {}".format(sample_rate))
    bvp_data = bvp_data[bvp_data.index != 0]
    bvp_data.index = bvp_data.index - 1

    # Reset the data frame assuming expected_sample_rate
    bvp_data.columns = ["BVP"]

    # Make sure data has a sample rate of 8Hz
    bvp_data.index = pd.date_range(start=start_time, periods=len(bvp_data), freq='15625U')
    bvp_data = bvp_data.resample("125L").mean()

    # Interpolate all empty values
    bvp_data.loc[:, "BVP"] = bvp_data.interpolate()
    return bvp_data


def load_results(filepath):
    try:
        e4_data = loadData_E4(filepath)
        hr_data = _load_hr(os.path.join(filepath, 'HR.csv'))
        bvp_data = _load_bvp(os.path.join(filepath, 'BVP.csv'))
    except IOError:
        raise IOError("File {} not Found".format(filepath))
    except Exception:
        raise Exception("Error in reading {}".format(filepath))
    e4_data = e4_data.join(hr_data, how='inner')
    e4_data = e4_data.join(bvp_data, how='inner')
    # min_length = min(len(e4_data), len(hr_data))
    return e4_data


def save_results(my_data, my_file):
    try:
        my_data.to_csv(my_file, encoding='utf-8', header=None, index=False)
    except IOError:
        raise IOError("File {} not Found".format(my_file))
    except Exception:
        raise Exception("Error in writing {}".format(my_file))


def downsample_to_1hz(e4_data):
    e4_data = e4_data.resample("1S").mean()
    return e4_data


def downsample_to_1min(e4_data):
    e4_data = e4_data.resample("1T").mean()
    return e4_data


if __name__ == "__main__":

    data = load_results("../data/ejemplo4")
    # data = downsample_to_1min(data)
    print(data)
