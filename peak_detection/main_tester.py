

""" INCLUDES """
# Internal
from peak_detection import *
from util import *


# External
from datetime import datetime
import heartpy as hp
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# HW device:
TS_ROW_IDX = 0
FS_ROW_IDX = 1
FS_PPG = None

# Processing defines:
WIN_SIZE_SEC = 1.00  # s
WIN_SIZE_BREATH = 0.50  # s
OVERLAP_PEAK_DET = 0.0  # %
OVERLAP_BREATH = 50.0  # %

LOWPAS_FC = 2.5  # Hz

# Experimental environment
INPUT_DATA_PATH = 'data_test/72474/'
OUTPUT_DATA_PATH = INPUT_DATA_PATH
START_MINUTE = 60
MINUTES_OF_EVALUATION = 10
PLOT_ENABLE = True

################
# FUNCTIONS
################
def ppg_feature_extraction(ppg_org):
    ppg_dc_avg = compute_dc(
        ppg_org, FS_PPG, win_size_sec=WIN_SIZE_SEC, overlap_perc=50)

    # Flip the signal substracting the difference of the signal and the average DC to the avarage DC
    ppg = ppg_dc_avg-(ppg_org-ppg_dc_avg)

    # Low pass filtering:
    ppg_lp = but_lp_filter(ppg, LOWPAS_FC, FS_PPG, order=3)

    _, ppg_measures = hp.process(ppg_lp, FS_PPG, report_time=True, calc_freq=True,
                                 freq_method='fft', breathing_method='fft', clean_rr=True, clean_rr_method='iqr')

    return ppg_measures

""" Description of data from the device """
def device_data_description(ppg_org, ppg_ts):
    # Result dataframe
    data_description_df = pd.DataFrame()

    """ Adapt the signal accordingly to each processing need """
    # Flip the signal by subtracting the maximum value (if necessary)
    if False:
        ppg = np.max(ppg_org)-ppg_org
    else:
        ppg = ppg_org


    # Moving average DC value:
    ppg_dc = compute_dc(
        ppg, FS_PPG, win_size_sec=WIN_SIZE_SEC, overlap_perc=50)

    # Subtract computed moving average (DC)
    ppg = ppg - ppg_dc
    
    # Correct small offset to achieve a centered signal in 0:
    ppg -= np.mean(ppg)
    
    # Low pass filtering:
    ppg_lp = but_lp_filter(ppg, LOWPAS_FC, FS_PPG, order=3)
    
    # Peak detection
    ppg_M_peakPos, ppg_M_peakValue = peakDetection(ppg_lp, FS_PPG, 'Empatica', 10)
    ppg_m_peakPos, ppg_m_peakValue = peakDetection(-ppg_lp, FS_PPG, 'Empatica', 10)
    
    if PLOT_ENABLE:
        plt.figure()
        plt.plot(ppg_ts, ppg_lp, 'r')
        plt.plot(ppg_ts[ppg_M_peakPos], ppg_lp[ppg_M_peakPos], 'o')
        plt.plot(ppg_ts[ppg_m_peakPos], ppg_lp[ppg_m_peakPos], 'o')
    
    """ Compute HR manually """
    # IBI (inter-beat-interval):
    ppg_ibi = np.diff(ppg_ts[ppg_M_peakPos])/1000
    
    # HR (heart rate):
    ppg_hr = 60/ppg_ibi
    
    ppg_hr_u = np.mean(ppg_hr)
    
    """ Compute R on the overall signal """
    # Compute perfusion indexes for red an ir
    ppg_dc = np.mean(ppg_dc)  # Mean of de moving average
    ppg_ac = rms(ppg)
    ppg_pi = ppg_ac/ppg_dc

    """ Compute clinical information using hearthpy """
    try:
        _, ppg_measures = hp.process(ppg, FS_PPG, report_time=True)
        ppg_measures = ppg_feature_extraction(ppg)

        ppg_hr_hp = ppg_measures['bpm']
        ppg_ibi_hp = ppg_measures['ibi']
        ppg_rmssd = ppg_measures['rmssd']
        ppg_sdnn = ppg_measures['sdnn']
        ppg_sdsd = ppg_measures['sdsd']
        ppg_pnn20 = ppg_measures['pnn20']
        ppg_pnn50 = ppg_measures['pnn50']
        ppg_hr_mad = ppg_measures['hr_mad']
        ppg_sd1 = ppg_measures['sd1']
        ppg_sd2 = ppg_measures['sd2']
        ppg_s = ppg_measures['s']
        ppg_breath = ppg_measures['breathingrate']
        ppg_vlf = ppg_measures['vlf']
        ppg_vlf_perc = ppg_measures['vlf_perc']
        ppg_lf = ppg_measures['lf']
        ppg_lf_perc = ppg_measures['lf_perc']
        ppg_hf = ppg_measures['hf']
        ppg_hf_perc = ppg_measures['hf_perc']
        ppg_lf_hf = ppg_measures['lf/hf']
        ppg_p_total = ppg_measures['p_total']
        
    except:
        ppg_hr_hp = "-"
        ppg_ibi_hp = "-"
        ppg_rmssd = "-"
        ppg_sdnn = "-"
        ppg_sdsd = "-"
        ppg_pnn20 = "-"
        ppg_pnn50 = "-"
        ppg_hr_mad = "-"
        ppg_sd1 = "-"
        ppg_sd2 = "-"
        ppg_s = "-"
        ppg_breath = "-"
        ppg_vlf = "-"
        ppg_vlf_perc = "-"
        ppg_lf = "-"
        ppg_lf_perc = "-"
        ppg_hf = "-"
        ppg_hf_perc = "-"
        ppg_lf_hf = "-"
        ppg_p_total = "-"

    """ Append """
    row_df = pd.DataFrame(data=np.array([[ppg_pi, ppg_hr_u, ppg_hr_hp, ppg_ibi_hp, ppg_rmssd, ppg_sdnn, ppg_sdsd, ppg_pnn20, ppg_pnn50, ppg_hr_mad, ppg_sd1, ppg_sd2, ppg_s, ppg_breath, ppg_vlf, ppg_vlf_perc, ppg_lf, ppg_lf_perc, ppg_hf, ppg_hf_perc, ppg_lf_hf, ppg_p_total]]), columns=
                          ['ppg_pi', 'ppg_hr_u', 'ppg_hr_hp', 'ppg_ibi_hp', 'ppg_rmssd', 'ppg_sdnn', 'ppg_sdsd', 'ppg_pnn20', 'ppg_pnn50', 'ppg_hr_mad', 'ppg_sd1', 'ppg_sd2', 'ppg_s', 'ppg_breath', 'ppg_vlf', 'ppg_vlf_perc', 'ppg_lf', 'ppg_lf_perc', 'ppg_hf', 'ppg_hf_perc', 'ppg_lf_hf', 'ppg_p_total'])                          
    data_description_df = pd.concat(
        [data_description_df, row_df], ignore_index=True)

    return data_description_df


#######################################
#######################################
# MAIN
#######################################
#######################################
if __name__ == "__main__":
    device_data_description_df = pd.DataFrame()
    
    """ Read PPG """        
    ppg_df = load_data(INPUT_DATA_PATH + 'BVP.csv', header=None)
    
    # Get timestamps:
    ppg_ts = ppg_df.iloc[TS_ROW_IDX].values[0]
    
    # Get fs:
    FS_PPG = ppg_df.iloc[FS_ROW_IDX].values[0]
    
    # Get data (remove ts column):
    ppg_df = ppg_df.drop(TS_ROW_IDX, axis=0)
    ppg_df = ppg_df.drop(FS_ROW_IDX, axis=0)
    
    # Evaluate a fraction of the data
    ppg_df = ppg_df[int(START_MINUTE*60*FS_PPG):int(FS_PPG*60*(START_MINUTE+MINUTES_OF_EVALUATION))]
    
    # Get number of elements per sensor:
    ppg_numel = len(ppg_df)*len(ppg_df.columns)
    
    # Create data arrays:
    ppg_arr = np.reshape(ppg_df.values.tolist(), (ppg_numel, -1)).T[0]
    
    # Create timestamp arrays
    ppg_ts_arr = np.arange(0, 1000*(ppg_numel/FS_PPG), 1000/FS_PPG)
    
    """ Data description """
    data_description = device_data_description(ppg_arr, ppg_ts_arr)
    device_data_description_df = pd.concat([device_data_description_df, data_description], ignore_index=True)

        

    device_data_description_df.to_csv(
        OUTPUT_DATA_PATH + "device_data_description.csv")
