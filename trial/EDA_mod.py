from trial.EDA_wavelet_thresholding import correct_eda
from trial.adaptive_filtering import filt_accel, calculate_xyz, plot_eda
from trial.EDAtoSCL import calculate_eda_features
from trial import csvmanage as cm


def eda_module(data):
    accel = calculate_xyz(data)
    output, error, coeffs = filt_accel(data, accel, m=M, step=STEP, leak=LEAK)
    output = correct_eda(output, 1.5)
    calculate_eda_features(output)
    return output


if __name__ == '__main__':
    M = 24     # FIR filter taps
    STEP = 1   # FIR filter step
    LEAK = 0   # FIR filter leakage factor
    directory = '../data/ejemplo1'
    EDAdata = cm.load_results(directory)[0:1000]
    EDAout = eda_module(EDAdata)
    xyz = calculate_xyz(EDAdata)
    plot_eda(EDAdata, EDAout, EDAdata['EDA'] - EDAout['EDA'], xyz, M, STEP, LEAK)
