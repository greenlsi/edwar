import logging
import pandas as pd
import numpy as np

from . import utils
from ..errors import *

__all__ = {
    'load_files'
}


def _load_single_file(directory, file, list_of_columns):
    log = logging.getLogger('EDWAR')
    # Load data
    if '.csv' in file:
        f = utils.file_to_df(directory, file)
    else:
        f = utils.file_to_df(directory, '_' + file + '_', partial_name=True)
    try:
        data1 = pd.read_csv(f)
    except DeviceFileNotFoundError:
        log.error("EVERION data file {} not found, so {} will not be available.".format(file, list_of_columns))
        return
    except SeveralFilesFoundError as e:
        log.error("Several EVERION data files found when searching {}.".format(e.search))
        return
    except Exception as err:
        log.error("EVERION data file {} unknown error: {}.".format(file, err))
        return

    try:
        data1 = data1[data1.index != 0]
        data1.index = data1.index - 1
        data = pd.DataFrame(data1.iloc[:, 4])
        data.index = list(pd.to_datetime(data1.iloc[:, 2].astype('float'), unit="s"))
        data.columns = list_of_columns
    except Exception:
        expected_format = (
            "6 columns, third and fifth columns needed, third column as timestamps and fifth column as sampled "
            "data values in those timestamps"
        )
        log.error("EVERION data file {} format error. Expected format is {}.".format(file, expected_format))
        # raise FileFormatError(file, expected_format, 'unknown')
        return
    else:
        period = min(data1.iloc[:, 2].shift(-1) - data1.iloc[:, 2])
        try:
            data.frequency = 1/period
        except ZeroDivisionError:
            data.frequency = np.inf
        log.info("EVERION data in {} file loaded.".format(file))
        return data


def _load_ibi_file(directory, file, list_of_columns):
    log = logging.getLogger('EDWAR')
    # Load data
    if '.csv' in file:
        f = utils.file_to_df(directory, file)
    else:
        f = utils.file_to_df(directory, '_' + file + '_', partial_name=True)
    try:
        data1 = pd.read_csv(f)
    except DeviceFileNotFoundError:
        log.error("EVERION data file {} not found, so {} will not be available.".format(file, list_of_columns))
        return
    except SeveralFilesFoundError as e:
        log.error("Several EVERION data files found when searching {}.".format(e.search))
        return
    except Exception as err:
        log.error("EVERION data file {} unknown error: {}.".format(file, err))
        return

    try:
        data1 = data1[data1.index != 0]
        data1.index = data1.index - 1
        data = pd.DataFrame(data1.iloc[:, 4] / 1000.0)
        data1['expected_ts'] = ((data1.iloc[:, 2] + data1.iloc[:, 4] / 1000.0).shift()).fillna(0)
        data1['reference'] = np.where((data1.iloc[:, 2] - data1['expected_ts']) > 2, data1.iloc[:, 2], np.nan)
        data1['reference'] = data1['reference'].fillna(method='ffill')
        grouper = (data1['reference'] != data1['reference'].shift()).cumsum()
        data1['sum'] = data1.iloc[:, 4].groupby(grouper).transform(lambda x: x.cumsum().shift().fillna(0)) / 1000.0
        data1['new_index'] = data1['reference'] + data1['sum']
        data.index = pd.to_datetime(data1['new_index'].values * 1000, unit="ms")
        data.columns = list_of_columns
        data.frequency = None
    except Exception:
        expected_format = (
            "6 columns, third and fifth columns needed, third column as timestamps and fifth column as sampled "
            "data values in those timestamps"
        )
        log.error("EVERION data file {} format error. Expected format is {}.".format(file, expected_format))
        # raise FileFormatError(file, expected_format, 'unknown')
        return
    else:
        log.info("EVERION data in {} file loaded.".format(file))
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
        if v is not None:
            data.append(v)
    return data
