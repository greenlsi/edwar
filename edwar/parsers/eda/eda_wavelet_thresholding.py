import pywt
import numpy as np

from ..utils import butter_lowpass_filter


def correct_eda(eda_data, classifier):
    eda = eda_data['EDA'].values
    f = eda_data.frequency
    k = 0
    olen = len(eda)
    while k*np.power(2, 7) < olen:
        k = k + 1
    diff = k*np.power(2, 7) - olen
    eda = np.pad(eda, (0, diff), 'constant', constant_values=0)
    type_of_wavelet = 'haar'
    coeff = pywt.swt(eda, type_of_wavelet, 7, 0, 0)
    # od1 = coeff[0][1][0:olen]
    for i in range(0, len(coeff[0][0])):
        for j in range(0, len(coeff)):
            coeff[j][1][i] = 0

    eda_data['corrected'] = pywt.iswt(coeff, type_of_wavelet)[0:olen]
    eda_data.loc[eda_data[classifier[0]] == 1, 'corrected'] = eda_data.loc[eda_data[classifier[0]] == 1, 'EDA']
    eda_data['EDA'] = eda_data['corrected']
    eda_data['filtered_eda'] = butter_lowpass_filter(eda_data['EDA'].values, 1.0, eda_data.frequency, 6)
    eda_data = eda_data[['EDA', 'filtered_eda', classifier[0]]]
    eda_data.frequency = f
    return eda_data
