import logging
import pandas as pd

from . import utils
from ..errors import *


__all__ = {
    'load_files'
}


def _load_single_file(directory, file, list_of_columns):
    # Load data
    f = utils.file_to_df(directory, file)
    log = logging.getLogger('EDWAR')
    try:
        data = pd.read_csv(f)
    except DeviceFileNotFoundError:
        log.error("E4 data file {} not found, so {} will not be available.".format(file, list_of_columns))
        return
    except Exception as err:
        log.error("E4 data file {} unknown error: {}.".format(file, err))
        return

    try:
        # Get the startTime and sample rate
        start_time = pd.to_datetime(float(data.columns.values[0]), unit="s")
        sample_rate = float(data.iloc[0][0])
        increment = 1/sample_rate
        data = data[data.index != 0]  # remove first data
        data.index = data.index - 1

        data.columns = list_of_columns

    except Exception:
        n = len(list_of_columns)
        expected_format = (
            "{} column(s), first value as init timestamp, second value as sample rate and"
            "following values as sampled data".format(n)
        )
        log.error("E4 data file {} format error. Expected format is {}.".format(file, expected_format))
        # raise FileFormatError(file, expected_format, 'unknown')
        return
    else:
        # Make sure data has a sample rate of 8Hz
        data.index = pd.date_range(start=start_time, periods=len(data), freq=str(int(increment*1e6))+'U')
        data.frequency = sample_rate
        log.info("E4 data in {} file loaded.".format(file))
        return data


def _load_ibi_file(directory, file, list_of_columns):
    # Load data
    f = utils.file_to_df(directory, file)
    log = logging.getLogger('EDWAR')
    try:
        ibi = pd.read_csv(f)
    except DeviceFileNotFoundError:
        log.error("E4 data file {} not found, so {} will not be available.".format(file, list_of_columns))
        return
    except Exception as err:
        log.error("Error in file {}: {}.".format(file, err))
        return

    try:
        # Get the startTime and sample rate
        start_time = float(ibi.columns.values[0])
        list_index = list(pd.to_datetime(start_time + ibi.iloc[:, 0] - ibi.iloc[:, 1], unit='s'))
        ibi = pd.DataFrame(ibi.iloc[:, 1])
        ibi.columns = list_of_columns
        ibi.index = list_index
        ibi.frequency = None
    except Exception:
        expected_format = (
            "two columns, first value in first column as init timestamp and following values as time "
            "difference respect init timestamp; second column are IBI sampled values at those times"
        )
        log.error('E4 data file {} format error. Expected format is {}.'.format(file, expected_format))
        # raise FileFormatError(file, expected_format, 'unknown')
        return
    else:
        log.info("E4 data in {} file loaded.".format(file))
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
        if v is not None:
            data.append(v)
    return data
