import pandas as pd

from . import utils

__all__ = {
    'load_files'
}


def _load_single_file(directory, file, list_of_columns):
    # Load data
    if '.csv' in file:
        f = utils.file_to_df(directory, file)
    else:
        f = utils.file_to_df(directory, '_' + file + '_', partial_name=True)
    try:
        data1 = pd.read_csv(f)
    except FileNotFoundError:
        raise FileNotFoundError("(!) Something went wrong with {}: File not Found".format(f))
    except Exception as err:
        raise Exception("(!) Something went wrong with {}: {}".format(f, err))
    data1 = data1[data1.index != 0]
    data1.index = data1.index - 1
    data = pd.DataFrame(data1.iloc[:, 4])
    data.index = list(pd.to_datetime(data1.iloc[:, 2].astype('float'), unit="s"))
    data.columns = list_of_columns
    period = utils.get_time_difference(data.index[0], data.index[1])
    for i in range(1, len(data.index) - 1):
        period = min(period, utils.get_time_difference(data.index[i], data.index[i+1]))
    data.frequency = 1/period
    return data


def _load_ibi_file(directory, file, list_of_columns):
    # Load data
    if '.csv' in file:
        f = utils.file_to_df(directory, file)
    else:
        f = utils.file_to_df(directory, '_' + file + '_', partial_name=True)
    try:
        data1 = pd.read_csv(f)
    except FileNotFoundError:
        raise FileNotFoundError("(!) Something went wrong with {}: File not Found".format(f))
    except Exception as err:
        raise Exception("(!) Something went wrong with {}: {}".format(f, err))
    data1 = data1[data1.index != 0]
    data1.index = data1.index - 1
    data = pd.DataFrame(data1.iloc[:, 4]/1000.0)
    start_time = data1.iloc[:, 2][0]
    new_index = [start_time]
    for i in range(0, len(data1) - 1):
        next_ts = new_index[-1] + data1.iloc[:, 4][i] / 1000.0  # to improve precision of ts of everion (1 second)
        if data1.iloc[:, 2][i+1] - next_ts > 1:            # if time difference major than 1 second (precision)
            next_ts = data1.iloc[:, 2][i+1]
        new_index += [next_ts]
    data.index = pd.to_datetime(new_index, unit="s")
    data.columns = list_of_columns
    data.frequency = None
    return data


def load_files(dirpath, variables):
    data = list()
    for file in variables.keys():
        if 'IBI' in file:
            v = _load_ibi_file(dirpath, file, variables[file].replace(' ', '').split(','))
        else:
            v = _load_single_file(dirpath, file, variables[file].replace(' ', '').split(','))
            if 'gsr' in file:
                v[:] = 1/v[:]*1000
            elif 'hrv' in file:
                v[:] = v[:]/1000.0
        data.append(v)
    return data
