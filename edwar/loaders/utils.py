import os
import zipfile
import glob

from ..errors import *


def get_time_difference(pandas_time1, pandas_time2):
    time1 = ((pandas_time1.day * 24 + pandas_time1.hour) * 60 + pandas_time1.minute) * 60 + pandas_time1.second + \
            pandas_time1.microsecond * 1e-6
    time2 = ((pandas_time2.day * 24 + pandas_time2.hour) * 60 + pandas_time2.minute) * 60 + pandas_time2.second + \
            pandas_time2.microsecond * 1e-6
    diff = abs(time1 - time2)
    return diff


def get_seconds_and_microseconds(pandas_time):
    return pandas_time.second + pandas_time.microsecond * 1e-6


def get_date(pandas_time):
    day = pandas_time.day
    month = pandas_time.month
    year = pandas_time.year
    return day, month, year


def downsample_to_1s(data):
    data = data.resample("1S").mean()
    return data


def downsample_to_10s(data):
    data = data.resample("10S").mean()
    return data


def downsample_to_1min(data):
    data = data.resample("1T").mean()
    return data


def resample_to_8hz(data):
    data = data.resample("125L").mean()
    cols = data.columns.values
    for c in cols:
        data.loc[:, c] = data[c].interpolate()
    return data


# Check if directory is compressed or not
def file_to_df(dirpath, cfile, partial_name=False):
    if zipfile.is_zipfile(dirpath):
        directory = zipfile.ZipFile(dirpath)
        if partial_name:
            cfile1 = [f for f in directory.namelist() if cfile in f]
            if len(cfile1) == 0:
                raise DeviceFileNotFoundError(cfile)
            elif len(cfile1) > 1:
                raise SeveralFilesFoundError(partial_name, cfile1)
            else:
                file = directory.open(cfile1[0])
        else:
            file = directory.open(cfile)
    else:
        if partial_name:
            cfile1 = glob.glob(os.path.join(dirpath, '*' + cfile + '*'))
            if len(cfile1) == 0:
                raise DeviceFileNotFoundError('*' + cfile + '*')
            elif len(cfile1) > 1:
                raise SeveralFilesFoundError(partial_name, cfile1)
            else:
                file = cfile1[0]
        else:
            file = os.path.join(dirpath, cfile)
    return file
