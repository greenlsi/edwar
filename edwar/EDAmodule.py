from scipy import signal
# from edwar.EDA_wavelet_thresholding import correct_eda
from edwar.adaptive_filtering import filt_accel, calculate_xyz, plot_eda
from edwar.EDAtoSCL import calculate_eda_features
from edwar import csvmanage as cm


def butter_lowpass(cutoff, fs, order=5):
    # Filtering Helper functions
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    # noinspection PyTupleAssignmentBalance
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    # Filtering Helper functions
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y


def eda_module(data):
    # Get the filtered data1 using a low-pass butterworth filter (cutoff:1hz, fs:8hz, order:6)
    data['filtered_eda'] = butter_lowpass_filter(data['EDA'], 1.0, 8, 6)
    accel = calculate_xyz(data)
    output, error, coeffs = filt_accel(data, accel, m=M, step=STEP, leak=LEAK,  adaptive_step_factor=0.001)
    # output = correct_eda(output, 1.5)
    calculate_eda_features(output)
    return output


if __name__ == '__main__':
    M = 24     # FIR filter taps
    STEP = 1   # FIR filter step
    LEAK = 0   # FIR filter leakage factor
    directory = '../data1/ejemplo1'
    EDAdata = cm.load_results_e4(directory)[0:1000]
    EDAout = eda_module(EDAdata)
    xyz = calculate_xyz(EDAdata)
    plot_eda(EDAdata, EDAout, EDAdata['EDA'] - EDAout['EDA'], xyz, M, STEP, LEAK)
