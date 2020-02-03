from scipy.interpolate import interp1d
from scipy import signal
import numpy as np
import pandas as pd

# __all__ = {
#     'data_resample'
# }


def get_diff_seconds(ts1, ts2):
    diff_seconds = (ts2 - ts1).total_seconds()
    return diff_seconds


def frequency_conversion(data, f, **kwargs):
    input_frequency = data.frequency
    output_frequency = f
    if input_frequency == output_frequency:
        return data
    input_samples = len(data)
    output_samples = int(output_frequency * input_samples/input_frequency)

    # Generate new dataframe:
    start_time = data.index[0]
    increment = 1/output_frequency
    new_index = pd.date_range(start=start_time, periods=output_samples, freq=str(int(increment * 1e9)) + 'N')
    data1 = pd.DataFrame(index=new_index)

    # Generate new data with output_frequency
    cols = data.columns.values
    for c in cols:
        x = np.array(data.loc[:, c])
        x1 = data_resample(x, output_samples, **kwargs)
        # Insert data in new dataframe
        data1[c] = x1
    return data1


def data_resample(n_data, n_samples, fill_value=np.nan, interp_type='linear'):
    """
    This resample uses interpolation function as upsampling and downsampling function
    """
    n_samples_i = len(n_data)
    if n_samples_i == n_samples:
        return n_data
    else:
        x = np.linspace(0, n_samples_i - 1, n_samples_i)
        f = interp1d(x, n_data, kind=interp_type, fill_value=fill_value, assume_sorted=True)
        x1 = np.linspace(0, n_samples_i - 1, n_samples)
        return f(x1)


def data_resample1(n_data, n_samples, window=None):
    """
    This resample uses resample function as upsampling and downsampling function
    """
    n_samples_i = len(n_data)
    if n_samples_i == n_samples:
        return n_data
    else:
        f = signal.resample(n_data, n_samples, window=window)
        return f


def data_resample2(n_data, n_samples, fill_value=np.nan, interp_type='linear', filter_order=None, filter_type='iir',):
    """
    This resample uses interpolation function as upsampling function, and interpolation and decimate or only decimate
    if possible as downsampling function
    """
    n_samples_i = len(n_data)
    if n_samples_i == n_samples:
        return n_data
    elif n_samples_i < n_samples:
        x = np.linspace(0, n_samples_i - 1, n_samples_i)
        f = interp1d(x, n_data, kind=interp_type, fill_value=fill_value, assume_sorted=True)
        x1 = np.linspace(0, n_samples_i - 1, n_samples)
        return f(x1)
    else:
        a = n_samples_i / n_samples
        if int(a) != a:
            n_samples_i1 = mcm(n_samples, n_samples_i)
            q = int(n_samples_i1/n_samples)
            s = data_resample2(n_data, n_samples_i1, fill_value, interp_type)
        else:
            s = n_data
            q = int(a)
        return signal.decimate(s, q, n=filter_order, ftype=filter_type)


def interpolate_empty_values(data, **kwargs):
    cols = data.columns.values
    for c in cols:
        data.loc[:, c] = data[c].interpolate(**kwargs)
    return data


def mcm(num1, num2):
    result = (num1 * num2) // mcd(num1, num2)
    return result


def mcd(num1, num2):
    a = max(num1, num2)
    b = min(num1, num2)
    result = 1
    while b:
        result = b
        b = a % b
        a = result
    return result
