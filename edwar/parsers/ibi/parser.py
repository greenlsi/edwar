import pandas as pd
import numpy as np
# import warnings
import matplotlib.pyplot as plt
import datetime
from scipy.stats import norm

from ..utils import get_diff_seconds

# VARIABLES
max_hr = 220  # Haskell & Fox based
min_hr = 40  # U.S. Department of Health and Human Services - National Ites of Health // Bradycardia record limit
window_error_detection = 4  # seconds
max_correction_time = 60  # seconds


def __tacogram(ibi):
    ibi1 = ibi.copy()
    for i in range(0, len(ibi1) - 1):
        ibi_i = get_diff_seconds(ibi1.index[i], ibi1.index[i + 1])
        if ibi_i < 0 or ibi1.values[i] < 0:
            raise ValueError('(!) IBI value can not be negative: {}->{}, {}->{}'.format(ibi1.index[i], ibi1.values[i],
                                                                                        ibi1.index[i+1],
                                                                                        ibi1.values[i+1]))
        elif abs(ibi_i - ibi1.values[i]) > 0.01:  # error of 10 ms is allowed
            new_date = ibi1.index[i] + np.timedelta64(int(ibi1.values[i] * 1e9), 'ns')
            new_ibi = ibi_i - ibi1.values[i]
            ibi1 = ibi1.append(pd.DataFrame([new_ibi], index=[new_date], columns=['IBI']))
    ibi1 = ibi1.sort_index()
    return ibi1


def _error_detection(ibi):
    max_ibi = 60 / min_hr
    min_ibi = 60 / max_hr
    max_diff_ibi = 0.2  # maximum ibi gradient value in seconds
    ibi['ERROR'] = np.zeros(len(ibi['IBI']))
    ibi['CORRECTED'] = np.zeros(len(ibi['IBI']))
    ibi['DIFF'] = np.concatenate((np.diff(np.array(ibi['IBI']).flatten()), [0]))

    for i in range(0, len(ibi)-1):
        if ibi['IBI'][i] > max_ibi or ibi['IBI'][i] < min_ibi:  # method 1: hard limits
            ibi['ERROR'][i] = 1

        elif abs(ibi['DIFF'][i]) > max_diff_ibi:                # method 2: gradient limit
            ibi['ERROR'][i + 1] = 1                             # if reference is valid, apply method 2 to next sample

    if ibi['IBI'][-1] > max_ibi or ibi['IBI'][-1] < min_ibi:    # method 1: only value left to check
        ibi['ERROR'][-1] = 1

    return ibi


def __wide_correction(ibi_pre2, ibi_pre1, ibi_e, ibi_pos1, ibi_pos2):  # buffer of 4 samples
    ibi_c = pd.DataFrame()  # new IBIs corrected
    ibi_d = pd.DataFrame()  # IBIs to be deleted
    if ibi_e['IBI'] > max_correction_time:
        pass
        # print('(!) IBI is interrupted at {} {} seconds (max {}), so correction is not possible'.format(
        #       ibi_e.index, round(ibi_e, 2), max_correction_time))  # TODO: log warning
    else:
        prev_reference = ibi_pos1['IBI'] if ibi_pre1 is None else ibi_pre1['IBI']
        post_reference = ibi_pre1['IBI'] if ibi_pos1 is None else ibi_pos1['IBI']
        diff = abs(ibi_e['DIFF']) if ibi_pre1 is None else abs(ibi_e['DIFF']) + abs(ibi_pre1['DIFF'])
        n_ibis = int(round(ibi_e['IBI'] / np.mean([prev_reference, post_reference])))  # how many IBIs needed

        if n_ibis >= 1:     # create more IBIs (peaks not detected)
            new_ibi_mean = ibi_e['IBI'] / n_ibis
            if (abs(new_ibi_mean - prev_reference) + abs(new_ibi_mean - post_reference)) >= diff:
                # if error with new ibi increases, do nothing
                pass
            else:
                max_var = 0.05
                rand_numbers = np.random.rand(n_ibis)
                rand_numbers = (rand_numbers - np.mean(rand_numbers)) / np.std(rand_numbers)
                new_interval = rand_numbers / max(abs(rand_numbers)) * max_var + new_ibi_mean
                ts = ibi_e.name
                new_index = [ts]
                for i in range(0, len(new_interval) - 1):
                    ts += datetime.timedelta(seconds=new_interval[i])
                    new_index.append(ts)
                ibi_c['IBI'] = new_interval
                ibi_c['ERROR'] = np.ones(len(new_interval))
                ibi_c['CORRECTED'] = np.ones(len(new_interval))
                ibi_c['DIFF'] = np.concatenate((np.diff(np.array(ibi_c['IBI']).flatten()), [ibi_pos1['IBI'] -
                                                                                            new_interval[-1]]))
                ibi_c.index = new_index
                ibi_d = ibi_d.append(ibi_e)
        else:           # delete IBIs (trigger false peaks)
            if ibi_pos1 is None or ibi_pre1 is None:
                # check if last or first ibi: remove it directly
                ibi_d = ibi_d.append(ibi_e)
            else:
                # case 1: add extra ibi to next & calculate error
                ibi_new1 = ibi_e['IBI'] + ibi_pos1['IBI']
                prev_reference1 = ibi_pre1['IBI']
                if ibi_pos2 is not None:
                    post_reference1 = ibi_pos2['IBI']
                else:
                    post_reference1 = ibi_new1
                error_pos = abs(ibi_new1 - prev_reference1) + abs(ibi_new1 - post_reference1)

                # case 2: add extra ibi to previous & calculate error
                ibi_new2 = ibi_e['IBI'] + ibi_pre1['IBI']
                post_reference2 = ibi_pos1['IBI']
                if ibi_pre2 is not None:
                    prev_reference2 = ibi_pre2['IBI']
                else:
                    prev_reference2 = ibi_new2
                error_pre = abs(ibi_new2 - prev_reference2) + abs(ibi_new2 - post_reference2)

                if error_pre > error_pos:
                    # apply case 1
                    ibi_c['IBI'] = [ibi_new1]
                    ibi_c['ERROR'] = [1]
                    ibi_c['CORRECTED'] = [1]
                    ibi_c['DIFF'] = [post_reference1 - ibi_new1]
                    ibi_c.index = [ibi_e.name]
                    ibi_d = ibi_d.append(ibi_e)
                    ibi_d = ibi_d.append(ibi_pos1)
                else:
                    # apply case 2
                    ibi_c['IBI'] = [ibi_new2]
                    ibi_c['ERROR'] = [1]
                    ibi_c['CORRECTED'] = [1]
                    ibi_c['DIFF'] = [post_reference2 - ibi_new2]
                    ibi_c.index = [ibi_pre1.name]
                    ibi_d = ibi_d.append(ibi_e)
                    ibi_d = ibi_d.append(ibi_pre1)
    return ibi_c, ibi_d


def __error_intervals_sum(ibi):
    ibi['dates'] = ibi.index
    ibi = ibi.groupby([(ibi.ERROR * ibi.ERROR.shift() != 1).cumsum()], as_index=False).agg({
        'IBI': sum, 'ERROR': max, 'CORRECTED': min, 'dates': min})
    ibi = ibi.set_index('dates')
    ibi = ibi.rename_axis(None)
    ibi['DIFF'] = np.concatenate((np.diff(np.array(ibi['IBI']).flatten()), [0]))
    return ibi


def _error_correction(ibi):
    ibis_to_drop = list()
    ibis_to_add = list()
    ibi = __error_intervals_sum(ibi)
    for i in range(0, len(ibi)):
        pre_value1 = ibi.iloc[i - 1] if i > 1 else None
        pre_value2 = ibi.iloc[i - 2] if i > 2 else None
        pos_value1 = ibi.iloc[i + 1] if i + 1 < len(ibi['IBI']) else None
        pos_value2 = ibi.iloc[i + 2] if i + 2 < len(ibi['IBI']) else None
        if ibi['ERROR'][i] != 0:
            ibi_to_add, ibi_to_drop = __wide_correction(pre_value2, pre_value1, ibi.iloc[i], pos_value1, pos_value2)
            if not ibi_to_add.empty:
                ibis_to_add.append(ibi_to_add)
            if not ibi_to_drop.empty:
                ibis_to_drop.append(ibi_to_drop)

    for a in ibis_to_drop:  # remove selected intervals
        ibi = ibi.drop(a.index, axis=0)

    for a in ibis_to_add:  # add new intervals created
        ibi = ibi.append(a, sort=False)
    ibi = ibi.sort_index()
    return ibi[['IBI', 'ERROR', 'CORRECTED', 'DIFF']]


def check_ibi(ibi, correction=True):
    ibi1 = ibi.copy()
    tacogram_o = __tacogram(ibi1)
    detected = _error_detection(tacogram_o)
    if correction:
        corrected = _error_correction(detected)
    else:
        corrected = detected
    return corrected[['IBI', 'ERROR', 'CORRECTED']]


def __print_diff_ibi(ibi):
    try:
        ibi1 = ibi.loc[ibi['ERROR'] == 0]
    except KeyError:
        ibi1 = ibi
    signal = ibi1[['IBI']] * 1000
    diff = np.concatenate(([0], np.diff(np.array(signal).flatten())))
    plt.figure(1)
    plt.scatter(signal['IBI'][:-1], signal['IBI'][1:], s=2)
    plt.title('IBI diff')
    plt.xlabel('IBI(t-1) [ms]')
    plt.ylabel('IBI(t) [ms]')
    plt.grid()
    plt.figure(2)
    # best fit of data
    (mu, sigma) = norm.fit(diff)  # mean and standard deviation
    print('TOTAL -> pos_mean = {:.5f}, pos_std = {:.5f}, neg_mean = {:.5f}, neg_std = {:.5f}'.format(
        np.mean(diff[diff > 0]), np.std(diff[diff > 0]), np.mean(diff[diff < 0]), np.std(diff[diff < 0])))
    count, bins, ignored = plt.hist(diff, 100, density=1)
    y = norm.pdf(bins, mu, sigma)
    plt.plot(bins, y, 'r--', linewidth=2)
    plt.title('Histogram diff IBI')
    plt.ylabel('Prob')
    plt.xlabel('ms')
    plt.show()
    limits = [500, 700, 900]  # ms
    diffs = list()
    diffs.append(np.diff(np.array(signal.loc[(signal['IBI'] < limits[0])]).flatten()))
    for i in range(0, len(limits) - 1):
        diffs.append(np.diff(np.array(signal.loc[(limits[i] < signal['IBI']) & (signal['IBI'] < limits[i + 1])]).
                             flatten()))
    diffs.append(np.diff(np.array(signal.loc[(limits[-1] < signal['IBI'])]).flatten()))
    for j in range(0, len(limits)):
        if diffs[j][diffs[j] > 0].size != 0:
            print('IBI < {} -> pos_mean = {:.5f}, pos_std = {:.5f}, neg_mean = {:.5f}, neg_std = {:.5f}'.
                  format(limits[j], np.mean(diffs[j][diffs[j] > 0]), np.std(diffs[j][diffs[j] > 0]),
                         np.mean(diffs[j][diffs[j] < 0]), np.std(diffs[j][diffs[j] < 0])))
    print('IBI > {} -> pos_mean = {:.5f}, pos_std = {:.5f}, neg_mean = {:.5f}, neg_std = {:.5f}'.
          format(limits[-1], np.mean(diffs[-1][diffs[-1] > 0]), np.std(diffs[-1][diffs[-1] > 0]),
                 np.mean(diffs[-1][diffs[-1] < 0]), np.std(diffs[-1][diffs[-1] < 0])))
