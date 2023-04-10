#############
# IMPORTS
#############
# Internal
import math
import matplotlib.pyplot as plt
import numpy as np
from numpy.core.defchararray import isnumeric
#import neurokit2 as  nk

#############
# DEFINE/ GLOBAL
#############
PEAK_COUNT_DIFF_PERC = 5 # percentage
FS = None 
ITERATIONS = None
PERCENTAGE = None 
DECAY_TIME = None 
SMALL_WINDOW_SIZE = None 
LARGE_WINDOW_SIZE = None 
DISABLED_SEARCH_TIME = None 
DELTA = None
U = None 
smallWindowSize = 1

def peakDetection(rawSignal, fs, parametersFamily, iterations=1, e_perc_win=0, e_decay_win=0, e_large_win=0, e_small_win=0, e_decay=0):
    # peakDetectionn- Detects peaks for a given signals (tested for Plux and Onyx)
    #
    # Syntax:  [peakValue, peakPos] = peakDetection(rawSignal, FS, parametersFamily)
    #
    # Inputs:
    #   - rawSignal: signal that are to be detected peaks
    #   - FS: raw signal sampling frequency
    #   - parametersFamily:
    #        input must be 'Plux': for ECG peak detection
    #        or 'Onyx': for PLETH peak detection
    #        or other thing or nothin for general purpose signal
    #
    # Outputs:
    #    - peakValue: detected peaks in the whole signal
    #    - peakPos: position where the signal has a peak
    #
    # Example:
    #
    # Subdefs:
    #   - peakdet: find local and global maximum an minimum values
    #   - twoOfThree: choose the most voted input
    #   - normalize: normalize a signal with its maximum value
    # MAT-files required: none

    # How this funtion works:
    #
    # There are two parameters "LARGE_WINDOW_SIZE" and "SMALL_WINDOW_SIZE" (seconds) which define a window
    # interval. In the greater interval ("LARGE_WINDOW_SIZE") the def looks for
    # the maximum also in the lower interval ("SMALL_WINDOW_SIZE") a maximum is looked for.
    # In the other hand, for the greater interval, we look for the first local
    # or global maximums. We choose the peak with the most voted if the is no
    # concordance between "max in LARGE_WINDOW_SIZE", "max in SMALL_WINDOW_SIZE" and "the first local or
    # global max" then the window forward one sample.
    #
    # After a peak is detected, there is a time "DISABLED_SEARCH_TIME" where no peaks are looked
    # for. This is because of the origin of the signals (biological signals in
    # most cases of usage)

    ## CONSTANTS
    # PERCENTAGE = # over the max value detected to run the adaptive threshold.
    # DECAY_TIME = time constant in the exponential. Decay time of threshold (seconds).
    # LARGE_WINDOW_SIZE = large window's size for search a peak(seconds)
    # SMALL_WINDOW_SIZE = small window's size for search a peak (secodns)
    # DISABLED_SEARCH_TIME = time with detection disabled. (seconds)

    # These values should have a logical explanation, but his value is an
    # experimental result. Nevertheless there are aceptable ranges.
    # SMALL_WINDOW_SIZE: To detect high variations
    # LARGE_WINDOW_SIZE: To detect low variations
    # DISABLED_SEARCH_TIME: It is assumed that there are no peaks at high rate

    global FS, ITERATIONS, PERCENTAGE, DECAY_TIME, SMALL_WINDOW_SIZE, LARGE_WINDOW_SIZE, DISABLED_SEARCH_TIME, DELTA, U
    global smallWindowSize

    FS = fs
    ITERATIONS = iterations

    if parametersFamily == 'Plux':
        # Experimental values adjusted with a 8 hours test
        PERCENTAGE = 1+e_perc_win
        DECAY_TIME = 0.25+e_decay_win # Seconds
        LARGE_WINDOW_SIZE = 2.5+e_large_win # Seconds. 25 peaks per minute
        SMALL_WINDOW_SIZE = 0.4+e_small_win# Seconds. 150 peaks per minute
        DISABLED_SEARCH_TIME = 0.200+e_decay # Seconds. between peaks (300 ppm)
    elif parametersFamily == 'm2c':
         # Experimental values adjusted with a 8 hours test
        PERCENTAGE = 1+e_perc_win
        DECAY_TIME = 0.01+e_decay_win # Seconds
        LARGE_WINDOW_SIZE = 2.5+e_large_win # Seconds. 25 peaks per minute
        SMALL_WINDOW_SIZE = 0.4+e_small_win # Seconds. 150 peaks per minute
        DISABLED_SEARCH_TIME = 0.200+e_decay # Seconds. between peaks (300 ppm)
    elif parametersFamily == 'Onyx':
        # Experimental values adjusted with a 8 hours test
        PERCENTAGE = 0.98+e_perc_win # Seconds
        DECAY_TIME = 1.8+e_decay_win # Seconds
        LARGE_WINDOW_SIZE = 2+e_large_win # Seconds. 30 ppm
        SMALL_WINDOW_SIZE = 0.66+e_small_win # Seconds. 90 ppm
        DISABLED_SEARCH_TIME = 0.250+e_decay # Seconds
    elif parametersFamily == 'Empatica':
        # Experimental values adjusted with a 8 hours test
        PERCENTAGE = 0.98+e_perc_win
        DECAY_TIME = 1.8+e_decay_win # Seconds
        LARGE_WINDOW_SIZE = 2+e_large_win # Seconds. 30 ppm
        SMALL_WINDOW_SIZE = 0.6+e_small_win # Seconds. 100 ppm
        DISABLED_SEARCH_TIME = 0.250+e_decay # Seconds    
    elif parametersFamily == 'planar-oxi':
         # Experimental values adjusted with a 8 hours test
        PERCENTAGE = 1+e_perc_win # Seconds
        DECAY_TIME = 1.8+e_decay_win # Seconds
        LARGE_WINDOW_SIZE = 2+e_large_win # Seconds. 30 ppm
        SMALL_WINDOW_SIZE = 0.5+e_small_win # Seconds. 68 ppm
        DISABLED_SEARCH_TIME = 0.500+e_decay # Seconds
    elif parametersFamily == 'respiration':
         # Experimental values
        PERCENTAGE = 1+e_perc_win # Seconds
        DECAY_TIME = 1+e_decay_win # Seconds
        LARGE_WINDOW_SIZE = 6+e_large_win # Seconds. 10 resppm
        SMALL_WINDOW_SIZE = 3+e_small_win # Seconds. 20 resppm
        DISABLED_SEARCH_TIME = 0.500+e_decay # Seconds
    else:
        PERCENTAGE = 0.5+e_perc_win
        DECAY_TIME = 0.5+e_decay_win
        LARGE_WINDOW_SIZE = 1+e_large_win
        SMALL_WINDOW_SIZE = 0.66+e_small_win # Seconds. 90 ppm
        DISABLED_SEARCH_TIME = 0.100+e_decay


    # This constant has an experimental value, but also ensure that our signals
    # cannot increase more thar 1/5 of his amplitude in 1 sample (FS)
    DELTA=5/FS # This value is to be ensured that a maximum really is a maximum

    # Optional vector to store thresholds an visualize them for debuggin
    # purposes. Set U = true, if you want to use it.
    U = False

    # Count ositive and negative peaks iteratively. 
    # If the difference of peaks count is higher that "PEAK_COUNT_DIFF_PERC", 
    # change epsilons and run it again up to "ITERATIONS" times. 

    diff_max_min_peaks = math.inf
    prev_diff = diff_max_min_peaks
    sign_epsilon = "sub"

    for i in range(0, ITERATIONS):
        pos_peaks, _ = peak_detection(rawSignal)
        neg_peaks, _ = peak_detection(-rawSignal)

        count_pos_peaks = np.count_nonzero(pos_peaks)
        count_neg_peaks = np.count_nonzero(neg_peaks)
        max_count = max(count_pos_peaks, count_neg_peaks)
        min_count = min(count_pos_peaks, count_neg_peaks)

        diff_max_min_peaks = 100*((max_count-min_count)/max_count)

        if diff_max_min_peaks < PEAK_COUNT_DIFF_PERC:
            break
        else:
            if diff_max_min_peaks < prev_diff:
                keep_sign_epsilon = True                
            else:
                keep_sign_epsilon = False
        
        if keep_sign_epsilon:
            if sign_epsilon == "sum":
                SMALL_WINDOW_SIZE += 0.05 # seconds
            else: 
                SMALL_WINDOW_SIZE -= 0.05 # seconds                 

    return pos_peaks, neg_peaks

def peak_detection(rawSignal):
    
    ## INIT VARIABLES
    largeWindowSize=round(LARGE_WINDOW_SIZE*FS) # Samples
    smallWindowSize = round(SMALL_WINDOW_SIZE*FS) # Samples
    disabledSearchTime=round(DISABLED_SEARCH_TIME*FS) # Samples with detection disabled
    l=len(rawSignal)

    initTime = 0 # Sample
    expTime = 0 # Sample to explore the signal
    localMax = 0 # Theshold starts in 0

    # Init U vector to store the thresholds detected
    if U:
        localThresholdVector = np.zeros((l,1), dtype=int)

    # Init vector "peakValue" to store positions fo peaks detected
    peakPos = np.zeros((1, l), dtype=bool) # Logical vector, set TRUE where a peak is found
    peakValue = np.zeros((1, l), dtype=float) # To store peaks' values


    ## ALGORITH. PEAK DETECTION
    ## Adaptive-exponential-threshold
    if (len(list(filter(lambda x: (x < 0), rawSignal))) > 2): # At least 1 peak
        while(expTime < l):
            threshold = localMax*math.exp(-(expTime-initTime)/(FS*DECAY_TIME)) # Update threshold
            
            if rawSignal[expTime]>=threshold:                
                # Take a piece of signal. Take up to the max value for searching "largeWindowSize".
                # Take also a small window:
                if (expTime+largeWindowSize <= l):               
                    a = normalize(rawSignal[expTime : expTime+largeWindowSize])
                    b = normalize(rawSignal[expTime : expTime+smallWindowSize])
                else:
                    a = normalize(rawSignal[expTime : l])
                    if (expTime+smallWindowSize <= l):
                        b = normalize(rawSignal[expTime:expTime+smallWindowSize])
                    else:
                        b = normalize(rawSignal[expTime:l])
                    
                               
                
                # Search the global or local max in the whole window.
                # We only need the first one as you will see later.
                localOrGlobalMax, _ = peakdet(a, DELTA)         
                if (len(localOrGlobalMax)<1):
                    localMaxPos = 0

                else:                    
                    # New threshold = max value in the interval and its position
                    # Furthermore threshold is updated with "PERCENTAGE"
                    # Look for near("smallWindowSize") and far ("largeWindowSize") to avoid not find a near peak.
                    # To avoid select a second peak before the next one, we select the
                    # previous one
                    absMaxPos = (a*PERCENTAGE).argmax(0) # Where the max point is in the whole window
                    posibleMaxPos = (b*PERCENTAGE).argmax(0) # Where the max point is in the small window
                    """ if (len(posibleMaxPos)<1):
                        posibleMaxPos = 1 """
                    
                    
                    # If no concordance between values then localMaxPos=0 and increase
                    # one sample to keep searching.
                    localMaxPos  = twoOfThree(posibleMaxPos, absMaxPos, localOrGlobalMax[0][0])
                    localMax = localOrGlobalMax[0][1] # "a" contains "DISABLED_SEARCH_TIME" vector
                
                if (localMaxPos != 0): # Peak detected
                    # Keep the threshold in the same value up to the max
                    if U:
                        localThresholdVector[expTime:expTime+localMaxPos] = threshold
                    # Update indexes of samples
                    expTime=expTime+localMaxPos
                    
                    peakValue[0][expTime] = rawSignal[expTime] # Store the peaks' values
                    peakPos[0][expTime] = True # Store the peaks' positions
                                                           
                    # Disable detection along "DISABLED_SEARCH_TIME" millis
                    # ("disabledSearchTime" samples) and keep
                    # the threshold in the same value
                    if (expTime+disabledSearchTime <= l):
                        if U:
                            localThresholdVector[expTime:expTime+disabledSearchTime] = localMax 
                        expTime = expTime + disabledSearchTime
                    else:
                        if U:
                            localThresholdVector[expTime:l] = localMax 
                        expTime = l
                    
                    
                    # Update indexes of samples
                    initTime = expTime
               
            
            expTime = expTime+1 # Keep searching
        

    return peakPos[0], peakValue[0]


## LOCAL METHODS:
def peakdet(v, delta):
    #PEAKDET Detect peaks in a vector
    #        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    #        maxima and minima ("peaks") in the vector V.
    #        MAXTAB and MINTAB consists of two columns. Column 1
    #        contains indices in V, and column 2 the found values.
    #
    #        A point is considered a maximum peak if it has the maximal
    #        value, and was preceded (to the left) by a value lower by
    #        DELTA.
        
    # Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    # This def is released to the public domain Any use is allowed.
        
    maxtab = np.empty((0,2), float)
    mintab = np.empty((0,2), float)
        
    v = v[:] # Just in case this wasn't a proper vector
    x = range(0,len(v))
        
    mn = math.inf 
    mx = -math.inf
    mnpos = None
    mxpos = None
        
    lookformax = 1
        
        
    for i in range(0,len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]
          
        if lookformax:
            if this < mx-delta:
                maxtab = np.append(maxtab, np.array([[mxpos, mx]]), axis=0)
                mn = this
                mnpos = x[i]
                lookformax = 0
                
        else:
            if this > mn+delta:
                mintab = np.append(mintab, np.array([[mnpos, mn]]), axis=0)
                mx = this
                mxpos = x[i]
                lookformax = 1
        
    return maxtab, mintab
    
###
# sws = small window size
# fs = sampling frequency
def twoOfThree(inOne, inTwo, inThree):
    global SMALL_WINDOW_SIZE, FS, smallWindowSize

    # Choose the most voted input
    if (inOne == inTwo) | (inOne == inThree):
        pos = inOne
        smallWindowSize = int(SMALL_WINDOW_SIZE*FS)
    elif (inTwo == inThree):
        pos = inTwo
        smallWindowSize = round(SMALL_WINDOW_SIZE*FS)
    else:
        # No ha consenso
        pos = 0
        smallWindowSize=smallWindowSize-1 #reduce la largeWindowSize para que al avanzar +1 no pille un segundo pico que enmascare
        if(smallWindowSize < 1):
            smallWindowSize = 1
        
    return pos
            
        
    

def normalize(inputVector):
    # Normalize a signal with its maximum value
    # josueportiz@20201211 add mean removal
    dataNoMean = inputVector-np.mean(inputVector)
    outputNormalized = dataNoMean/max(dataNoMean)

    return outputNormalized    


    


