import pandas as pd
import scipy.signal as sci
# import numpy as np


def get_user_input(prompt):
    try:
        return raw_input(prompt)
    except NameError:
        return input(prompt)


def get_seconds_and_microseconds(pandas_time):
    return pandas_time.second + pandas_time.microsecond * 1e-6


def get_date(pandas_time):
    day = pandas_time.day
    month = pandas_time.month
    year = pandas_time.year
    return day, month, year


def load_results(my_file, interpolate):
    try:
        results = pd.read_csv(my_file, header=None)
        start_time = pd.to_datetime(float(results.iloc[0][0]), unit="s")
        sample_rate = float(results.iloc[1][0])
        results = results[2:]
        results.index = results.index-1
        results.columns = ['medida']
        # print('start time: {}'.format(start_time))
        # print('sample rate: {}'.format(sample_rate))
        results = interpolate_data(results, sample_rate, start_time, interpolate)
        return results
    except IOError:
        raise IOError('File {} not Found'.format(my_file))
    except Exception:
        raise Exception('Unexpected error in reading {}'.format(my_file))


def save_results(my_data, my_file):
    try:
        my_data.to_csv(my_file, encoding='utf-8', header=None, index=False)
    except IOError:
        raise IOError("File {} not Found".format(my_file))
    except Exception:
        raise Exception("Error in writing {}".format(my_file))


def interpolate_data(data, sample_rate, start_time, interpolate):
    if sample_rate == 1:
        data.index = pd.date_range(start=start_time, periods=len(data), freq='1000L')
    elif sample_rate == 2:
        data.index = pd.date_range(start=start_time, periods=len(data), freq='500L')
    elif sample_rate == 4:
        data.index = pd.date_range(start=start_time, periods=len(data), freq='250L')
    elif sample_rate == 8:
        # Downsample
        # idx_range = list(range(0,len(data))) # TODO: double check this one
        # data = data.iloc[idx_range[0::int(int(sample_rate)/8)]]
        # Set the index to be 8Hz
        data.index = pd.date_range(start=start_time, periods=len(data), freq='125L')
    else:
        data.index = pd.date_range(start=start_time, periods=len(data), freq='1000L')
        # raise ValueError("unvalid sample rate")
    # Interpolate all empty values
    if interpolate:
        data = interpolate_empty_values(data)
    data['filtered'] = butter_lowpass_filter(data['medida'], 0.05, 10, 1)
    data = data.resample("1000L").mean()
    return data


def interpolate_empty_values(data):
    cols = data.columns.values
    for c in cols:
        data.loc[:, c] = data[c].interpolate()

    return data


def butter_lowpass(cutoff, fs, order=5):
    # Filtering Helper functions
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = sci.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    # Filtering Helper functions
    b, a = butter_lowpass(cutoff, fs, order=order)
    # y = sci.lfilter(b, a, data, axis=0)
    y = sci.filtfilt(b, a, data, axis=0, padlen=0, irlen=None)
    return y
# Checking code
# results=load_results('example.csv')
# for i in results:
#     results.fiabilidad=5
# save_results(results, 'example2.csv')
# print(results.iloc[2:,:])
# print(results.medida[2:])
# print((results[2:].index-2)/4)
