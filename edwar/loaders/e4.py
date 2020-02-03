import pandas as pd

from . import utils


__all__ = {
    'load_files'
}


def _load_single_file(directory, file, list_of_columns):
    # Load data
    f = utils.file_to_df(directory, file)
    try:
        data = pd.read_csv(f)
    except FileNotFoundError:
        raise FileNotFoundError("(!) Something went wrong with {}: File not Found".format(f))
    except Exception as err:
        raise Exception("(!) Something went wrong with {}: {}".format(f, err))

    # Get the startTime and sample rate
    start_time = pd.to_datetime(float(data.columns.values[0]), unit="s")
    sample_rate = float(data.iloc[0][0])
    increment = 1/sample_rate
    data = data[data.index != 0]
    data.index = data.index - 1

    data.columns = list_of_columns

    # Make sure data has a sample rate of 8Hz
    data.index = pd.date_range(start=start_time, periods=len(data), freq=str(int(increment*1e6))+'U')
    data.frequency = sample_rate
    return data


def _load_ibi_file(directory, file, list_of_columns):
    # Load data
    f = utils.file_to_df(directory, file)
    try:
        ibi = pd.read_csv(f)
    except FileNotFoundError:
        raise FileNotFoundError("(!) Something went wrong with {}: File not Found".format(f))
    except Exception as err:
        raise Exception("(!) Something went wrong with {}: {}".format(f, err))

    # Get the startTime and sample rate
    start_time = float(ibi.columns.values[0])
    list_index = list(pd.to_datetime(start_time + ibi.iloc[:, 0] - ibi.iloc[:, 1], unit='s'))
    ibi = pd.DataFrame(ibi.iloc[:, 1])
    ibi.columns = list_of_columns
    ibi.index = list_index
    ibi.frequency = None
    return ibi


def load_files(dirpath, variables):
    data = list()
    for file in variables.keys():
        if 'IBI' in file:
            v = _load_ibi_file(dirpath, file + '.csv', variables[file].replace(' ', '').split(','))
        else:
            v = _load_single_file(dirpath, file + '.csv', variables[file].replace(' ', '').split(','))
            if 'ACC' in file:
                v[:] = v[:]/64.0
        data.append(v)
    return data
