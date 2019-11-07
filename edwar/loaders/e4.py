import os

import configparser
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
    except IOError:
        raise IOError("File {} not Found".format(f))
    except Exception:
        raise Exception("Error in {}".format(f))

    # Get the startTime and sample rate
    start_time = pd.to_datetime(float(data.columns.values[0]), unit="s")
    sample_rate = float(data.iloc[0][0])
    increment = 1/sample_rate
    data = data[data.index != 0]
    data.index = data.index - 1

    data.columns = list_of_columns

    # Make sure data has a sample rate of 8Hz
    data.index = pd.date_range(start=start_time, periods=len(data), freq=str(int(increment*1e6))+'U')
    data = data.resample("125L").mean()
    cols = data.columns.values
    for c in cols:
        data.loc[:, c] = data[c].interpolate()

    return data


def _load_ibi_file(directory, file, list_of_columns):
    # Load data
    f = utils.file_to_df(directory, file)
    try:
        ibi = pd.read_csv(f)
    except IOError:
        raise IOError("File {} not Found".format(f))
    except Exception:
        raise Exception("Error in {}".format(f))

    # Get the startTime and sample rate
    start_time = pd.to_datetime(float(ibi.columns.values[0]), unit="s")
    list_index = list(start_time + pd.to_timedelta(ibi.iloc[:, 0], unit='s'))
    ibi = pd.DataFrame(ibi.iloc[:, 1])
    ibi.columns = list_of_columns
    ibi.index = list_index
    return ibi


def load_files(dirpath, downsample=None):
    structure_file = "structure.ini"
    if not os.path.exists(structure_file):
        raise Exception("\n\t(!) Something went wrong: Configuration file {} not found".format(structure_file))
    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.optionxform = str
    config.read(structure_file)
    variables = config.items(section='VARIABLES E4')
    ibi = data = pd.DataFrame()
    for variable in variables:
        if variable[0] == 'IBI':
            try:
                ibi = _load_ibi_file(dirpath, variable[0] + '.csv', variable[1].replace(' ', '').split(','))
            except Exception as err:
                raise Exception("\n\t(!) Something went wrong with {}: {}".format(variable[0]+'.csv', err))
        else:
            try:
                v = _load_single_file(dirpath, variable[0] + '.csv', variable[1].split(', '))
            except Exception as err:
                raise Exception("\n\t(!) Something went wrong with {}: {}".format(variable[0]+'.csv', err))
            if data.empty:
                data = v
            else:
                data = data.join(v, how='inner')

    if downsample == '1s':
        data = utils.downsample_to_1s(data)
        ibi = utils.downsample_to_1s(ibi)
    elif downsample == '10s':
        data = utils.downsample_to_10s(data)
        ibi = utils.downsample_to_10s(ibi)
    elif downsample == '1min':
        data = utils.downsample_to_1min(data)
        ibi = utils.downsample_to_1min(ibi)
    else:
        pass

    return [data, ibi]


if __name__ == "__main__":
    Data, IBI = load_files("../data/ejemplo4")[:][0:100]
    print(Data)
    print(IBI)
