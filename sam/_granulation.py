import numpy as np
import numpy.random as rng
from .components import Component
from . import units, _Q
from .utils import timeseries_from_power_spectrum, normalise_timeseries

__all__ = ['Granulation',]


class Granulation(Component):
    def __init__(self, sigma=75, tau=2/24, model='kallinger'):
        self.sigma, self.tau = sigma, tau
        self.random_state = rng.get_state()

    def __repr__(self):
        s = _Q(self.sigma, 'meter / second')
        tau = _Q(self.tau, 'day')
        return "Granulation(sigma={0:.2f~P}, tau={1:.2f~P})".format(s, tau)

    def __condensed_repr__(self):
        return "KGran(%.1f, %.1f)" % (self.sigma, self.tau)

    def psd(self, f):
        c = 2.0 * np.sqrt(2.0) / np.pi
        b = 1 / (2*np.pi*self.tau)
        return (c * self.sigma**2 / b) / (1.0 + (f / b) ** 4)

    # def eta_sq(self):
    #     """ Compute sinc^2 modulation from sampling """
    #     return np.sinc(self.f / (2.0 * self.nyq)) ** 2.0


    def sample(self, t=None, change_random_state=False):
        if not change_random_state:
            rng.set_state(self.random_state)
        if t is None:
            if self.sampling is None:
                raise ValueError('provide `t` or use set_sampling')
            t = self.sampling.get_times()

        avg_Nyquist = 0.5 * len(t) / (t.max() - t.min())
        f0 = 0.0
        bw = 1.0 / t.ptp()
        
        freq = np.arange(f0, avg_Nyquist, bw)
        power = self.psd(freq)

        y = timeseries_from_power_spectrum(freq, power)
        y = normalise_timeseries(freq, power, t, y)

        return y

