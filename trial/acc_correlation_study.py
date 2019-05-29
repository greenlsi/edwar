import numpy as np
import matplotlib.pyplot as plt
from math import ceil
from trial import csvmanage as cm


def _calculate_window(eda):
    init_count = 0
    peaks_duration = np.array([])
    eda_deriv = np.concatenate((np.array([0]), np.diff(eda)))

    for i in range(0, len(eda)-1):
        if (eda_deriv[i] < 0) and (eda_deriv[i+1] >= 0):
            peaks_duration = np.append(peaks_duration, [i - init_count])
            init_count = i
    mean_duration = np.mean(peaks_duration, dtype=np.float32)
    return mean_duration


def _transform_boxcox(x, landa):
    # to avoid divide by zero warnings
    offset = 0.0001
    if landa:
        y = (pow(x + offset, landa) - 1)/landa
    else:
        y = np.log(x + offset)

    return y


def _calculate_xyz(data):
    x = data['AccelX'].values  # x-axis
    y = data['AccelY'].values  # y-axis
    z = data['AccelZ'].values  # z-axis

    x_y_z = np.sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2))
    xyz = np.concatenate((np.array([0]), np.diff(x_y_z)))

    return xyz


def calculate_correlation(eda, xyz, window, d, var_offset_eda):
    var_eda = np.zeros(len(eda)-window)
    var_acc = np.zeros(len(xyz) - window)
    var_acct = np.zeros(len(xyz)-window)
    max_iter = len(eda) - (d + window)

    for i in range(0, max_iter):
        if np.var(eda[(i + d):(i + d + window - 1)]) >= var_offset_eda:
            var_eda[i] = np.var(eda[(i + d):(i + d + window)])
        else:
            var_eda[i] = 0
        var_acc[i] = np.var(xyz[i:(i+window-1)])
        var_acct[i] = _transform_boxcox(var_acc[i], 0)

    correlation = round(np.corrcoef(var_eda, var_acct)[0, 1], 5)

    return var_eda, var_acct, correlation, var_acc


def calculate_correlation_per_axis(data, window, d):
    x = np.concatenate((np.array([0]), np.diff(data['AccelX'].values)))  # x-axis
    y = np.concatenate((np.array([0]), np.diff(data['AccelY'].values)))  # y-axis
    z = np.concatenate((np.array([0]), np.diff(data['AccelZ'].values)))  # z-axis
    eda = data['EDA'].values
    var_eda = np.zeros(len(data)-window)
    var_x = np.zeros(len(data)-window)
    var_xt = np.zeros(len(data)-window)
    var_y = np.zeros(len(data)-window)
    var_yt = np.zeros(len(data)-window)
    var_z = np.zeros(len(data)-window)
    var_zt = np.zeros(len(data)-window)
    max_iter = len(data) - (d + window)
    landa = 0

    for i in range(0, max_iter):
        var_eda[i] = np.var(eda[(i + d):(i + d + window)])
        var_x[i] = np.var(x[i:(i + window)])
        var_y[i] = np.var(y[i:(i + window)])
        var_z[i] = np.var(z[i:(i + window)])
        var_xt[i] = _transform_boxcox(var_x[i], landa)
        var_yt[i] = _transform_boxcox(var_y[i], landa)
        var_zt[i] = _transform_boxcox(var_z[i], landa)
    '''
    for i in range(0, max_iter):
        var_eda[i] = np.var(eda[(i + d):(i + d + window - 1)])
        var_x[i] = np.var(x[i:(i + window - 1)])
        var_y[i] = np.var(y[i:(i + window - 1)])
        var_z[i] = np.var(z[i:(i + window - 1)])
    '''
    correlation_x = round(np.corrcoef(var_eda, var_xt)[0, 1], 2)
    correlation_y = round(np.corrcoef(var_eda, var_yt)[0, 1], 2)
    correlation_z = round(np.corrcoef(var_eda, var_zt)[0, 1], 2)
    fig, axs = plt.subplots(3, 1)
    axs[0].set_title('window = {} s    delay = {} s\n correlation = {}'.format(window / 8, d / 8, correlation_x))
    axs[0].plot(var_eda, var_xt, 'ro', markersize=1)
    axs[0].set_xlabel('var EDA')
    axs[0].set_ylabel('var X')
    axs[1].set_title('correlation = {}'.format(correlation_y))
    axs[1].plot(var_eda, var_yt, 'ro', markersize=1)
    axs[1].set_xlabel('var EDA')
    axs[1].set_ylabel('var Y')
    axs[2].set_title('correlation = {}'.format(correlation_z))
    axs[2].plot(var_eda, var_zt, 'ro', markersize=1)
    axs[2].set_xlabel('var EDA')
    axs[2].set_ylabel('var Z')
    plt.show()

    return var_x, var_y, var_z


def plot_josue_graph(var_eda, var_acc, correlation, window, d, o):
    plt.plot(var_eda, var_acc, 'ro', markersize=1)
    plt.xlabel('var EDA')
    plt.ylabel('var ACC')
    plt.title('window = {} s    delay = {} s\n correlation = {}    offset = {}'.format(window / 8, d / 8, correlation,
                                                                                       o))
    plt.show()


def plot_eda_histogram(data, window, d):
    eda = data['EDA'].values
    max_iter = len(eda) - window
    var_eda = np.zeros(max_iter)
    for i in range(0, max_iter):
        var_eda[i] = np.var(eda[i:(i + window)])
    plt.hist(var_eda, 5000)
    print('histogram ready!')
    xmin = 0
    xmax = 0.01
    ymin = 0
    ymax = 200
    plt.axis([xmin, xmax, ymin, ymax])
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))
    plt.gca().xaxis.set_minor_locator(plt.MaxNLocator(100))
    plt.grid(b=True, which='both', alpha=0.7)
    plt.title('{}\n window = {}'.format(d, window))
    plt.show()
    return var_eda


if __name__ == '__main__':
    directory = '../data/ejemplo3'
    w = 8
    delay = 0
    OFFSET = 0
    print('loading data........................................0%')
    DATA = cm.load_results(directory)
    EDA = DATA['EDA']
    mean_time = _calculate_window(EDA)
    print('Mean time of a peak = %f s ==> %d samples' % (round(mean_time/8, 4), ceil(mean_time)))
    # var_EDA = plot_eda_histogram(DATA, w, directory[8:])

    # print('calculting correlation & printing graphs per axis...1%')
    # var_X, var_Y, var_Z = calculate_correlation_per_axis(DATA, w, delay)
    '''
    print('calculating unified accelerometer data..............40%')
    EDA = DATA['EDA']
    ACC = _calculate_xyz(DATA)
    print('calculating correlation.............................50%')
    var_EDA, var_ACCt, cor, var_ACC = calculate_correlation(EDA, ACC, w, delay, OFFSET)

    print('printing graph......................................80%')
    plot_josue_graph(var_EDA, var_ACCt, cor, w, delay, OFFSET)
    '''
    print('process finished....................................100%')
