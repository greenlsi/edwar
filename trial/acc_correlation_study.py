import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, SecondLocator
from trial import csvmanage as cm


def _calculate_window(eda):
    init_count = 0
    peaks_duration = np.array([])
    eda_deriv = np.concatenate((np.array([0]), np.diff(eda)))

    for i in range(0, len(eda) - 1):
        if (eda_deriv[i] < 0) and (eda_deriv[i + 1] >= 0):
            peaks_duration = np.append(peaks_duration, [i - init_count])
            init_count = i
    mean_duration = np.mean(peaks_duration, dtype=np.float32)
    return mean_duration


def _transform_boxcox(x, landa):
    # to avoid divide by zero warnings
    offset = 0.0001
    if landa:
        y = (pow(x + offset, landa) - 1) / landa
    else:
        y = np.log(x + offset)

    return y


def _calculate_xyz(data):
    x = data.loc[:, 'AccelX']  # x-axis
    y = data.loc[:, 'AccelY']  # y-axis
    z = data.loc[:, 'AccelZ']  # z-axis

    x_y_z = np.sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2))
    xyz = np.concatenate((np.array([0]), np.diff(x_y_z)))

    return xyz


def thresholding(data, var_acc_thrld, var_eda_thrld, window=8, delay=0, to_print_deleted=False, detailed_axis=False,
                 to_use_transform=True):
    d = data.loc[:, ['EDA', 'AccelX', 'AccelY', 'AccelZ']]
    d.loc[:, 'ACC'] = _calculate_xyz(d)

    var_eda, var_acc, correlation = calculate_correlation(d.loc[:, 'EDA'], d.loc[:, 'ACC'], window, delay,
                                                          to_correlate=False, to_use_transform=to_use_transform)
    d.loc[:, 'var_eda'] = np.concatenate((var_eda, np.zeros(window)))
    deleted = np.zeros(len(data))
    var_acc_thrld_t = _transform_boxcox(var_acc_thrld, 0) if to_use_transform else var_acc_thrld

    if var_eda_thrld:
        deleted[d.var_eda < var_eda_thrld] = 1
        d.loc[:, 'var_acc'] = np.concatenate((var_acc, np.zeros(window)))
    else:
        deleted[d.var_acc < var_acc_thrld_t] = 1

    if to_print_deleted:
        print_data(d, deleted, detailed_axis=detailed_axis)
    d = d[deleted == 0]
    correlation = round(np.corrcoef(d.loc[:, 'var_eda'], d.loc[:, 'var_acc'])[0, 1], 7)

    return d, correlation


def print_data(data, deleted, detailed_axis=False):
    first_deleted = 1
    fig, axs = plt.subplots(2, 1, figsize=(20, 20))
    axs[0].plot(data.index, data['EDA'], 'b', label='EDA')
    axs[1].plot(data.index, data['ACC'], 'b', label='ACC')
    for i in range(0, len(deleted) - 1):
        if deleted[i]:
            if first_deleted:
                axs[0].axvspan(data.index[i], data.index[i + 1], facecolor='red', alpha=0.7, edgecolor='none',
                               label='deleted')
                axs[1].axvspan(data.index[i], data.index[i + 1], facecolor='red', alpha=0.7, edgecolor='none',
                               label='deleted')
                first_deleted = 0
            else:
                axs[0].axvspan(data.index[i], data.index[i + 1], facecolor='red', alpha=0.7, edgecolor='none')
                axs[1].axvspan(data.index[i], data.index[i + 1], facecolor='red', alpha=0.7, edgecolor='none')
    axs[0].legend(loc='upper right')
    axs[1].legend(loc='upper right')
    formatter = DateFormatter('%H:%M:%S')
    bysecond = range(60)
    plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
    plt.gcf().axes[1].xaxis.set_major_formatter(formatter)

    if detailed_axis:
        plt.gcf().axes[0].xaxis.set_major_locator(SecondLocator(bysecond=[0, 15, 30, 45]))
        plt.gcf().axes[0].xaxis.set_minor_locator(SecondLocator(bysecond=bysecond))
        plt.gcf().axes[1].xaxis.set_major_locator(SecondLocator(bysecond=[0, 15, 30, 45]))
        plt.gcf().axes[1].xaxis.set_minor_locator(SecondLocator(bysecond=bysecond))
    plt.show()


def calculate_correlation(eda, xyz, window, delay, to_correlate=True, to_use_transform=True):
    var_eda = np.zeros(len(eda) - window)
    var_acc = np.zeros(len(xyz) - window)
    var_acct = np.zeros(len(xyz) - window)
    max_iter = len(eda) - (delay + window)

    for i in range(0, max_iter):
        var_eda[i] = np.var(eda[(i + delay):(i + delay + window)])
        var_acc[i] = np.var(xyz[i:(i + window - 1)])
        var_acct[i] = _transform_boxcox(var_acc[i], 0) if to_use_transform else var_acc[i]

    correlation = 0
    if to_correlate:
        correlation = round(np.corrcoef(var_eda, var_acct)[0, 1], 5)

    return var_eda, var_acct, correlation


def calculate_correlation_per_axis(data, window, d):
    f = 1 / cm.get_seconds_and_microseconds(data.index[1] - data.index[0])
    x = np.concatenate((np.array([0]), np.diff(data['AccelX'].values)))  # x-axis
    y = np.concatenate((np.array([0]), np.diff(data['AccelY'].values)))  # y-axis
    z = np.concatenate((np.array([0]), np.diff(data['AccelZ'].values)))  # z-axis
    eda = data['EDA'].values
    var_eda = np.zeros(len(data) - window)
    var_x = np.zeros(len(data) - window)
    var_xt = np.zeros(len(data) - window)
    var_y = np.zeros(len(data) - window)
    var_yt = np.zeros(len(data) - window)
    var_z = np.zeros(len(data) - window)
    var_zt = np.zeros(len(data) - window)
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
    axs[0].set_title('window = {} s    delay = {} s\n correlation = {}'.format(window / f, d / f, correlation_x))
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


def plot_josue_graph(var_eda, var_acc, correlation, window, d, o, f):
    plt.plot(var_eda, var_acc, 'ro', markersize=1)
    plt.xlabel('var EDA')
    plt.ylabel('var ACC')
    plt.title('window = {} s  delay = {} s\n correlation = {}  offset = {}'.format(window / f, d / f, correlation, o))
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
    WINDOW = 16
    DELAY = 2
    OFFSET = 0.05
    TRANSFORM = False
    print('loading data........................................0%')
    DATA = cm.downsample_to_1hz(cm.load_results(directory))[0:10000]
    EDA = DATA['EDA']

    # mean_time = _calculate_window(EDA)
    # print('Mean samples per peak' % mean_time)
    # var_EDA = plot_eda_histogram(DATA, w, directory[8:])

    # print('calculting correlation & printing graphs per axis...1%')
    # var_X, var_Y, var_Z = calculate_correlation_per_axis(DATA, w, delay)

    print('calculating unified accelerometer data..............40%')
    ACC = _calculate_xyz(DATA)
    print('calculating correlation.............................50%')
    OUT_DATA, CORRCOEF = thresholding(DATA, 0, OFFSET, window=WINDOW, delay=DELAY, to_print_deleted=True,
                                      to_use_transform=TRANSFORM)
    var_EDA, var_ACCt, cor = calculate_correlation(EDA, ACC, WINDOW, DELAY, to_use_transform=TRANSFORM)

    print('printing graph......................................80%')
    frequency = 1 / cm.get_seconds_and_microseconds(DATA.index[1] - DATA.index[0])
    plot_josue_graph(var_EDA, var_ACCt, cor, WINDOW, DELAY, 0, frequency)
    plot_josue_graph(OUT_DATA.loc[:, 'var_eda'], OUT_DATA.loc[:, 'var_acc'], CORRCOEF, WINDOW, DELAY, OFFSET, frequency)

    print('process finished....................................100%')
