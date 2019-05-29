import numpy as np
import matplotlib.pyplot as plt
from trial import csvmanage as cm


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


def calculate_correlation(eda, xyz, window, d):
    var_eda = np.zeros(len(eda)-window + 1)
    var_acc = np.zeros(len(xyz) - window + 1)
    var_acct = np.zeros(len(xyz)-window + 1)
    max_iter = len(eda) - (d + window - 1)

    for i in range(0, max_iter):
        var_eda[i] = np.var(eda[(i + d):(i + d + window - 1)])
        var_acc[i] = np.var(xyz[i:(i+window-1)])
        var_acct[i] = _transform_boxcox(var_acc[i], 0)

    correlation = round(np.corrcoef(var_eda, var_acct)[0, 1], 2)

    return var_eda, var_acct, correlation, var_acc


def calculate_correlation_per_axis(data, window, d):
    x = np.concatenate((np.array([0]), np.diff(data['AccelX'].values)))  # x-axis
    y = np.concatenate((np.array([0]), np.diff(data['AccelY'].values)))  # y-axis
    z = np.concatenate((np.array([0]), np.diff(data['AccelZ'].values)))  # z-axis
    eda = data['EDA'].values
    var_eda = np.zeros(len(data)-window + 1)
    var_x = np.zeros(len(data)-window + 1)
    var_xt = np.zeros(len(data)-window + 1)
    var_y = np.zeros(len(data)-window + 1)
    var_yt = np.zeros(len(data)-window + 1)
    var_z = np.zeros(len(data)-window + 1)
    var_zt = np.zeros(len(data)-window + 1)
    max_iter = len(data) - (d + window - 1)
    landa = 0

    for i in range(0, max_iter):
        var_eda[i] = np.var(eda[(i + d):(i + d + window - 1)])
        var_x[i] = np.var(x[i:(i + window - 1)])
        var_y[i] = np.var(y[i:(i + window - 1)])
        var_z[i] = np.var(z[i:(i + window - 1)])
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


def plot_josue_graph(var_eda, var_acc, correlation, window, d):
    plt.plot(var_eda, var_acc, 'ro', markersize=1)
    plt.xlabel('var EDA')
    plt.ylabel('var ACC')
    plt.title('window = {} s    delay = {} s\n correlation = {}'.format(window / 8, d / 8, correlation))
    plt.show()


def plot_eda_histogram(data, window, d):
    eda = data['EDA'].values
    max_iter = len(eda) - (window - 1)
    var_eda = np.zeros(max_iter)
    for i in range(0, max_iter):
        var_eda[i] = np.var(eda[i:(i + window - 1)])
    plt.hist(var_eda, 70000)
    print('histogram ready')
    xmin = 0
    xmax = 0.1
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
    directory = '../data/ejemplo4'
    w = 8
    delay = 0
    print('loading data........................................0%')
    DATA = cm.load_results(directory)
    var_EDA = plot_eda_histogram(DATA, w, directory[8:])
    '''
    print('calculting correlation & printing graphs per axis...1%')
    # var_X, var_Y, var_Z = calculate_correlation_per_axis(DATA, w, delay)

    print('calculating unified accelerometer data..............40%')
    EDA = DATA['EDA']
    ACC = _calculate_xyz(DATA)
    print('calculating correlation.............................50%')
    var_EDA, var_ACCt, cor, var_ACC = calculate_correlation(EDA, ACC, w, delay)

    # plot_josue_histogram(var_EDA, var_ACC, var_X, var_Y, var_Z)
    print('printing graph......................................80%')
    plot_josue_graph(var_EDA, var_ACCt, cor, w, delay)
    '''
    print('process finished....................................100%')
