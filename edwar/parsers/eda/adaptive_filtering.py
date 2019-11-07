import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import timedelta
from edwar.parsers import eda as em
from edwar.parsers.eda import art_detect as ad, nlms as nm
from edwar.loaders import e4 as cm


def calculate_xyz(data):
    x = data['AccelX'].values  # x-axis
    y = data['AccelY'].values  # y-axis
    z = data['AccelZ'].values  # z-axis

    x_y_z = np.sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2))
    xyz = np.concatenate((np.array([0]), np.diff(x_y_z))) + np.mean(x_y_z)
    xyz_f = em.butter_lowpass_filter(xyz, 1.0, 8, 6)

    return xyz_f


def filt_accel(data, xyz, m=48, step=1.0, leak=0.0, init_coeffs=None, adaptive_step_factor=0.0001):
    d = data['EDA'].values
    u = xyz
    if init_coeffs is None:
        # aproximation of initial coefficients based on proximity 2 consecutive points
        yi, ei, wi = nm.nlms(u, d, m, 1, init_coeffs=init_coeffs, n=1)
    else:
        wi = init_coeffs

    y, e, w = nm.nlms(u, d, m, step, init_coeffs=wi, leak=leak, adaptive_step_factor=adaptive_step_factor)
    out = pd.DataFrame(y, index=data['EDA'].index[m-1:])
    '''np.concatenate((d[0:m - 1], y))'''
    out.columns = ['EDA']
    out['filtered_eda'] = em.butter_lowpass_filter(out['EDA'], 1.0, 8, 6)
    # out['filtered_eda'][0:4*6] = out['EDA'][0:4*6]  # margin to stabilize filter
    er = pd.DataFrame(np.concatenate((np.zeros(m-1), e)), index=data['EDA'].index)

    return out, er, w


def plot_eda(data, y, e, xyz, m, step, leak):
    first_artifact = 1
    first_questionable = 1
    classifier = ['Multiclass']
    feature_labels = ad.detect_arts(data, classifier)
    feature_labels_corrected = ad.detect_arts(y, classifier)
    # EDAdata['filterACC']
    fig, axs = plt.subplots(4, 1, figsize=(20, 20))
    axs[0].plot(y.index, y['EDA'], 'b', label='EDA')
    axs[0].plot(y.index, y['filtered_eda'], 'g', label='filtered EDA')
    for i in range(0, len(feature_labels_corrected)):
        start = feature_labels_corrected.index[i]
        end = start + timedelta(seconds=5)
        if feature_labels_corrected[classifier[0]][i] == -1:
            # artifact
            if first_artifact:
                axs[0].axvspan(start, end, facecolor='red', alpha=0.7, edgecolor='none', label='artifact')
                first_artifact = 0
            else:
                axs[0].axvspan(start, end, facecolor='red', alpha=0.7, edgecolor='none')
        elif feature_labels_corrected[classifier[0]][i] == 0:
            # Questionable
            if first_questionable:
                axs[0].axvspan(start, end, facecolor='.5', alpha=0.5, edgecolor='none', label='questionable')
                first_questionable = 0
            else:
                axs[0].axvspan(start, end, facecolor='.5', alpha=0.5, edgecolor='none')
    axs[0].legend(loc='upper right')
    axs[1].plot(data.index, data['EDA'], 'r', label='EDA')
    axs[1].plot(data.index, data['filtered_eda'], 'g', label='filtered EDA')
    axs[1].plot(y.index, y['EDA'], 'b', label='corrected EDA')
    first_artifact = 1
    first_questionable = 1
    for i in range(0, len(feature_labels) - 1):
        start = feature_labels.index[i]
        end = start + timedelta(seconds=5)
        if feature_labels[classifier[0]][i] == -1:
            # Artifact
            if first_artifact:
                axs[0].axvspan(start, end, facecolor='red', alpha=0.7, edgecolor='none', label='artifact')
                first_artifact = 0
            else:
                axs[0].axvspan(start, end, facecolor='red', alpha=0.7, edgecolor='none')
        elif feature_labels[classifier[0]][i] == 0:
            # Questionable
            if first_questionable:
                axs[1].axvspan(start, end, facecolor='.5', alpha=0.5, edgecolor='none', label='questionable')
                first_questionable = 0
            else:
                axs[1].axvspan(start, end, facecolor='.5', alpha=0.5, edgecolor='none')
    axs[1].legend(loc='upper right')
    formatter = DateFormatter('%H:%M:%S')
    plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
    plt.gcf().axes[1].xaxis.set_major_formatter(formatter)
    plt.gcf().axes[2].xaxis.set_major_formatter(formatter)
    xyz_min = min(xyz)
    xyz_max = max(xyz)
    axs[2].plot(e, 'g')
    axs[0].set_title('M = {}, STEP = {}, LEAK = {}\n corrected signal'.format(m, step, leak))
    axs[1].set_title('original signal')
    axs[2].set_title('error signal')
    axs[3].plot(xyz, '#31d63c', label='xyz')
    axs[3].set_title('accelerometer signal')
    axs[3].legend(loc='upper right')
    axs[3].set_ylim([xyz_min, xyz_max * 1.15])
    plt.show()


if __name__ == '__main__':
    directory = '../data/ejemplo3'
    eda_data = cm.load_files(directory)[0:10000]
    # [6000:7000] # [7500:8500] # [1500:2500 # [6000:7000] # [7800:8600]
    accel = calculate_xyz(eda_data)
    M = 12     # FIR filter taps
    STEP = 1   # FIR filter step
    LEAK = 0   # FIR filter leakage factor
    output, error, coeffs = filt_accel(eda_data, accel, m=M, step=STEP, leak=LEAK)
    print('order: {} \t mean: {} \t variance: {} \t '.format(M, np.mean(error), np.var(error)))
    plot_eda(eda_data, output, error, accel, M, STEP, LEAK)
