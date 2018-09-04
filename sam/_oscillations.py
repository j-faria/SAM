import numpy as np
import numpy.random as rng
from .components import Component
from . import units
from .utils import timeseries_from_power_spectrum, normalise_timeseries,\
                   _pprint, _pprints

from astropy.stats import LombScargle

__all__ = ['Oscillation',]


sigma_units = (units.ms**2/units.uHz)
width_units = units.uHz
numax_units = units.uHz

class Oscillation(Component):
    def __init__(self, sigma=1.0, width=0.5, numax=3000, model='lorentzian'):
        try:
            assert sigma.unit == sigma_units, \
                'Units of `sigma` in Oscillation should be %s' % sigma_units
        except AttributeError:
            sigma = sigma * sigma_units

        try:
            assert width.unit == width_units, \
                'Units of `width` in Oscillation should be %s' % width_units
        except AttributeError:
            width = width * width_units

        try:
            assert numax.unit == numax_units, \
                'Units of `numax` in Oscillation should be %s' % numax_units
        except AttributeError:
            numax = numax * numax_units

        self.sigma, self.width, self.numax = sigma, width, numax
        assert model.lower() in ('lorentzian', 'gaussian'), \
            'Oscillation `model` should be "lorentzian" or "gaussian".'
        self.model = model

        self.random_state = rng.get_state()

    def __repr__(self):
        s, w, n = self.sigma, self.width, self.numax
        return "Oscillation(sigma={0}, width={1}, numax={2})".format(*_pprints([s, w, n]))

    # def __condensed_repr__(self):
    #     return "KGran(%.1f, %.1f)" % (self.sigma, self.tau)

    def psd_lorentzian(self, nu, A, G, nu0):
        assert A.unit == sigma_units
        assert G.unit == width_units
        assert nu0.unit == numax_units
        assert nu.unit == units.Hz
        G = G.to(units.Hz)
        nu0 = nu0.to(units.Hz)
        return A * G**2 / ((nu - nu0)**2 + G**2)


    def psd_gaussian(self, nu, A, G, nu0):
        assert A.unit == sigma_units
        assert G.unit == width_units
        assert nu0.unit == numax_units
        assert nu.unit == units.Hz
        G = G.to(units.Hz)
        nu0 = nu0.to(units.Hz)
        c = 4 * np.log(2)
        return A * np.exp(- c * (nu-nu0)**2 / G**2)

    def get_psd(self, nu):
        assert nu.unit == units.Hz
        if self.model == 'lorentzian':
            return self.psd_lorentzian(nu, self.sigma, self.width, self.numax)
        elif self.model == 'gaussian':
            return self.psd_gaussian(nu, self.sigma, self.width, self.numax)

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

        if self.model == 'lorentzian':
            power = self.psd_lorentzian(nu, self.sigma, self.width, self.numax)
        elif self.model == 'gaussian':
            power = self.psd_gaussian(nu, self.sigma, self.width, self.numax)
        
        y = timeseries_from_power_spectrum(nu, power)
        y = y[:t.size]

        y = normalise_timeseries(nu, power, t, y)
        
        # in the middle of all this we lost a factor of 1000
        # (the units of y are Hz(1/2) m / (s uHz(1/2))
        factor = (units.Hz / units.uHz)**(1/2)
        y = y * factor.decompose().scale / factor

        return y
