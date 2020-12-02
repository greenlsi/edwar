import joblib
import pandas as pd
import numpy as np
import scipy.signal as scisig
import scipy.stats
from edwar.parsers.eda import cvxEDA
from edwar.parsers.utils import frequency_conversion
import os


def get_slope(series):
    linreg = scipy.stats.linregress(np.arange(len(series)), series)
    slope = linreg[0]
    return slope


def get_net_accel(data):
    return (data['x'] ** 2 + data['y'] ** 2 + data['z'] ** 2).apply(lambda x: np.sqrt(x))


def get_peak_freq(x):
    f, pxx = scisig.periodogram(x, fs=8)
    psd_dict = {amp: freq for amp, freq in zip(pxx, f)}
    peak_freq = psd_dict[max(psd_dict.keys())]
    return peak_freq


def get_window_stats(data):
    mean_features = np.mean(data)
    std_features = np.std(data)
    min_features = np.amin(data)
    max_features = np.amax(data)
    all_feat = np.hstack([mean_features, std_features, min_features, max_features])
    # features = {'mean': mean_features, 'std': std_features, 'min': min_features, 'max': max_features}
    return list(all_feat)


# cvxEDA
def eda_stats(y, fs):
    yn = (y - y.mean()) / y.std()
    [r, p, t, l, d, e, obj] = cvxEDA.cvxEDA(yn, 1. / fs)
    return [r, p, t, l, d, e, obj]


# https://github.com/MITMediaLabAffectiveComputing/eda-explorer/blob/master/load_files.py
def butter_lowpass(cutoff, fs, order=5):
    # Filtering Helper functions
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = scisig.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    # Filtering Helper functions
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = scisig.lfilter(b, a, data)
    return y


def compute_eda_features(eda_df):
    # EDA features
    eda_df['EDA'] = butter_lowpass_filter(eda_df['EDA'], 1.0, eda_df.frequency, 6)
    eda_df = frequency_conversion(eda_df, 2)
    eda_df['EDA'] = (eda_df['EDA'] - eda_df['EDA'].mean()) / eda_df['EDA'].std()
    r, p, t, l, d, e, obj = cvxEDA.cvxEDA(eda_df['EDA'], 1. / eda_df.frequency, options={'reltol': 1e-9,
                                                                                         'show_progress': False})
    eda_df['SCR'] = r
    eda_df['SMNA'] = p
    eda_df['SCL'] = t
    del eda_df['EDA']

    return eda_df


def eda_get_samples(data):
    data1 = data[['EDA']].copy()
    data1.frequency = data.frequency
    data1 = compute_eda_features(data1)
    base = data1.index[0].second + data1.index[0].microsecond / 1000
    features1 = data1.groupby(pd.Grouper(freq='5s', origin=base)).apply(get_window_stats)
    column_names = ['SCR_mean', 'SMNA_mean', 'SCL_mean', 'SCR_std', 'SMNA_std', 'SCL_std', 'SCR_min', 'SMNA_min',
                    'SCL_min', 'SCR_max', 'SMNA_max', 'SCL_max']
    features = pd.DataFrame(features1.values.tolist(), columns=column_names, index=features1.index)
    return features


def bvp_get_samples(data):
    data1 = data[['BVP']].copy()
    base = data1.index[0].second + data1.index[0].microsecond / 1000
    features1 = data1.groupby(pd.Grouper(freq='5s', origin=base)).apply(get_window_stats)
    features2 = data1['BVP'].groupby(pd.Grouper(freq='5s', origin=base)).apply(get_peak_freq)
    column_names = ['BVP_mean', 'BVP_std', 'BVP_min', 'BVP_max']
    features = pd.DataFrame(features1.values.tolist(), columns=column_names, index=features1.index)
    features['BVP_peak_freq'] = features2
    return features


def acc_get_samples(data):
    data1 = data[['x', 'y', 'z']].copy()
    data1['E'] = get_net_accel(data1)
    base = data1.index[0].second + data1.index[0].microsecond / 1000
    featuresa = data1.groupby(pd.Grouper(freq='5s', origin=base)).apply(get_window_stats)
    column_names = ['x_mean', 'y_mean', 'z_mean', 'E_mean', 'x_std', 'y_std', 'z_std', 'E_std', 'x_min', 'y_min',
                    'z_min', 'E_min', 'x_max', 'y_max', 'z_max', 'E_max']
    features = pd.DataFrame(featuresa.values.tolist(), columns=column_names, index=featuresa.index)
    data1['diff_x'] = abs(data1['x'].diff())
    data1['diff_y'] = abs(data1['y'].diff())
    data1['diff_z'] = abs(data1['z'].diff())
    data1 = data1.fillna(0)
    featuresb = data1[['diff_x', 'diff_y', 'diff_z']].groupby(pd.Grouper(freq='5s', origin=base)).max()
    column_names1 = ['max_diff_x', 'max_diff_y', 'max_diff_z']
    features1 = pd.DataFrame(featuresb.values.tolist(), columns=column_names1, index=featuresb.index)
    return pd.concat([features, features1], axis=1)


def temp_get_samples(data):
    data1 = data[['TEMP']].copy()
    base = data1.index[0].second + data1.index[0].microsecond / 1000
    features1 = data1.groupby(pd.Grouper(freq='5s', origin=base)).apply(get_window_stats)
    column_names = ['TEMP_mean', 'TEMP_std', 'TEMP_min', 'TEMP_max']
    features = pd.DataFrame(features1.values.tolist(), columns=column_names, index=features1.index)
    features['TEMP_slope'] = data1['TEMP'].groupby(pd.Grouper(freq='5s', origin=base)).apply(get_slope)

    return features


def generate_data(eda_df, bvp_df, acc_df, temp_df):
    eda_features_samples = eda_get_samples(eda_df)
    bvp_features_samples = bvp_get_samples(bvp_df)
    acc_features_samples = acc_get_samples(acc_df)
    temp_features_samples = temp_get_samples(temp_df)
    results = eda_features_samples.join(bvp_features_samples, how='inner')
    results = results.join(acc_features_samples, how='inner')
    results = results.join(temp_features_samples, how='inner')
    column_names = ['E_max', 'E_mean', 'E_min', 'E_std', 'SCR_max', 'SCR_mean', 'SCR_min',
                    'SMNA_std', 'SMNA_max', 'SMNA_mean', 'SMNA_min', 'SMNA_std',
                    'SCL_max', 'SCL_mean', 'SCL_min', 'SCL_std', 'BVP_max', 'BVP_mean', 'BVP_min', 'BVP_std',
                    'TEMP_max', 'TEMP_mean', 'TEMP_min', 'TEMP_std', 'x_max', 'x_mean', 'x_min', 'x_std',
                    'y_max', 'y_mean', 'y_min', 'y_std', 'z_max', 'z_mean', 'z_min', 'z_std',
                    'BVP_peak_freq', 'TEMP_slope']
    return results[column_names]


def predict_stress(data):
    script_dir = os.path.dirname(__file__)
    stress_model = joblib.load(os.path.join(script_dir, 'models/finalized_raw_model_stress.sav'))
    data['stress'] = stress_model.predict(data)
    data.loc[data['stress'] == 0, 'stress'] = 'amusement'
    data.loc[data['stress'] == 1, 'stress'] = 'baseline'
    data.loc[data['stress'] == 2, 'stress'] = 'stress'
    return data
