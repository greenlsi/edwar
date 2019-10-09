import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pywt
from matplotlib.dates import DateFormatter
from . import csvmanage as cm
from .eda_explorer.load_files import butter_lowpass_filter


def accelerometer_study(acc_data):
    acc_x = np.array(acc_data['AccelX'], dtype='float64')
    acc_y = np.array(acc_data['AccelY'], dtype='float64')
    acc_z = np.array(acc_data['AccelZ'], dtype='float64')
    plt.figure(3, figsize=(8, 5))
    plt.hist(acc_data['AccelX'], bins='auto', label='x', alpha=0.5, color='#ff0000')
    plt.hist(acc_data['AccelY'], bins='auto', label='y', alpha=0.5, color='#ffdd00')
    plt.hist(acc_data['AccelZ'], bins='auto', label='z', alpha=0.5, color='#0011ff')
    plt.legend(loc='upper right')
    plt.title('Distribution values x,y,z')
    text1 = 'x: $\mu={0},\ \sigma={1}$\n'.format(round(acc_x.mean(), 2), round(acc_x.var(), 2))
    text2 = 'y: $\mu={0},\ \sigma={1}$\n'.format(round(acc_y.mean(), 2), round(acc_y.var(), 2))
    text3 = 'z: $\mu={0},\ \sigma={1}$  '.format(round(acc_z.mean(), 2), round(acc_z.var(), 2))
    text = text1+text2+text3
    plt.figtext(0.1, 0.8, text, bbox=dict(facecolor='red', alpha=0.5))
    plt.show()


def evaluate_reliability_acc(data, size_window=10):
    data['unreliable'] = np.zeros(len(data))
    acc_y = np.array(data['AccelY'], dtype='float64')
    for i in reversed(range(size_window, len(acc_y)-size_window, size_window)):
        if abs(acc_y[i-size_window: i+size_window].var()) > 25:
            data['unreliable'][i - size_window: i + size_window] = np.ones(2 * size_window)
        else:
            data['unreliable'][i - size_window: i + size_window] = np.zeros(2 * size_window)

    return data


def correct_eda(eda_data, thr, test=0):
    eda = eda_data['EDA'].values
    k = 0
    olen = len(eda)
    while k*np.power(2, 7) < olen:
        k = k + 1
    diff = k*np.power(2, 7) - olen
    eda = np.pad(eda, (0, diff), 'constant', constant_values=0)
    type_of_wavelet = 'haar'
    coeff = pywt.swt(eda, type_of_wavelet, 7, 0, 0)
    od1 = coeff[0][1][0:olen]
    for i in range(0, len(coeff[0][0])):
        for j in range(0, len(coeff)):
            if abs(coeff[j][1][i]) > thr:
                coeff[j][1][i] = 0

    eda_corrected = pywt.iswt(coeff, type_of_wavelet)[0:olen]
    out = pd.DataFrame(np.array(eda_corrected), index=eda_data['EDA'].index)
    out.columns = ['EDA']
    out['filtered_eda'] = butter_lowpass_filter(out['EDA'], 1.0, 8, 6)

    if test:
        out['od1'] = od1
        out['a1'] = coeff[0][0][0:olen]
        out['a2'] = coeff[1][0][0:olen]
        out['a3'] = coeff[2][0][0:olen]
        out['a4'] = coeff[3][0][0:olen]
        out['a5'] = coeff[4][0][0:olen]
        out['a6'] = coeff[5][0][0:olen]
        out['a7'] = coeff[6][0][0:olen]

        out['d1'] = coeff[0][1][0:olen]
        out['d2'] = coeff[1][1][0:olen]
        out['d3'] = coeff[2][1][0:olen]
        out['d4'] = coeff[3][1][0:olen]
        out['d5'] = coeff[4][1][0:olen]
        out['d6'] = coeff[5][1][0:olen]
        out['d7'] = coeff[6][1][0:olen]

    return out


def _plot_eda(data, out, reliability):
    data_min = min(data['EDA'])
    data_max = max(data['EDA'])
    day, month, year = cm.get_date(data.index[0])

    fig, axs = plt.subplots(4, 1, figsize=(20, 20))
    axs[0].set_title('{0}/{1}/{2} \nSkin Conductance'.format(day, month, year))
    axs[0].set_xlim([data.index[0], data.index[-1]])
    # y_min = min(0, data_min) - (data_max - data_min) * 0.1
    axs[0].set_ylim([min(0, data_min), data_max * 1.15])
    axs[0].set_ylabel('$\mu$S')
    formatter = DateFormatter('%H:%M:%S')
    plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
    axs[0].set_xlabel('Time')
    if reliability:
        axs[0].plot(data.index, data['unreliable']*data_max*1.15, '#cc7a7a', label='not reliable', alpha=0.5)
        axs[0].fill_between(data.index, data['unreliable']*data_max*1.15, color='#cc7a7a', alpha=0.5)
    axs[0].plot(data.index, data['EDA'], '#9F33BD', label='original')
    axs[0].plot(data.index, out['EDA'], '#2e352c', label='corrected', alpha=0.8)
    axs[0].legend(loc='upper right')

    axs[1].set_title('Accelerometer data1')
    axs[1].set_xlim([data.index[0], data.index[-1]])
    # y_min = min(0, data_min) - (data_max - data_min) * 0.1
    axs[1].set_ylim([min(min(data['AccelX']), min(data['AccelY']), min(data['AccelZ'])),
                     max(max(data['AccelX']), max(data['AccelY']), max(data['AccelZ']))])
    axs[1].set_ylabel('acceleration')
    plt.gcf().axes[1].xaxis.set_major_formatter(formatter)
    axs[1].set_xlabel('Time')
    # plt.plot(EDAdata.index, EDAdata['phasic'], '#6d1013') #red
    axs[1].plot(data.index, data['AccelX'], '#31d63c', label='x', alpha=0.7)
    axs[1].plot(data.index, data['AccelY'], '#a37e22', label='y', alpha=0.7)
    axs[1].plot(data.index, data['AccelZ'], '#a22222', label='z', alpha=0.7)
    axs[1].legend(loc='upper right')

    axs[2].set_xlim([data.index[0], data.index[-1]])
    axs[2].set_title('Approximation coefficients')
    # y_min = min(0, data_min) - (data_max - data_min) * 0.1
    axs[2].set_ylim([min(min(out['a1']), min(out['a1'])),
                     max(max(out['a1']), max(out['a1']))])
    axs[2].set_ylabel('$\mu$S')
    plt.gcf().axes[2].xaxis.set_major_formatter(formatter)
    axs[2].set_xlabel('Time')
    axs[2].plot(out.index, out['a1'], '#cdadd6')  # mas claro
    axs[2].plot(out.index, out['a2'], '#c394d1')
    axs[2].plot(out.index, out['a3'], '#b667ce')
    axs[2].plot(out.index, out['a4'], '#ae44ce')
    axs[2].plot(out.index, out['a5'], '#9e1fc4')
    axs[2].plot(out.index, out['a6'], '#700191')
    axs[2].plot(out.index, out['a7'], '#48005e')  # mas oscuro
    # axs[3].set_xlim([data1.index[0], data1.index[-1]])
    axs[3].set_title('Detail coefficients')
    # y_min = min(0, data_min) - (data_max - data_min) * 0.1
    axs[3].set_ylim([min(min(out['d1']), min(out['d7'])),
                     max(max(out['d1']), max(out['d7']))])
    axs[3].set_ylabel('$\mu$S')
    plt.gcf().axes[3].xaxis.set_major_formatter(formatter)
    axs[3].set_xlabel('Time')
    axs[3].plot(out.index, out['d1'], '#000000')

    plt.figure(2, figsize=(20, 10))
    plt.hist(out['od1'], bins='auto', label='initial d1', color='#0011ff')
    plt.hist(out['d1'], bins='auto', label='final d1', color='#ff0000')
    plt.legend(loc='upper right')
    plt.title('Histogram of detail coefficients')
    plt.show()


if __name__ == '__main__':
    testing = 1
    directory = '../data1/ejemplo1'
    EDAdata = cm.load_results_e4(directory)[0:10000]
    evaluate_reliability_acc(EDAdata)
    EDAout = correct_eda(EDAdata, 1.5, testing)

    if testing:
        _plot_eda(EDAdata, EDAout, 1)
    else:
        print(EDAout)
    # accelerometer_study(ACCdata)
