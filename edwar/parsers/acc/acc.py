import numpy as np
import pandas as pd
import pywt
import joblib
import os


def generate_features(data):
    # data1 = filter_acc_data(data)
    # data1 = pd.DataFrame(butter_lowpass_filter(data1, 1, 32, 6), columns=data1.columns)
    data1 = data.copy()
    data1[['diff x', 'diff y', 'diff z']] = (data1.diff()).abs()
    data1['E'] = np.sqrt(np.power(data1['x'], 2) + np.power(data1['y'], 2) + np.power(data1['z'], 2))
    # group each 5s interval and calculate
    data2 = data1.groupby(pd.Grouper(freq='5s')).agg(['max', 'min', 'mean', 'std'])
    desired_features = [('x', 'max'), ('y', 'max'), ('z', 'max'), ('x', 'min'), ('y', 'min'),
                        ('z', 'min'), ('x', 'mean'), ('y', 'mean'), ('z', 'mean'), ('x', 'std'),
                        ('y', 'std'), ('z', 'std'), ('diff x', 'max'), ('diff y', 'max'),
                        ('diff z', 'max'), ('E', 'max'), ('E', 'min'), ('E', 'mean'), ('E', 'std')]
    data3 = data2[desired_features].copy()
    data3.columns = ['%s %s' % ('%s' % b if b else '', a) for a, b in data3.columns]
    return data3


def filter_acc_data(data_in):
    data = data_in.copy()
    x = data['x'].values
    y = data['y']. values
    z = data['x'].values
    # k = 0
    # olen = len(x)
    # while k*np.power(2, 7) < olen:
    #     k = k + 1
    # diff = k*np.power(2, 7) - olen
    # x = np.pad(x, (0, diff), 'constant', constant_values=0)
    # y = np.pad(y, (0, diff), 'constant', constant_values=0)
    # z = np.pad(z, (0, diff), 'constant', constant_values=0)
    type_of_wavelet = 'haar'
    coeffx = pywt.swt(x, type_of_wavelet, 5, 0, 0)
    coeffy = pywt.swt(y, type_of_wavelet, 5, 0, 0)
    coeffz = pywt.swt(z, type_of_wavelet, 5, 0, 0)
    thr = 100
    for i in range(4, len(coeffx)):
        for j in range(0, len(coeffx[0][0])):
            if abs(coeffx[i][1][j]) > thr:
                coeffx[i][1][j] = 0
            if abs(coeffy[i][1][j]) > thr:
                coeffy[i][1][j] = 0
            if abs(coeffz[i][1][j]) > thr:
                coeffz[i][1][j] = 0
    data['x'] = pywt.iswt(coeffx, type_of_wavelet)  # [0:olen]
    data['y'] = pywt.iswt(coeffy, type_of_wavelet)  # [0:olen]
    data['z'] = pywt.iswt(coeffz, type_of_wavelet)  # [0:olen]
    return data


def predict_activity(features):
    script_dir = os.path.dirname(__file__)
    model_hand = joblib.load(os.path.join(script_dir,
                                          'models/finalized_raw_model_hand_selection.sav'))
    model_act_left = joblib.load(os.path.join(script_dir,
                                              'models/finalized_raw_model_leftHand.sav'))
    model_act_right = joblib.load(os.path.join(script_dir,
                                               'models/finalized_raw_model_rightHand.sav'))
    # Fill nan values for model prediction
    # features.fillna(method='bfill', inplace=True)
    if features.isna().any().any():
        missing_is = np.where(features.isna().any(axis=1))[0]
        if len(missing_is) == 1 and missing_is[0] == len(features) - 1:
            features = features[:-1]

    # Predict activity
    result = model_hand.predict(features)
    result1 = model_act_left.predict(features)
    result2 = model_act_right.predict(features)
    features['hand'] = ['rightHand' if x < 1.5 else 'leftHand' for x in result]
    features['activity'] = result1
    features['activity2'] = result2
    features.loc[features['hand'] == 'rightHand', 'activity'] = features.loc[features['hand'] == 'rightHand',
                                                                             'activity2']
    features['activity'] = features['activity'].round()
    features.loc[features['activity'] == 1, 'activity'] = 'layingDown'
    features.loc[features['activity'] == 2, 'activity'] = 'sitting'
    features.loc[features['activity'] == 3, 'activity'] = 'standing'
    features.loc[features['activity'] == 4, 'activity'] = 'walking'
    features.loc[features['activity'] == 5, 'activity'] = 'upstairs'
    features.loc[features['activity'] == 6, 'activity'] = 'downstairs'
    features.loc[features['activity'] == 7, 'activity'] = 'bendingDown'
    features.loc[features['activity'] == 8, 'activity'] = 'jogging'
    features = features.drop(['activity2'], axis=1)
    features.frequency = 0.2
    return features
