#############
# IMPORTS
#############
# External
import datetime
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.fft import fft, fftfreq, fftshift
from scipy import interpolate
from scipy.signal import butter, lfilter

# Internal

###
# Load data from CSV
def load_data(data_path, header=0):
    data = pd.read_csv(data_path, header=header)
    return data

###
def strdate2datetime(d):
  if d != '?':
    dt = datetime.strptime(d, '%Y%m%d%H%M%S')
  else:
    dt = ""
  return dt

###
def rms(data):  # valor rms
    rms = math.sqrt(np.mean(np.power(data, 2)))
    return rms


### 
def but_bp_filter(data, lowcut, highcut, fs, order=3): #filtro paso banda
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    
    y = lfilter(b, a, data)
    return y

###
def but_lp_filter(data, highcut, fs, order=3): #filtro paso bajo
    nyq = 0.5 * fs
    high = highcut / nyq
    b, a = butter(order, high, btype='low')
    
    y = lfilter(b, a, data)
    return y

### 
def plot_fft(data, fs, remove_dc=True):
    # Number of samples
    N = len(data)
    
    # Remove DC component
    if remove_dc:
        yf = fftshift(fft(data-compute_dc(data, fs)))
    
    xf = fftshift(fftfreq(N, 1.0/fs))
    
    # Plot it
    plt.figure()
    plt.plot(xf, np.abs(yf)/N)
    plt.grid()
    plt.xlabel('Freq (Hz)')
    plt.ylabel('Amplitude')
    plt.show()
    
###
def rms(data): #valor rms
    rms = math.sqrt(np.mean(np.power(data,2)))
    return rms
    

###
def resampling(s_in, desired_length, sense='up', order=3): 
    # Interpolation
    if sense == 'up':
        # Resampling to original number of samples (upsampling)
        x = np.linspace(0, len(s_in), len(s_in))
        x_new = np.linspace(0, len(s_in), desired_length)
        interp = interpolate.UnivariateSpline(x, s_in, k=order)
        s_out = interp(x_new)
    elif sense == 'down':
        #TODO
        s_out = s_in
    
    return s_out

###
""" Apply a given function to a moving window """
def rolling_window(func, data, fs, win_size_sec=1, overlap_perc=0.0):
    """ - Window centered (if odd, add 1)
        - Use as much window as you can
    """
    # Winsize in samples
    ws = win_size_sec*fs
     
    # Winsize half width
    wsh = int(ws//2)

    # OVERLAP_PEAK_DET in samples
    ol = max(int(ws *(100-overlap_perc)/100)-1, 1)

    max_idx = data.size    
    res = np.empty(max_idx, dtype=object) 

    for i in np.arange(0, max_idx, ol):      
        res[i] = func(data[range(max(0, i-wsh), min(i+wsh, max_idx-1))])

    # Remove none
    res = res[res!=None]

    # Resampling to original number of samples (upsampling)
    res = resampling(res, max_idx, sense='up', order=3)

    return res

### 
def compute_dc(data, fs, win_size_sec=1, overlap_perc=0.0):
    dc = rolling_window(np.mean, data, fs, win_size_sec, overlap_perc)
    
    return dc


### 
def compute_rms(data, fs, win_size_sec=1, overlap_perc=0.0):
    rms_values = rolling_window(rms, data, fs, win_size_sec, overlap_perc)
    
    return rms_values

