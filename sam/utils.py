import numpy as np
from astropy.stats import LombScargle

from . import units

def _pprint(value):
    """ A pretty representation of one value with units """
    valstr = np.array2string(value)
    s = value._unitstr.replace(' / ', '/')
    unitstr = s[0] + s[1:].replace(' ', '·')
    return '{0}{1:s}'.format(valstr, unitstr)

def _pprints(values):
    """ A pretty representation of values with units """
    return list(map(_pprint, values))


def power_spectrum(t, y, freq=None):
    assert t.unit == units.day
    assert y.unit == ms

    f, p = LombScargle(t, y, normalization='psd').autopower()
    N = t.size
    # return frequency in Hz and power in (m/s)^2
    return f.to(units.Hz), p/N


def convolve_hanning(f, p, window):
    # smooth the spectrum by convolving with a (normalized) Hann window of window points
    kernel = np.hanning(window)
    kernel = kernel / kernel.sum()
    smoothed = np.convolve(kernel, p, mode='SAME')
    return smoothed

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
