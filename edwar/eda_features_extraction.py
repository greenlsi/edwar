import matplotlib.pyplot as plt
import ledapy
from numpy import array as npa
from matplotlib.dates import DateFormatter
from edwar import csvmanage as cm


def calculate_eda_features(eda_data):

    sampling_rate = 1/cm.get_seconds_and_microseconds(eda_data.index[1]-eda_data.index[0])
    rawdata = npa(eda_data['EDA'], dtype='float64')
    rawdata = rawdata.flatten()
    phasicdata = ledapy.runner.getResult(rawdata, 'phasicdata', sampling_rate, downsample=1, optimisation=0)
    phasic = phasicdata.tolist()
    eda_data['phasic'] = phasic
    # EDAdata['tonic'] = EDAdata['filtered'] - EDAdata['phasic']
    eda_data['tonic'] = ledapy.runner.leda2.analysis.tonicData

    return eda_data


def plot_scl(eda_data):

    day, month, year = cm.get_date(eda_data.index[0])
    plt.figure(1, figsize=(20, 5))
    plt.title('SC, SCL and SCR \n {0}/{1}/{2}'.format(day, month, year))
    plt.ylabel('$\mu$S')
    formatter = DateFormatter('%H:%M:%S')
    plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
    plt.xlabel('Time')
    plt.plot(eda_data.index, eda_data['EDA'], '#9F33BD', label='SC')
    plt.plot(eda_data.index, eda_data['filtered_eda'], '#2a3282', label='filtered SC')

    try:
        plt.plot(eda_data.index, eda_data['tonic'], '#2e352c', label='SCL')
        plt.plot(eda_data.index, eda_data['phasic'], '#ffa500', label='SCR')
    except KeyError:
        raise KeyError('SCL & SCR not calculated yet, execute first calculate_eda_features()')

    plt.legend(loc='upper right')
    data_min = min(eda_data['phasic'])
    data_max = max(eda_data['EDA'])
    plt.xlim([eda_data.index[0], eda_data.index[-1]])
    plt.ylim([min(0, data_min), data_max * 1.15])
    plt.show()


if __name__ == '__main__':
    from edwar import eda_module as ed
    # Prueba:
    directory = '../data/ejemplo1'
    EDA = cm.load_results_e4(directory)[0].loc[:, ['EDA']]
    EDA = EDA[0:10000]
    EDA['filtered_eda'] = ed.butter_lowpass_filter(EDA['EDA'], 1.0, 8, 6)
    EDA = cm.downsample_to_1hz(EDA)

    EDA = calculate_eda_features(EDA)
    print(EDA)
    plot_scl(EDA)
    # cm.save_results(EDA, 'results.csv')
