import numpy as np
import matplotlib.pyplot as plt
import pywt
import pandas as pd
from matplotlib.dates import DateFormatter
from trial import csvmanage as cm

directory = '../data/ejemplo'
EDAdata = cm.load_results(directory + '/EDA.csv', 0)
EDA = np.array(EDAdata['medida'], dtype='float64')
type_of_wavelet = 'db1'
# print(pywt.swt_max_level(len(EDA)))
coeff = pywt.swt(EDA, type_of_wavelet, 7, 0, 0)
for i in range(0, len(coeff)):
    for j in range(0, len(coeff[0][0])):
        coeff[i][1][j] = 0
EDAcorrected = pywt.iswt(coeff, type_of_wavelet)
EDAdata['corrected'] = EDAdata['medida']
for i in range(0, len(EDAdata)):
    EDAdata['corrected'][i] = EDAcorrected[i]

data_min = min(EDAdata['medida'])
data_max = max(EDAdata['medida'])
day, month, year = cm.get_date(EDAdata.index[0])
plt.figure(1, figsize=(20, 5))
plt.xlim([EDAdata.index[0], EDAdata.index[-1]])
# y_min = min(0, data_min) - (data_max - data_min) * 0.1
plt.ylim([min(0, data_min), data_max * 1.15])
plt.title('EDA (purple), EDA corrected (gray) \n {0}/{1}/{2}'.format(day, month, year))
plt.ylabel('$\mu$S')
formatter = DateFormatter('%H:%M:%S')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.xlabel('Time')
# plt.plot(EDAdata.index, EDAdata['phasic'], '#6d1013') #red
plt.plot(EDAdata.index, EDAdata['medida'], '#9F33BD')
plt.plot(EDAdata.index, EDAdata['corrected'], '#2e352c')
plt.show()

