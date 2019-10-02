import os
import zipfile
import configparser
import pandas as pd


def get_input(prompt):
    return input(prompt)


def get_seconds_and_microseconds(pandas_time):
    return pandas_time.seconds + pandas_time.microseconds * 1e-6


def get_date(pandas_time):
    day = pandas_time.day
    month = pandas_time.month
    year = pandas_time.year
    return day, month, year


def _load_single_file(directory, file, list_of_columns):
    # Load data1
    f = file_to_df(directory, file)
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

    # Reset the data1 frame assuming expected_sample_rate
    data.columns = list_of_columns

    # Make sure data1 has a sample rate of 8Hz
    data.index = pd.date_range(start=start_time, periods=len(data), freq=str(int(increment*1e6))+'U')
    data = data.resample("125L").mean()
    cols = data.columns.values
    for c in cols:
        data.loc[:, c] = data[c].interpolate()

    return data


def load_results(dirpath):
    structureFile = "structure.ini"
    if not os.path.exists(structureFile):
        raise Exception("\n\t(!) Something went wrong: Configuration file {} not found".format(structureFile))
    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.optionxform = str
    config.read(structureFile)
    variables = config.items(section='VARIABLES')
    data = pd.DataFrame()
    for variable in variables:
        try:
            v = _load_single_file(dirpath, variable[0]+'.csv', variable[1].split(', '))
        except Exception as err:
            raise Exception("\n\t(!) Something went wrong with {}: {}".format(variable[0]+'.csv', err))
        if data.empty:
            data = v
        else:
            data = data.join(v, how='inner')

    return data


def save_results(my_data, my_file):
    try:
        my_data.to_csv(my_file, encoding='utf-8', header=None, index=False)
    except IOError:
        raise IOError("File {} not Found".format(my_file))
    except Exception:
        raise Exception("Error while writing in {}".format(my_file))


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


if __name__ == "__main__":
    Data = load_results("../data1/ejemplo4")[0:100]
    # Data = downsample_to_1min(Data)
    print(Data)
