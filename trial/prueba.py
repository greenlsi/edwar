
import Ledapy as ledapy
import csvmanage as cm
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from numpy import array as npa



directory = '../data/ejemplo'
sampling_rate = 100
EDAdata = cm.load_results(directory + '/EDA.csv', 0)[10:-60]
rawdata = npa(EDAdata['filtered'], dtype='float64')
rawdata = rawdata.flatten()
phasicdata = ledapy.runner.getResult(rawdata, 'phasicdata', sampling_rate, downsample=1, optimisation=2)
phasic = phasicdata.tolist()
EDAdata['phasic'] = phasic
EDAdata['tonic'] = EDAdata['filtered']- EDAdata['phasic']
tonicdata = ledapy.leda2.analysis.phasicData
print(phasicdata.shape)
# phasicdata = ledapy.runner.getResult(rawdata, 'phasicdata', sampling_rate, downsample=1, optimisation=2)

data_min = min(EDAdata['phasic'])
data_max = max(EDAdata['medida'])
day, month, year = cm.get_date(EDAdata.index[0])
# Plot the data with the Peaks marked
plt.figure(1, figsize=(20, 5))
plt.xlim([EDAdata.index[0], EDAdata.index[-1]])
# y_min = min(0, data_min) - (data_max - data_min) * 0.1
plt.ylim([min(0, data_min), data_max * 1.15])
plt.title('EDA (purple), EDA filtered (blue), SCL (green) \n {0}/{1}/{2}'.format(day, month, year))
plt.ylabel('$\mu$S')
formatter = DateFormatter('%H:%M:%S')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.xlabel('Time')
# plt.plot(EDAdata.index, EDAdata['phasic'], '#6d1013') #red
plt.plot(EDAdata.index, EDAdata['medida'], '#9F33BD')
plt.plot(EDAdata.index, EDAdata['tonic'], '#4DBD33')
plt.plot(EDAdata.index, EDAdata['filtered'], '#2a3282')
plt.show()

'''
import Ledapy
import scipy.io as sio
from numpy import array as npa
filename = 'Ledapy/EDA1_long_100Hz.mat'
sampling_rate = 100
matdata = sio.loadmat(filename)
rawdata = npa(matdata['data']['conductance'][0][0][0], dtype='float64')
phasicdata = Ledapy.runner.getResult(rawdata, 'phasicdata', sampling_rate, downsample=4, optimisation=2)
import matplotlib.pyplot as plt
plt.plot(phasicdata)
plt.show()
'''
