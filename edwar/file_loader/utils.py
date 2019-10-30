import os
import zipfile


def get_seconds_and_microseconds(pandas_time):
    return pandas_time.seconds + pandas_time.microseconds * 1e-6


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


# Check if directory is compressed or not
def file_to_df(dirpath, cfile):
    if zipfile.is_zipfile(dirpath):
        directory = zipfile.ZipFile(dirpath)
        file = directory.open(cfile)
    else:
        file = os.path.join(dirpath, cfile)
    return file
