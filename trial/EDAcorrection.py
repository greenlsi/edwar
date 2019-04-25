import numpy as np
import matplotlib.pyplot as plt
import pywt
from matplotlib.dates import DateFormatter
from trial import csvmanage as cm

directory = '../data/ejemplo'
EDAdata = cm.load_results(directory + '/EDA.csv', 0)
ACCdata = cm.load_acc(directory + '/ACC.csv', 0)[EDAdata.index[0]:EDAdata.index[-1]]


def accelerometer_study(ACCdata):
    ACCx = np.array(ACCdata['x'], dtype='float64')
    ACCy = np.array(ACCdata['y'], dtype='float64')
    ACCz = np.array(ACCdata['z'], dtype='float64')
    plt.figure(3, figsize=(8, 5))
    plt.hist(ACCdata['x'], bins='auto', label='x', alpha=0.5, color='#ff0000')
    plt.hist(ACCdata['y'], bins='auto', label='y', alpha=0.5, color='#ffdd00')
    plt.hist(ACCdata['z'], bins='auto', label='z', alpha=0.5, color='#0011ff')
    plt.legend(loc='upper right')
    plt.title('Distribution values x,y,z')
    text1 = 'x: $\mu={0},\ \sigma={1}$\n'.format(round(ACCx.mean(), 2), round(ACCx.var(), 2))
    text2 = 'y: $\mu={0},\ \sigma={1}$\n'.format(round(ACCy.mean(), 2), round(ACCy.var(), 2))
    text3 = 'z: $\mu={0},\ \sigma={1}$  '.format(round(ACCz.mean(), 2), round(ACCz.var(), 2))
    text = text1+text2+text3
    plt.figtext(0.1, 0.8, text, bbox=dict(facecolor='red', alpha=0.5))
    plt.show()


def evaluate_reliability_acc(EDAdata, ACCdata, size_window=10):
    EDAdata['unreliable'] = np.zeros(len(EDAdata))
    ACCy = np.array(ACCdata['y'], dtype='float64')
    for i in reversed(range(size_window, len(ACCy)-size_window, size_window)):
        if abs(ACCy[i-size_window: i+size_window].var()) > 25:
            EDAdata['unreliable'][i - size_window: i + size_window] = np.ones(2 * size_window)
        else:
            EDAdata['unreliable'][i - size_window: i + size_window] = np.zeros(2 * size_window)

    return EDAdata


def correct_EDA(EDAdata):
    EDA = np.array(EDAdata['medida'], dtype='float64')
    type_of_wavelet = 'haar'
    # print(pywt.swt_max_level(len(EDA)))
    coeff = pywt.swt(EDA, type_of_wavelet, 7, 0, 0)
    EDAdata['od1'] = coeff[0][1]
    for i in range(0, len(coeff[0][0])):
        for j in range(0, len(coeff)):
            if abs(coeff[j][1][i]) > 5 or EDAdata['unreliable'][i]:
                coeff[j][1][i] = 0

    EDAcorrected = pywt.iswt(coeff, type_of_wavelet)
    EDAdata['corrected'] = EDAcorrected
    EDAdata['a1'] = coeff[0][0]
    EDAdata['a2'] = coeff[1][0]
    EDAdata['a3'] = coeff[2][0]
    EDAdata['a4'] = coeff[3][0]
    EDAdata['a5'] = coeff[4][0]
    EDAdata['a6'] = coeff[5][0]
    EDAdata['a7'] = coeff[6][0]
    EDAdata['d1'] = coeff[0][1]
    EDAdata['d2'] = coeff[1][1]
    EDAdata['d3'] = coeff[2][1]
    EDAdata['d4'] = coeff[3][1]
    EDAdata['d5'] = coeff[4][1]
    EDAdata['d6'] = coeff[5][1]
    EDAdata['d7'] = coeff[6][1]

    return EDAdata


def plotEDA(EDAdata, ACCdata, reliability):
    data_min = min(EDAdata['medida'])
    data_max = max(EDAdata['medida'])
    day, month, year = cm.get_date(EDAdata.index[0])

    fig, axs = plt.subplots(4, 1, figsize=(20, 20))
    axs[0].set_title('{0}/{1}/{2} \nSkin Conductance'.format(day, month, year))
    axs[0].set_xlim([EDAdata.index[0], EDAdata.index[-1]])
    # y_min = min(0, data_min) - (data_max - data_min) * 0.1
    axs[0].set_ylim([min(0, data_min), data_max * 1.15])
    axs[0].set_ylabel('$\mu$S')
    formatter = DateFormatter('%H:%M:%S')
    plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
    axs[0].set_xlabel('Time')
    if reliability:
        axs[0].plot(EDAdata.index, EDAdata['unreliable']*data_max*1.15, '#cc7a7a', label='not reliable', alpha=0.5)
        axs[0].fill_between(EDAdata.index, EDAdata['unreliable']*data_max*1.15, color='#cc7a7a', alpha=0.5)
    axs[0].plot(EDAdata.index, EDAdata['medida'], '#9F33BD', label='original')
    axs[0].plot(EDAdata.index, EDAdata['corrected'], '#2e352c', label='corrected', alpha=0.8)
    axs[0].legend(loc='upper right')

    axs[1].set_title('Accelerometer data')
    axs[1].set_xlim([ACCdata.index[0], ACCdata.index[-1]])
    # y_min = min(0, data_min) - (data_max - data_min) * 0.1
    axs[1].set_ylim([min(min(ACCdata['x']), min(ACCdata['y']), min(ACCdata['z'])),
                     max(max(ACCdata['x']), max(ACCdata['y']), max(ACCdata['z']))])
    axs[1].set_ylabel('acceleration')
    plt.gcf().axes[1].xaxis.set_major_formatter(formatter)
    axs[1].set_xlabel('Time')
    # plt.plot(EDAdata.index, EDAdata['phasic'], '#6d1013') #red
    axs[1].plot(ACCdata.index, ACCdata['x'], '#31d63c', label='x', alpha=0.7)
    axs[1].plot(ACCdata.index, ACCdata['y'], '#a37e22', label='y', alpha=0.7)
    axs[1].plot(ACCdata.index, ACCdata['z'], '#a22222', label='z', alpha=0.7)
    axs[1].legend(loc='upper right')

    axs[2].set_xlim([EDAdata.index[0], EDAdata.index[-1]])
    axs[2].set_title('Approximation coefficients')
    # y_min = min(0, data_min) - (data_max - data_min) * 0.1
    axs[2].set_ylim([min(min(EDAdata['a1']), min(EDAdata['a7'])),
                     max(max(EDAdata['a1']), max(EDAdata['a7']))])
    axs[2].set_ylabel('$\mu$S')
    plt.gcf().axes[2].xaxis.set_major_formatter(formatter)
    axs[2].set_xlabel('Time')
    axs[2].plot(EDAdata.index, EDAdata['a1'], '#cdadd6')  # mas claro
    axs[2].plot(EDAdata.index, EDAdata['a2'], '#c394d1')
    axs[2].plot(EDAdata.index, EDAdata['a3'], '#b667ce')
    axs[2].plot(EDAdata.index, EDAdata['a4'], '#ae44ce')
    axs[2].plot(EDAdata.index, EDAdata['a5'], '#9e1fc4')
    axs[2].plot(EDAdata.index, EDAdata['a6'], '#700191')
    axs[2].plot(EDAdata.index, EDAdata['a7'], '#48005e')  # mas oscuro

    axs[3].set_xlim([EDAdata.index[0], EDAdata.index[-1]])
    axs[3].set_title('Detail coefficients')
    # y_min = min(0, data_min) - (data_max - data_min) * 0.1
    axs[3].set_ylim([min(min(EDAdata['d1']), min(EDAdata['d1'])),
                     max(max(EDAdata['d1']), max(EDAdata['d1']))])
    axs[3].set_ylabel('$\mu$S')
    plt.gcf().axes[3].xaxis.set_major_formatter(formatter)
    axs[3].set_xlabel('Time')
    axs[3].plot(EDAdata.index, EDAdata['d2'], '#000000')

    plt.figure(2, figsize=(20, 10))
    plt.hist(EDAdata['od1'], bins='auto', label='initial d1', color='#0011ff')
    plt.hist(EDAdata['d1'], bins='auto', label='final d1', color='#ff0000')
    plt.legend(loc='upper right')
    plt.title('Histogram of detail coefficients')
    plt.show()


evaluate_reliability_acc(EDAdata, ACCdata)
EDAdata = correct_EDA(EDAdata)
plotEDA(EDAdata, ACCdata, 1)
# accelerometer_study(ACCdata)


