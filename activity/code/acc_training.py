import numpy as np
import os
import glob
import joblib
import pandas as pd
import seaborn
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_fscore_support as mlMetrics
from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score

testRatio = 0.15
forestSize = 2000
DATA_PATH = 'raw_data'


def load_features(dir_path, path_save=None):
    subfolders = {f.name: f.path for f in os.scandir(dir_path) if f.is_dir()}
    data = pd.DataFrame()
    for dirname in subfolders.keys():
        p = subfolders[dirname]
        for label in os.scandir(p):
            if label.is_dir():
                for file in glob.glob(os.path.join(label, '*.csv')):
                    data1 = pd.read_csv(file, delimiter=';', usecols=[1, 2, 3], header=0)
                    data1[:] = data1[:] / 64.0
                    data1[['diff x', 'diff y', 'diff z']] = (data1.diff()).abs()
                    data1['E'] = np.sqrt(np.power(data1['x'], 2) + np.power(data1['y'], 2) + np.power(data1['z'], 2))
                    data2 = data1.groupby(data1.index // 160).agg(['max', 'min', 'mean', 'std'])
                    desired_features = [('x', 'max'), ('y', 'max'), ('z', 'max'), ('x', 'min'), ('y', 'min'),
                                        ('z', 'min'), ('x', 'mean'), ('y', 'mean'), ('z', 'mean'), ('x', 'std'),
                                        ('y', 'std'), ('z', 'std'), ('diff x', 'max'), ('diff y', 'max'),
                                        ('diff z', 'max'), ('E', 'max'), ('E', 'min'), ('E', 'mean'), ('E', 'std')]
                    data3 = data2[desired_features].copy()
                    data3.columns = ['%s %s' % ('%s' % b if b else '', a) for a, b in data3.columns]
                    data3.loc[:, 'class'] = label.name
                    data3.loc[:, 'hand'] = dirname
                    data = pd.concat([data, data3], ignore_index=True)
        if path_save:
            data.to_csv(path_save, index=False, header=True, sep=',')
    return data


def train_activity_model(features):
    global DATA_PATH
    hands = ['leftHand', 'rightHand']
    for hand in hands:
        features_h = features.loc[features['hand'] == hand]
        # Labels are the values we want to predict
        labels = np.array(features_h['class'])
        labels[labels == 'layingDown'] = 1
        labels[labels == 'sitting'] = 2
        labels[labels == 'standing'] = 3
        labels[labels == 'walking'] = 4
        labels[labels == 'upstairs'] = 5
        labels[labels == 'downstairs'] = 6
        labels[labels == 'bendingDown'] = 7
        labels[labels == 'jogging'] = 8

        # Remove the labels from the features
        # axis 1 refers to the columns
        features_h = features_h.drop('class', axis=1)
        features_h = features_h.drop('hand', axis=1)
        # Saving feature names for later use
        feature_list = list(features_h.columns)
        # Convert to numpy array
        features_h = np.array(features_h)
        # Split the data into training and testing sets
        train_features, test_features, train_labels, test_labels = train_test_split(features_h,
                                                                                    labels,
                                                                                    test_size=testRatio)  # , random_state=42)
        print('Training Features Shape:', train_features.shape)
        print('Training Labels Shape:', train_labels.shape)
        print('Testing Features Shape:', test_features.shape)
        print('Testing Labels Shape:', test_labels.shape)
        # Instantiate model with 1000 decision trees
        rf = RandomForestClassifier(n_estimators=forestSize)

        # Train the model on training data
        train_labels = train_labels.astype('int')
        test_labels = test_labels.astype('int')

        # Train - Test to pandas dataframe with columns names
        train_features = pd.DataFrame(train_features, columns=feature_list)
        test_features = pd.DataFrame(test_features, columns=feature_list)

        # Fit model
        trained_model = rf.fit(train_features, train_labels)

        # Use the forest's predict method on the test data
        trained_model.fit(train_features, train_labels)
        test_predictions = trained_model.predict(test_features)

        # Calculate the absolute errors
        test_errors = abs(test_predictions - test_labels)

        # Print out the mean absolute error (mae)
        print(hand)

        # noinspection PyTypeChecker
        print('TEST Mean Absolute Error: {}'.format(round(np.mean(test_errors), 2)))

        # Calculate mean absolute percentage error (MAPE)
        test_mape = 100 * (test_errors / test_labels)

        # Calculate and display accuracy
        test_accuracyManual = 100 - np.mean(test_mape)
        test_accuracyLibrary = accuracy_score(test_labels, test_predictions)
        print('TEST Accuracy Manual:', round(test_accuracyManual, 2), '%.')
        print('TEST Accuracy Library:', round(100 * test_accuracyLibrary, 2), '%.')

        # Visualise classical Confusion Matrix
        CM = confusion_matrix(test_labels, test_predictions)
        print("TEST confusion matrix")
        print(CM)

        precision, recall, f1, support = mlMetrics(test_labels, test_predictions)
        print("TEST F1, precision, recall")
        print(f1)
        print(precision)
        print(recall)

        roc = roc_auc_score(pd.get_dummies(pd.DataFrame(test_labels, dtype=str)),
                            pd.get_dummies(pd.DataFrame(test_predictions, dtype=str)),
                            multi_class="ovr",
                            average="weighted")
        print("TEST ROC-AUC scores")
        print(roc)

        # Visualize it as a heatmap
        plt.figure()
        seaborn.heatmap(CM)
        plt.show()

        filename = DATA_PATH + '/finalized_model_{}.sav'.format(hand)
        joblib.dump(trained_model, filename)


def train_hand_model(features):
    global DATA_PATH

    # Labels are the values we want to predict
    labels = np.array(features['hand'])
    labels[labels == 'rightHand'] = 1
    labels[labels == 'leftHand'] = 2

    # Remove the labels from the features
    # axis 1 refers to the columns
    features = features.drop('class', axis=1)
    features = features.drop('hand', axis=1)
    # Saving feature names for later use
    feature_list = list(features.columns)
    # Convert to numpy array
    features = np.array(features)
    # Split the data into training and testing sets
    train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size=testRatio,
                                                                                random_state=42)
    print('Training Features Shape:', train_features.shape)
    print('Training Labels Shape:', train_labels.shape)
    print('Testing Features Shape:', test_features.shape)
    print('Testing Labels Shape:', test_labels.shape)
    # Instantiate model with 1000 decision trees
    rf = RandomForestClassifier(n_estimators=forestSize)  # , random_state=42)
    # Train - Test to pandas dataframe with columns names
    train_features = pd.DataFrame(train_features, columns=feature_list)
    test_features = pd.DataFrame(test_features, columns=feature_list)

    # Train the model on training data
    train_labels = train_labels.astype('int')
    test_labels = test_labels.astype('int')
    rf.fit(train_features, train_labels)

    # Use the forest's predict method on the test data
    test_predictions = rf.predict(test_features)
    # Calculate the absolute errors
    errors = abs(test_predictions - test_labels)
    # Print out the mean absolute error (mae)
    # noinspection PyTypeChecker
    print('TEST Mean Absolute Error: {}'.format(round(np.mean(errors), 2)))
    # Calculate mean absolute percentage error (MAPE)
    mape = 100 * (errors / test_labels)

    # Calculate and display accuracy
    test_accuracyManual = 100 - np.mean(mape)
    test_accuracyLibrary = accuracy_score(test_labels, test_predictions)
    print('TEST Accuracy Manual:', round(test_accuracyManual, 2), '%.')
    print('TEST Accuracy Library:', round(100 * test_accuracyLibrary, 2), '%.')

    # Visualise classical Confusion Matrix
    CM = confusion_matrix(test_labels, test_predictions)
    print("TEST confusion matrix")
    print(CM)

    precision, recall, f1, support = mlMetrics(test_labels, test_predictions)
    print("TEST F1, precision, recall")
    print(f1)
    print(precision)
    print(recall)

    # josueportiz: comprobar error
    roc = roc_auc_score(pd.get_dummies(pd.DataFrame(test_labels, dtype=str)),
                        pd.get_dummies(pd.DataFrame(test_predictions, dtype=str)),
                        multi_class="ovr",
                        average="weighted")

    # Visualize it as a heatmap
    seaborn.heatmap(CM)
    plt.show()

    filename = DATA_PATH + '/finalized_model_hand_selection.sav'
    joblib.dump(rf, filename)


if __name__ == '__main__':
    # VARIABLES
    training = True
    production = False

    path = DATA_PATH + '/raw_data'
    path_features = DATA_PATH + '/features.csv'

    # LOAD FEATURES
    # my_features = load_features(path, path_w)
    my_features = pd.read_csv(path_features, header=0)

    # TRAIN MODELS
    if (training):
        train_activity_model(my_features)
        train_hand_model(my_features)

    # USE MODELS IN PRODUCTION
    if (production):
        loaded_model = joblib.load(DATA_PATH + '/finalized_model_hand_selection.sav')
        my_hand = my_features['hand'].values
        result = loaded_model.predict(my_features.drop(['class', 'hand'], axis=1))
        my_features['hand'] = my_hand
        my_features['predicted_hand'] = ['rightHand' if x < 1.5 else 'leftHand' for x in result]
