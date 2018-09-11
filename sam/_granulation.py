import numpy as np
import numpy.random as rng
from .components import Component
from . import units, constants
from .utils import timeseries_from_power_spectrum, normalise_timeseries, \
                   _pprint, _pprints

from astropy.stats import LombScargle

__all__ = ['Granulation',]

sigma_units = (units.ms**2/units.uHz)
tau_units = units.hour

class Granulation(Component):
    
    def __init__(self, sigma=0.01, tau=2, model='', C=None):
        try:
            assert sigma.unit == sigma_units, \
                'Units of `sigma` in Granulation should be %s' % sigma_units
        except AttributeError:
            sigma = sigma * sigma_units

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
        return "Granulation(sigma={0}, tau={1})".format(*_pprints([s, tau]))
        # return "Granulation(sigma={0:.3f}, tau={1:.3f})".format(s, tau)

    def __condensed_repr__(self):
        return "Gran(%.2f, %.2f)" % (self.sigma.value, self.tau.value)

    def psd_kallinger(self, nu, A, B):
        assert A.unit == sigma_units
        assert B.unit == tau_units
        assert nu.unit == units.Hz
        B = B.to(1/nu.unit)
        return A / (1.0 + (B * nu) ** 4)

    def psd_harvey(self, nu, A, B):
        assert A.unit == sigma_units
        assert B.unit == tau_units
        assert nu.unit == units.Hz
        B = B.to(1/nu.unit)
        return A / (1.0 + (B * nu) ** 2)
    
    def psd_general(self, nu, A, B, C):
        assert A.unit == sigma_units
        assert B.unit == tau_units
        assert nu.unit == units.Hz
        B = B.to(1/nu.unit)
        return A / (1.0 + (B * nu) ** C)

    def get_psd(self, nu):
        assert nu.unit == units.Hz
        if self.model == 'harvey':
            return self.psd_harvey(nu, self.sigma, self.tau)
        elif self.model == 'kallinger':
            return self.psd_kallinger(nu, self.sigma, self.tau)
        else:
            return self.psd_general(nu, self.sigma, self.tau, self.C)

    def sample(self, t=None, change_random_state=False):
        if not change_random_state:
            rng.set_state(self.random_state)
        if t is None:
            t = self._get_t()

        try:
            assert t.unit == units.day
        except AttributeError:
            t = t * units.day

        minf = 1 / t.ptp() # periods up to the timespan
        maxf = 1 / (2*np.ediff1d(t).min()) # down to the min time spacing
        # freq comes in 1/d from autofrequency
        freq = LombScargle(t, np.zeros_like(t)).autofrequency(
                    minimum_frequency=minf, maximum_frequency=maxf,
                    # samples_per_peak=1/int(t.size/100)
                    )
        # print(freq.size)
        nu = freq.to(units.Hz)

        if self.model == 'harvey':
            power = self.psd_harvey(nu, self.sigma, self.tau)
        elif self.model == 'kallinger':
            power = self.psd_kallinger(nu, self.sigma, self.tau)
        else:
            power = self.psd_general(nu, self.sigma, self.tau, self.C)
        
        y = timeseries_from_power_spectrum(nu, power)
        y = y[:t.size]

        y = normalise_timeseries(nu, power, t, y)
        
        # in the middle of all this we lost a factor of 1000
        # (the units of y are Hz(1/2) m / (s uHz(1/2))
        factor = (units.Hz / units.uHz)**(1/2)
        y = y * factor.decompose().scale / factor

        return y

