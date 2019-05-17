import pandas as pd
import os
from trial.eda_explorer import EDA_Artifact_Detection_Script as art

numClassifiers = int(art.get_user_input('Would you like 1 classifier (Binary or Multiclass) or both (enter 1 or 2): '))

# Create list of classifiers
if numClassifiers == 1:
    temp_clf = int(art.get_user_input("Select a classifier:\n1: Binary\n2: Multiclass\n:"))
    while temp_clf != 1 and temp_clf != 2:
        temp_clf = art.get_user_input(
            "Something went wrong. Enter the number 1 or 2.\n Select a classifier:\n1: Binary\n2: Multiclass):")
    if temp_clf == 1:
        print('Binary Classifier selected')
        classifierList = ['Binary']
    elif temp_clf == 2:
        print('Multiclass Classifier selected')
        classifierList = ['Multiclass']
else:
    classifierList = ['Binary', 'Multiclass']

# Classify the data
dataType = art.get_user_input("Data Type (e4 or q or misc): ")
if dataType == 'q':
    filepath = art.get_user_input("Filepath: ")
    print("Classifying data for " + filepath)
    labels, data = art.classify(filepath, classifierList, art.loadData_Qsensor)
elif dataType == 'e4':
    filepath = art.get_user_input("Path to E4 directory: ")
    print("Classifying data for " + os.path.join(filepath, "EDA.csv"))
    labels, data = art.classify(filepath, classifierList, art.loadData_E4)
    print(data)
elif dataType == "misc":
    filepath = art.get_user_input("Filepath: ")
    print("Classifying data for " + filepath)
    labels, data = art.classify(filepath, classifierList, art.loadData_misc)
else:
    print("We currently don't support that type of file.")

# Plotting the data
plotDataInput = art.get_user_input('Do you want to plot the labels? (y/n): ')

if plotDataInput == 'y':
    # Include filter plot?
    filteredPlot = art.get_user_input('Would you like to include filtered data in your plot? (y/n): ')
    if filteredPlot == 'y':
        filteredPlot = 1
    else:
        filteredPlot = 0

    # X axis in seconds?
    secondsPlot = art.get_user_input('Would you like the x-axis to be in seconds or minutes? (sec/min): ')
    if secondsPlot == 'sec':
        secondsPlot = 1
    else:
        secondsPlot = 0

    # Plot Data
    art.plotData(data, labels, classifierList, filteredPlot, secondsPlot)

    print(
        "Remember! Red is for epochs with fact, grey is for epochs that are questionable, and no shading is for clean epochs")

# Saving the data
saveDataInput = art.get_user_input('Do you want to save the labels? (y/n): ')

if saveDataInput == 'y':
    outputPath = art.get_user_input('Output directory: ')
    outputLabelFilename = art.get_user_input('Output filename: ')

    # Save labels
    fullOutputPath = os.path.join(outputPath, outputLabelFilename)
    if fullOutputPath[-4:] != '.csv':
        fullOutputPath = fullOutputPath + '.csv'

    featureLabels = pd.DataFrame(labels, index=pd.date_range(data.index[0], periods=len(labels), freq='5s'),
                                 columns=classifierList)

    featureLabels.to_csv(fullOutputPath)

    print("Labels saved to " + fullOutputPath)
    print(
        "Remember! The first column is timestamps and the second column is the labels (-1 for fact, 0 for questionable, 1 for clean)")

print('--------------------------------')
print("Please also cite this project:")
print(
    "Taylor, S., Jaques, N., Chen, W., Fedor, S., Sano, A., & Picard, R. Automatic identification of facts in electrodermal activity data. In Engineering in Medicine and Biology Conference. 2015")
print('--------------------------------')