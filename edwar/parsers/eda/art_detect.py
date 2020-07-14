import pandas as pd
import numpy as np

from .eda_explorer.EDA_Artifact_Detection_Script import classifyEpochs, getSVMFeatures, getWaveletData, getFeatures


def __create_feature_df(data):
    """
    INPUTS:
        filepath:           string, path to input file
    OUTPUTS:
        features:           DataFrame, index is a list of timestamps for each 5 seconds, contains all the features
        data1:              DataFrame, index is a list of timestamps at 8Hz, columns include AccelZ, AccelY, AccelX,
                            Temp, EDA, filtered_eda
    """
    # Load data1 from q sensor
    wave1sec, wave_half = getWaveletData(data)

    # Compute features for each 5 second epoch
    this_data = data
    this_w1 = wave1sec
    this_w2 = wave_half
    return getFeatures(this_data, this_w1, this_w2)


def detect_arts(eda_data, classifier_list):
    five_sec = 8 * 5
    # Get pickle List and featureNames list
    feature_name_list = [[]] * len(classifier_list)
    for x in range(len(classifier_list)):
        feature_names = getSVMFeatures(classifier_list[x])
        feature_name_list[x] = feature_names

    # Get the number of data1 points, hours, and labels
    rows = len(eda_data)
    num_labels = int(np.ceil(float(rows) / five_sec))
    feature_labels = pd.DataFrame()

    # feature names for DataFrame columns
    all_feature_names = ['raw_amp', 'raw_maxd', 'raw_mind', 'raw_maxabsd', 'raw_avgabsd', 'raw_max2d', 'raw_min2d',
                         'raw_maxabs2d', 'raw_avgabs2d', 'filt_amp', 'filt_maxd', 'filt_mind', 'filt_maxabsd',
                         'filt_avgabsd', 'filt_max2d', 'filt_min2d', 'filt_maxabs2d', 'filt_avgabs2d', 'max_1s_1',
                         'max_1s_2', 'max_1s_3', 'mean_1s_1', 'mean_1s_2', 'mean_1s_3', 'std_1s_1', 'std_1s_2',
                         'std_1s_3', 'median_1s_1', 'median_1s_2', 'median_1s_3', 'aboveZero_1s_1', 'aboveZero_1s_2',
                         'aboveZero_1s_3', 'max_Hs_1', 'max_Hs_2', 'mean_Hs_1', 'mean_Hs_2', 'std_Hs_1', 'std_Hs_2',
                         'median_Hs_1', 'median_Hs_2', 'aboveZero_Hs_1', 'aboveZero_Hs_2']
    base = eda_data.index[0].second + eda_data.index[0].microsecond / 1000
    features1 = eda_data.groupby(pd.Grouper(freq='5s', base=base)).apply(__create_feature_df)
    features = pd.DataFrame(features1.values.tolist(), columns=all_feature_names, index=features1.index)
    for x in range(len(classifier_list)):
        classifier_name = classifier_list[x]
        feature_names = feature_name_list[x]
        feature_labels[classifier_list[x]] = classifyEpochs(features, feature_names, classifier_name)

    feature_labels.index = pd.date_range(eda_data.index[0], periods=num_labels, freq='5s')
    eda_data1 = eda_data.join(feature_labels, how='outer').fillna(method='ffill')
    eda_data1.frequency = eda_data.frequency
    return eda_data1
