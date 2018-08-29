import numpy as np
from scipy.signal import periodogram

def power_spectrum(time, y):
    time = time - time[0]
    df = 1.0 / np.ediff1d(time).min()
    f, p = periodogram(y, df)

    lhs = (1.0 / len(time)) * np.sum(y ** 2)
    rhs = np.sum(p)
    ratio = lhs / rhs
    p *= ratio / df
    fill = len(np.where(y != 0.0)[0]) / float(len(y))
    p /= fill
    return f, p

def timeseries_from_power_spectrum(freq, power):
    bw = freq[1] - freq[0]
    p = power * bw
    real_comp = np.random.normal(0, 1, len(p)) * np.sqrt(p / 2.0)
    imag_comp = np.random.normal(0, 1, len(p)) * np.sqrt(p / 2.0)

    inv_fft = real_comp + 1j*imag_comp
    y = np.fft.irfft(inv_fft, 2*len(p)) * len(p)
    return y


def normalise_timeseries(freq, power, time, y):
    lhs = (1.0 / len(time)) * np.sum(y ** 2)
    bw = freq[1]-freq[0]
    rhs = np.sum(power * bw)
    ratio = lhs / rhs
    # divide by square root to put ratio into amplitude
    y = y / np.sqrt(ratio)
    return y
