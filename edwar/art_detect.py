import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
from matplotlib.dates import DateFormatter
from edwar.eda_explorer.EDA_Artifact_Detection_Script import classifyEpochs, createFeatureDF, getSVMFeatures
import csvmanage as cm


def detect_arts(eda_data, classifier_list):
    one_hour = 8 * 60 * 60  # 8(samp/s)*60(s/min)*60(min/hour) = samp/hour
    five_sec = 8 * 5

    # Get pickle List and featureNames list
    feature_name_list = [[]] * len(classifier_list)
    for i in range(len(classifier_list)):
        feature_names = getSVMFeatures(classifier_list[i])
        feature_name_list[i] = feature_names

    # Get the number of data1 points, hours, and labels
    rows = len(eda_data)
    num_labels = int(np.ceil(float(rows) / five_sec))
    hours = int(np.ceil(float(rows) / one_hour))

    # Initialize labels array
    labels = -1 * np.ones((num_labels, len(classifier_list)))

    for h in range(hours):
        # Get a data1 slice that is at most 1 hour long
        start = h * one_hour
        end = min((h + 1) * one_hour, rows)
        cur_data = eda_data[start:end]

        features = createFeatureDF(cur_data)

        for i in range(len(classifier_list)):
            # Get correct feature names for classifier
            classifier_name = classifier_list[i]
            feature_names = feature_name_list[i]

            # Label each 5 second epoch
            temp_labels = classifyEpochs(features, feature_names, classifier_name)
            labels[(h * 12 * 60):(h * 12 * 60 + temp_labels.shape[0]), i] = temp_labels

    feature_labels = pd.DataFrame(labels, index=pd.date_range(eda_data.index[0], periods=len(labels), freq='5s'),
                                  columns=classifier_list)

    return feature_labels


def print_art_detection(feature_labels, eda_data, classifier_list):
    plt.figure(figsize=(10, 5))
    plt.plot(eda_data.index, eda_data['EDA'])
    day, month, year = cm.get_date(eda_data.index[0])
    plt.title('{0}/{1}/{2} \nSkin Conductance'.format(day, month, year))
    plt.xlim([eda_data.index[0], eda_data.index[-1]])
    plt.ylabel("$\mu$S")
    formatter = DateFormatter('%H:%M:%S')
    plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
    plt.xlabel('Time')

    for i in range(0, len(feature_labels) - 1):
        start = feature_labels.index[i]
        end = start + timedelta(seconds=5)
        if feature_labels[classifier_list[0]][i] == -1:
            # artifact
            plt.axvspan(start, end, facecolor='red', alpha=0.7, edgecolor='none')
        elif feature_labels[classifier_list[0]][i] == 0:
            # Questionable
            plt.axvspan(start, end, facecolor='.5', alpha=0.5, edgecolor='none')

    plt.show()


if __name__ == "__main__":
    from edwar import eda_module as ed
    EDAdata = cm.load_results_e4('../data/ejemplo1')[0]
    EDAdata['filtered_eda'] = ed.butter_lowpass_filter(EDAdata['EDA'], 1.0, 8, 6)
    classifier = ['Binary']
    lab = detect_arts(EDAdata, classifier)
    print_art_detection(lab, EDAdata, classifier)
