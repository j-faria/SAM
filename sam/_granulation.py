import numpy as np
import numpy.random as rng
from .components import Component
from . import units, constants, ms
from .utils import timeseries_from_power_spectrum, normalise_timeseries

from astropy.stats import LombScargle

__all__ = ['Granulation',]


sigma_units = (ms**2/units.uHz)

class Granulation(Component):
    
    def __init__(self, sigma=0.01, tau=2, model='harvey', C=None):
        try:
            assert sigma.unit == sigma_units, \
                'Units of `sigma` in Granulation should be %s' % sigma_units
        except AttributeError:
            sigma = sigma * sigma_units

        tau_units = units.hour
        try:
            assert tau.unit == tau_units, \
                'Units of `tau` in Granulation should be %s' % tau_units
        except AttributeError:
            tau = tau * tau_units

        self.sigma, self.tau = sigma, tau
        if model.lower() not in ('harvey', 'kallinger'):
            assert C is not None, \
                'For a model that is not "harvey" or "kallinger", '\
                'please provice the exponent `C`.'
            self.C = C
        self.model = model.lower()

        self.random_state = rng.get_state()

    def __repr__(self):
        s, tau = self.sigma, self.tau
        return "Granulation(sigma={0:.3f}, tau={1:.3f})".format(s, tau)

    def __condensed_repr__(self):
        return "Gran(%.2f, %.2f)" % (self.sigma.value, self.tau.value)

    def psd_kallinger(self, nu, A, B):
        assert A.unit == sigma_units
        assert B.unit == units.hour
        assert nu.unit == units.Hz
        B = B.to(1/nu.unit)
        return A / (1.0 + (B * nu) ** 4)

    def psd_harvey(self, nu, A, B):
        assert A.unit == sigma_units
        assert B.unit == units.hour
        assert nu.unit == units.Hz
        B = B.to(1/nu.unit)
        return A / (1.0 + (B * nu) ** 2)
    
    def psd_general(self, nu, A, B, C):
        assert A.unit == sigma_units
        assert B.unit == units.hour
        assert nu.unit == units.Hz
        B = B.to(1/nu.unit)
        return A / (1.0 + (B * nu) ** C)

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

        t = t * units.day
        # freq comes in 1/d from autofrequency
        freq = LombScargle(t, np.zeros_like(t)).autofrequency()
        nu = freq.to(units.Hz)

        if self.model == 'harvey':
            power = self.psd_harvey(nu, self.sigma, self.tau)
        if self.model == 'kallinger':
            power = self.psd_kallinger(nu, self.sigma, self.tau)
        else:
            power = self.psd_general(nu, self.sigma, self.tau, self.C)
        
        y = timeseries_from_power_spectrum(nu, power)
        y = y[:t.size]

        y = normalise_timeseries(nu, power, t, y)
        
        # in the middle of all this we lost a factor of 1000
        # (the units of y are Hz(1/2) m / (s uHz(1/2))
        factor = (units.Hz / units.uHz)**(1/2)
        y = y * factor.decompose().scale

        return y

