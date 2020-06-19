#  IBI
IBI_CORRECTION = True  # True if correction is needed, else False
IBI_SIGNAL = 'noisy'  # if noisy signal , HR calculated by robust but less precise algorithm

#  EDA
EDA_CLASSIFIER = ['Binary']  # selection must be always in a list
OUTPUT_FREQUENCY = 2  # in Hz, higher than 2 Hz can be problematic with cvxEDA for long dataframes
EDA_CORRECTION = True  # True if correction is needed, else False
