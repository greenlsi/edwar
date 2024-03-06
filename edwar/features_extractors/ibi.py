"""
                                    CODE BASED IN
                    'ARTEFACT CORRECTION FOR HEART BEAT INTERVAL DATA'
                    By Saalasti Sami, Seppänen Mikko and Kuusela Antti
"""
# IBI VARIABLES

MAX_HR = 220        # Haskell & Fox based
MIN_HR = 40         # U.S. Department of Health and Human Services - National Ites of Health // Bradycardia record limit
MAX_DIFF_IBI = 0.2  # maximum ibi gradient value in seconds: theoretically 0.1s as
MAX_ERROR_MARGIN_TS = 0.01  # error in seconds allowed in IBI file clock
MAX_CORRECTION_TIME = 60  # seconds
MAX_VAR = 0.05      # artificial variability of added IBIs
MIN_SAMPLES = 1     # min samples to calculate HR
HR_FREQ = 1         # sample frequency of HR in seconds

MAX_IBI = 60 / MIN_HR
MIN_IBI = 60 / MAX_HR

import pandas as pd
import numpy as np
# import warnings
from itertools import accumulate

from ..parsers.ibi.variables import *


def __tacogram(ibi):
    ibi1 = pd.DataFrame(ibi['IBI'].values, columns=['IBI'])
    ibi1['c_date'] = ibi.index
    ibi1['next_date'] = ibi1['c_date'].shift(-1)
    ibi1.loc[ibi1.index[-1], 'next_date'] = (ibi1['c_date'].values[-1] +
                                             np.timedelta64(int(ibi1['IBI'].values[-1]), 's'))
    # Compare IBI calculated with IBI given to check there are not time lapsus
    ibi1['real_ibi'] = (ibi1['next_date'].values - ibi1['c_date'].values) / pd.Timedelta(1, 's')
    # Check there are not negative IBIs or timestamp values before to previous ones
    illegal = ibi1.loc[(ibi1['IBI'].values < 0) | (ibi1['real_ibi'].values < ibi1['IBI'].values)]
    ibi1 = ibi1.drop(illegal.index)
    ibi1['next_date1'] = ibi1['c_date'] + pd.to_timedelta(ibi1['IBI'], unit='s')
    ibi1['next_ibi1'] = ibi1['real_ibi'] - ibi1['IBI']  # next_ibi1 = 0 if there is no time lapsus

    if not illegal.empty:
        pass
        # raise ValueError('(!) IBI value can not be negative: {}->{}, {}->...'.format(
        #     illegal['c_date'][illegal.index[0]], illegal['IBI'][illegal.index[0]],
        #     illegal['next_date'][illegal.index[0]]))
        # TODO: log warning

    # Create IBIs to add
    out = ibi1.loc[abs(ibi1['next_ibi1'].values) > MAX_ERROR_MARGIN_TS, ('next_date1', 'next_ibi1')]
    output = pd.DataFrame(np.concatenate((ibi['IBI'].values, out['next_ibi1'].values)),
                          index=np.concatenate((ibi.index, out['next_date1'].values)), columns=['IBI'])
    output = output.sort_index()
    return output


def _error_detection(ibi):
    ibi1 = ibi.copy()
    ibi1['ERROR'] = 0
    ibi1['CORRECTED'] = 0
    ibi1['prev_DIFF'] = np.concatenate(([0], np.diff(np.array(ibi1['IBI']).flatten())))
    ibi1['next_DIFF'] = np.concatenate((np.diff(np.array(ibi1['IBI']).flatten()), [0]))
    # method 1: hard limits
    ibi1.loc[(ibi['IBI'].values > MAX_IBI) | (ibi1['IBI'].values < MIN_IBI), 'ERROR'] = 1
    # method 2: gradient limit
    ibi1['prev_ERROR'] = ibi1['ERROR'].shift()
    ibi1['next_ERROR'] = ibi1['ERROR'].shift(-1)  # if reference is valid (previous sample), apply method 2
    ibi1.loc[(abs(ibi1['prev_DIFF'].values) > MAX_DIFF_IBI) & (ibi1['prev_ERROR'].values != 1), 'ERROR'] = 1
    ibi1.loc[(abs(ibi1['next_DIFF'].values) > MAX_DIFF_IBI) & (ibi1['next_ERROR'].values != 1), 'ERROR'] = 1

    return ibi1[['IBI', 'ERROR', 'CORRECTED']]


def __wide_correction(ibi):  # buffer of 4 samples
    ibi1 = __error_intervals_sum(ibi.copy())
    ibi1['prev_IBI1'] = ibi1['IBI'].shift(1)
    ibi1['prev_IBI2'] = ibi1['IBI'].shift(2)
    ibi1['post_IBI1'] = ibi1['IBI'].shift(-1)
    ibi1['post_IBI2'] = ibi1['IBI'].shift(-2)
    ibi1['prev_IBI1'].fillna(ibi1['post_IBI1'], inplace=True)
    ibi1['post_IBI1'].fillna(ibi1['prev_IBI1'], inplace=True)
    ibi1['prev_IBI2'].fillna(ibi1['post_IBI1'], inplace=True)
    ibi1['post_IBI2'].fillna(ibi1['prev_IBI1'], inplace=True)
    ibi1['date'] = ibi1['prev_date1'] = ibi1['post_date1'] = ibi1.index
    ibi1['prev_date1'] = ibi1['prev_date1'].shift(1)
    ibi1['post_date1'] = ibi1['post_date1'].shift(-1)
    ibi2 = ibi1.loc[ibi1['ERROR'] != 0, :].copy()
    ibi2['n_ibis'] = ibi2['IBI'].values / ibi2[['prev_IBI1', 'post_IBI1']].mean(axis=1)

    # CASE A: MISSING IBIs
    # TODO: log warning # ibi.loc[ibi['IBI'].values > MAX_CORRECTION_TIME]
    add_ibis = ibi2.loc[(ibi2['n_ibis'].round() > 1) & (ibi2['IBI'].values < MAX_CORRECTION_TIME)].copy()

    def generate_random_ibis(ts0, n, ref1, ref2):
        increment = (ref2 - ref1)/n
        linear_interpolation = np.array([increment]*n).cumsum() + ref1
        rand_numbers = np.random.rand(n)
        rand_numbers = (rand_numbers - np.mean(rand_numbers)) / np.std(rand_numbers)
        rand_ibis = list(rand_numbers / max(abs(rand_numbers)) * MAX_VAR + linear_interpolation)
        rand_dates = [ts0] + [ts0 + td for td in list(accumulate(pd.to_timedelta(rand_ibis, unit="s")))][:-1]
        return pd.DataFrame(rand_ibis, index=rand_dates, columns=['IBI'])

    ibis_created = pd.DataFrame()
    if not add_ibis.empty:
        ibis_created = pd.concat(
            list(map(generate_random_ibis, add_ibis['date'], (add_ibis['n_ibis'].round()).astype(int),
                     add_ibis['prev_IBI1'], add_ibis['post_IBI1'])), axis=0
        )
        ibis_created['ERROR'] = 1
        ibis_created['CORRECTED'] = 1

    # CASE B: EXTRA IBIs
    ibis_edited = pd.DataFrame()
    edit_ibis = ibi2.loc[(ibi2['n_ibis'].values < 0.5)].copy()
    to_remove = list(edit_ibis.index)
    edit_ibis['ibi_new1'] = edit_ibis['IBI'] + edit_ibis['post_IBI1']
    edit_ibis = edit_ibis.dropna(subset=["prev_date1", "post_date1"])  # remove sample directly if it is first or last
    if not edit_ibis.empty:
        # case 1: add extra ibi to next sample & calculate error
        edit_ibis['err1'] = (abs(edit_ibis['IBI'] + edit_ibis['post_IBI1'] - edit_ibis['prev_IBI1']) +
                             abs(edit_ibis['IBI'] + edit_ibis['post_IBI1'] - edit_ibis['post_IBI2']))
        # case 2: add extra ibi to previous sample & calculate error
        edit_ibis['err2'] = (abs(edit_ibis['IBI'] + edit_ibis['prev_IBI1'] - edit_ibis['prev_IBI2']) +
                             abs(edit_ibis['IBI'] + edit_ibis['prev_IBI1'] - edit_ibis['post_IBI1']))

        # Choose best option
        ibis_edited['IBI'] = np.select([edit_ibis['err1'].values > edit_ibis['err2'].values],
                                       [edit_ibis['IBI'].values + edit_ibis['prev_IBI1'].values],
                                       edit_ibis['IBI'].values + edit_ibis['post_IBI1'].values)
        ibis_edited.index = np.select([edit_ibis['err1'].values > edit_ibis['err2'].values],
                                      [edit_ibis['prev_date1'].values],
                                      edit_ibis['date'].values)
        ibis_edited['ERROR'] = 1
        ibis_edited['CORRECTED'] = 1

    # in case 1 next ibi must be removed
    next_ibis_to_drop = list(edit_ibis.loc[ibis_edited.index == edit_ibis['date'], 'post_date1'])
    remove_ibis = list(set(list(add_ibis.index) + to_remove + list(ibis_edited.index) + next_ibis_to_drop))
    return remove_ibis, ibis_created, ibis_edited


def __error_intervals_sum(ibi):
    ibi1 = ibi.copy()
    ibi1['dates'] = ibi1.index
    ibi1['group'] = (ibi1['ERROR'] * ibi1['ERROR'].shift() != 1).cumsum()
    ibi1 = ibi1.groupby(ibi1['group'], as_index=False).agg({
        'IBI': sum, 'ERROR': max, 'CORRECTED': min, 'dates': min})
    ibi1 = ibi1.set_index('dates')
    ibi1 = ibi1.rename_axis(None)
    ibi1['DIFF'] = np.concatenate(([0], np.diff(np.array(ibi1['IBI']).flatten())))
    return ibi1[['IBI', 'ERROR', 'CORRECTED', 'DIFF']]


def _error_correction(ibi):
    ibi1 = __error_intervals_sum(ibi)
    remove_ibi, add_ibi1, add_ibi2 = __wide_correction(ibi1)
    ibi1 = ibi1.drop(remove_ibi)
    new_ibi = pd.concat([ibi1[['IBI', 'ERROR', 'CORRECTED']], add_ibi1, add_ibi2], axis=0)
    new_ibi = new_ibi.sort_index()
    return new_ibi


def check_ibi(ibi, correction=True):
    ibi1 = ibi.copy()
    tacogram_o = __tacogram(ibi1)
    detected = _error_detection(tacogram_o)
    if correction:
        corrected = _error_correction(detected)
    else:
        corrected = detected
    return corrected[['IBI', 'ERROR', 'CORRECTED']]


def calculate_hr(ibi):
    hr = pd.DataFrame()
    try:
        hr['HR'] = 60/ibi.loc[(ibi['ERROR'].values == 0) | (ibi['CORRECTED'].values == 1), 'IBI'].copy()
    except KeyError:
        hr['HR'] = 60/ibi['IBI']
    # return hr[['HR']].resample('{}s'.format(HR_FREQ), label='right').mean()
    hr1 = hr[['HR']].rolling('10s', min_periods=1).mean()
    return hr1.resample('{}s'.format(HR_FREQ), label='right').last()


def calculate_josue_hr(ibi):
    hr = pd.DataFrame()
    hr['IBI'] = ibi['IBI'].copy()
    hr['HR'] = 1
    hr1 = hr[['HR']].resample('1s'.format(HR_FREQ)).sum()
    hr2 = hr1.rolling(60, min_periods=MIN_HR).sum()
    return hr2.resample('{}s'.format(HR_FREQ), label='right').last()
