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
        data1 = pd.read_csv(f)
    except IOError:
        raise IOError("File {} not Found".format(f))
    except Exception:
        raise Exception("Error in {}".format(f))
    data1 = data1[data1.index != 0]
    data1.index = data1.index - 1
    data = pd.DataFrame(data1.iloc[:, 4])
    data.index = list(pd.to_datetime(data1.iloc[:, 2].astype('float'), unit="s"))
    # Make sure data has a sample rate of 8Hz
    data.columns = list_of_columns
    # data = data.resample("125L").mean()
    # cols = data.columns.values
    # for c in cols:
    #     data.loc[:, c] = data[c].interpolate()

    return data


def load_files(dirpath, downsample=None):
    structure_file = "structure.ini"
    if not os.path.exists(structure_file):
        raise Exception("\n\t(!) Something went wrong: Configuration file {} not found".format(structure_file))
    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.optionxform = str
    config.read(structure_file)
    variables = config.items(section='VARIABLES')
    data = pd.DataFrame()
    for variable in variables:
        try:
            v = _load_single_file(dirpath, variable[0] + '.csv', variable[1].replace(' ', '').split(','))
        except Exception as err:
            raise Exception("\n\t(!) Something went wrong with {}: {}".format(variable[0]+'.csv', err))
        if data.empty:
            data = v
        else:
            data = data.join(v, how='inner')
    if downsample == '1s':
        data = utils.downsample_to_1s(data)
    elif downsample == '1min':
        data = utils.downsample_to_1min(data)
    else:
        pass
    return data


if __name__ == '__main__':
    Data = load_files('../data/everion/Dataexport')
    Data = utils.downsample_to_1min(Data)
    print(Data)
