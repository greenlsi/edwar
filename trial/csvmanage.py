
import os
import zipfile
import pandas as pd
from scipy import signal

# from trial.eda_explorer.load_files import butter_lowpass_filter


def get_input(prompt):
    return input(prompt)


def get_seconds_and_microseconds(pandas_time):
    return pandas_time.seconds + pandas_time.microseconds * 1e-6


def get_date(pandas_time):
    day = pandas_time.day
    month = pandas_time.month
    year = pandas_time.year
    return day, month, year


'''
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


def _load_single_file(directory, file, list_of_columns, expected_sample_rate, freq):
    # Load data
    f = file_to_df(directory, file)
    try:
        data = pd.read_csv(f)
    except IOError:
        raise IOError("File {} not Found".format(f))
    except Exception:
        raise Exception("Error in writing {}".format(f))

    # Get the startTime and sample rate
    start_time = pd.to_datetime(float(data.columns.values[0]), unit="s")
    sample_rate = float(data.iloc[0][0])
    data = data[data.index != 0]
    data.index = data.index - 1

    # Reset the data frame assuming expected_sample_rate
    data.columns = list_of_columns
    if sample_rate != expected_sample_rate:
        print('\n\t(!) Something is wrong: file {} not sampled at {}Hz. Problems will ' +
              'occur\n'.format(file, expected_sample_rate))

    # Make sure data has a sample rate of 8Hz
    # Make sure data has a sample rate of 8Hz
    data.index = pd.date_range(start=start_time, periods=len(data), freq=freq)
    data = data.resample("125L").mean()
    cols = data.columns.values
    for c in cols:
        data.loc[:, c] = data[c].interpolate()

    return data


def load_results(dirpath):

    # Load EDA data
    eda_data = _load_single_file(dirpath, 'EDA.csv', ["EDA"], 4, "250L")
    # Get the filtered data using a low-pass butterworth filter (cutoff:1hz, fs:8hz, order:6)
    eda_data['filtered_eda'] = butter_lowpass_filter(eda_data['EDA'], 1.0, 8, 6)
    # Load HR data
    hr_data = _load_single_file(dirpath, 'HR.csv', ["HR"], 1, "1S")
    # Load ACC data
    acc_data = _load_single_file(dirpath, 'ACC.csv', ["AccelX", "AccelY", "AccelZ"], 32, "31250U")
    # Scale the accelometer to +-2g
    acc_data[["AccelX", "AccelY", "AccelZ"]] = acc_data[["AccelX", "AccelY", "AccelZ"]] / 64.0
    # Load Temperature data
    temperature_data = _load_single_file(dirpath, 'TEMP.csv', ["Temp"], 4, "250L")

    data = eda_data.join(hr_data, how='inner')
    data = data.join(temperature_data, how='inner')
    data = data.join(acc_data, how='inner')
    # E4 sometimes records different length files - adjust as necessary
    min_length = min(len(acc_data), len(eda_data), len(temperature_data), len(hr_data))

    return data[:min_length]


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


# Check if directory is compressed or not
def file_to_df(dirpath, cfile):
    if zipfile.is_zipfile(dirpath):
        directory = zipfile.ZipFile(dirpath)
        file = directory.open(cfile)
    else:
        file = os.path.join(dirpath, cfile)
    return file


def butter_lowpass(cutoff, fs, order=5):
    # Filtering Helper functions
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    # noinspection PyTupleAssignmentBalance
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    # Filtering Helper functions
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y


if __name__ == "__main__":
    Data = load_results("../data/ejemplo4")[0:100]
    # Data = downsample_to_1min(Data)
    print(Data)
