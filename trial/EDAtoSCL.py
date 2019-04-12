# import numpy as np
# import os
import matplotlib.pyplot as plt
from numpy import array as npa
from matplotlib.dates import DateFormatter
from trial import csvmanage as cm
from trial import Ledapy as ledapy



def calculateEDAfeatures(EDAdata):

    sampling_rate = 100
    rawdata = npa(EDAdata['filtered'], dtype='float64')
    rawdata = rawdata.flatten()
    phasicdata = ledapy.runner.getResult(rawdata, 'phasicdata', sampling_rate, downsample=1, optimisation=2)
    phasic = phasicdata.tolist()
    EDAdata['phasic'] = phasic
    # EDAdata['tonic'] = EDAdata['filtered'] - EDAdata['phasic']
    EDAdata['tonic'] = ledapy.leda2.analysis.tonicData

    return EDAdata


def plots(EDAdata):

    data_min = min(EDAdata['phasic'])
    data_max = max(EDAdata['medida'])
    day, month, year = cm.get_date(EDAdata.index[0])
    # Plot the data with the Peaks marked
    plt.figure(1, figsize=(20, 5))
    plt.xlim([EDAdata.index[0], EDAdata.index[-1]])
    # y_min = min(0, data_min) - (data_max - data_min) * 0.1
    plt.ylim([min(0, data_min), data_max * 1.15])
    plt.title('EDA (purple), EDA filtered (blue), SCL (gray) \n {0}/{1}/{2}'.format(day, month, year))
    plt.ylabel('$\mu$S')
    formatter = DateFormatter('%H:%M:%S')
    plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
    plt.xlabel('Time')
    # plt.plot(EDAdata.index, EDAdata['phasic'], '#6d1013') #red
    plt.plot(EDAdata.index, EDAdata['medida'], '#9F33BD')
    plt.plot(EDAdata.index, EDAdata['tonic'], '#2e352c')
    plt.plot(EDAdata.index, EDAdata['filtered'], '#2a3282')
    plt.show()



# Prueba:
directory = '../data/ejemplo'
EDA = cm.load_results(directory + '/EDA.csv', 0)[10:-60]
EDA = calculateEDAfeatures(EDA)
plots(EDA)
cm.save_results(EDA, 'results.csv')

