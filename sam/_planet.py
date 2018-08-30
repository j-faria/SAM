from collections import namedtuple
from functools import partial
from itertools import product

import numpy as np
import numpy.random as rng
import matplotlib.pyplot as plt
from scipy import stats

from . import kepler
from .components import Component
from . import units

orb_pars = namedtuple('orbital_parameters', 'P K e omega Tp')
pi = np.pi

period_prior = stats.uniform(1.1, 1.1+1000)
semi_amplitude_prior = stats.uniform(0.0, 100)
ecc_prior = stats.beta(a=0.867, b=3.03)



def _parse_orbital_parameters(orbi):
    """
    Given a list orbi=[P,e,inc,Omega,omega,pomega,f,M,l,theta,Tp] of orbital
    parameters, parse the necessary ones to build a planet orbit.
    """
    # adapted from rebound 
    # (https://github.com/hannorein/rebound/blob/master/rebound/particle.py)

    try:
        P,e,inc,Omega,omega,pomega,f,M,l,theta,Tp = orbi
    except ValueError as e:
        raise ValueError('Got the wrong number of orbital parameters. '\
                         'This should not have happened...')

    if P is None: 
        # we will have to generate an orbital period
        pass


    ## other parameters
    if e is None:
        # we will have to generate an eccentricity
        pass
    if inc is None:
        inc = 0. # assumed

    ## angles
    if Omega is None: # we require that Omega be passed if you want to specify longitude of node
        Omega = 0.

    pericenters = [omega, pomega] # We need omega; can specify it either directly or through pomega
    numNones = pericenters.count(None)

    if numNones == 0:
        raise ValueError("You can't pass both omega and pomega")
    if numNones == 2: # Neither passed.  Default to 0.
        omega = 0.
    if numNones == 1:
        if pomega is not None:        # Only have to find omega is pomega was passed
            if np.cos(inc) > 0:       # inc is in range [-pi/2, pi/2] (prograde), so pomega = Omega + omega
                omega = pomega - Omega
            else:
                omega = Omega - pomega  # for retrograde orbits, pomega = Omega - omega

    longitudes = [f,M,l,theta,Tp] # can specify longitude through any of these four
    numNones = longitudes.count(None)

    if numNones < 4:
        raise ValueError("You can only pass one longitude/anomaly in the set [f, M, l, theta, Tp]")
    if numNones == 5:                           # none of them passed. Default to 0.
        f = 0.
    if numNones == 4:                           # Only one was passed.
        if f is None:                           # Only have to work if f wasn't passed.
            if theta is not None:               # theta is next easiest
                if np.cos(inc) > 0:             # for prograde orbits, theta = Omega + omega + f
                    f = theta - Omega - omega
                else:
                    f = Omega - omega - theta   # for retrograde, theta = Omega - omega - f
            else:                               # Either M, l, or T was passed.  Will need to find M first (if not passed) to find f
                if l is not None:
                    if np.cos(inc) > 0:         # for prograde orbits, l = Omega + omega + M
                        M = l - Omega - omega
                    else:
                        M = Omega - omega - l   # for retrograde, l = Omega - omega - M
                else:
                    if Tp is not None:
                        M = 0.0 # assumed
                # f = clibrebound.reb_tools_M_to_f(c_double(e), c_double(M))



class Planet(Component):
    def __init__(self, P=None, K=None, e=None, mass=None,
                 inc=None, Omega=None, omega=None, pomega=None, f=None,
                 M=None, l=None, theta=None, Tp=None, lam=None,
                 orbital_parameters=None):

        # the user can provide a list with the 5 more common orbital parameters
        # period, semi-amplitude, eccentricity, argument of periastron, time of periastron
        # these 5 parameters are always stored in self.orbital_parameters
        if orbital_parameters is None:
            self.P, self.K, self.e, self.w, self.Tp = P, K, e, omega, Tp
            self.orbital_parameters = orb_pars(P, K, e, omega, Tp)
        else:
            assert isinstance(orbital_parameters, list)
            self.orbital_parameters = orb_pars(*orbital_parameters)
            P, K, e, w, Tp = orbital_parameters
            self.P, self.K, self.e, self.w, self.Tp = orbital_parameters

        # TODO: K needs to be checked!
        # first check if we have enough (and not too much) to describe an orbit
        _parse_orbital_parameters([P,e,inc,Omega,omega,pomega,f,M,l,theta,Tp])

        # assume a random orbital period
        if self.P is None:
            self.P = period_prior.rvs()
        if self.K is None:
            self.K = semi_amplitude_prior.rvs()
        if self.e is None:
            self.e = ecc_prior.rvs()

        if self.w is None:
            self.w = rng.uniform(0, 2*pi)

        if self.Tp is None and lam is None:
            self.Tp = 57000.
        elif lam is not None:
            self.Tp = (self.P*(self.w - lam))/(2*np.pi) + 2454000.0

        # create range of parameters
        self.grid, self.grid2d = False, False
        self.gridsize = 1
        self.grid_parameters = []
        for var in ['P', 'K', 'e']:
            if isinstance(getattr(self, var), list) or \
               isinstance(getattr(self, var), np.ndarray):
                setattr(self, var, np.atleast_1d(getattr(self, var)))
                if self.grid:
                    self.grid2d = True
                else:
                    self.grid = True
                self.gridsize *= getattr(self, var).size
                self.grid_parameters.append(var)

        self.orbital_parameters = \
            orb_pars(self.P, self.K, self.e, self.w, self.Tp)

        super(Planet, self).__init__()

    def __repr__(self):
        if self.grid:
            return self._grid_par_repr()
        else:
            P = self.P #_Q(self.P,'days')
            K = self.K #_Q(self.K, 'meter / second')
            e = self.e #_Q(self.e)
            return "Planet(P={0:.2f~P}, K={1:.2f~P}, e={2:.2f~P})".format(P, K, e)

    """
    def _grid_par_repr(self):
        assert self.grid
        if 'P' in self.grid_parameters:
            if len(self.P) > 3:
                return "Planet(P=[%4.1f..%4.1f]days, K=%4.2fm/s, e=%2.2f)" % \
                       (self.P[0], self.P[-1], self.K, self.e)
            else:
                return "Planet(P=%sdays, K=%4.2fm/s, e=%2.2f)" % \
                       (self.P, self.K, self.e)

        if 'K' in self.grid_parameters:
            if len(self.K) > 3:
                return "Planet(P=%4.2fdays, K=[%4.1f..%4.1f]m/s, e=%2.2f)" % \
                       (self.P, self.K[0], self.K[-1], self.e)
            else:
                return "Planet(P=%4.2fdays, K=%sm/s, e=%2.2f)" % \
                       (self.P, self.K, self.e)

        if 'e' in self.grid_parameters:
            if len(self.e) > 3:
                return "Planet(P=%4.2fdays, K=%4.2fm/s, e=[%2.1f..%2.1f])" % \
                       (self.P, self.K, self.e[0], self.e[-1])
            else:
                return "Planet(P=%4.2fdays, K=%4.2fm/s, e=%s)" % \
                       (self.P, self.K, self.e)
    """

    def _grid_par_repr(self):
        old_printoptions = np.get_printoptions()
        np.set_printoptions(threshold=4, edgeitems=1)

        def atleast_1d_new(var):
            try:
                if len(var) > 1: return np.atleast_1d(var)
                elif len(var) == 1: return var[0]
            except TypeError:
                return var

        P, K, e = list(map(atleast_1d_new, [self.P, self.K, self.e]))
        P = self.P #_Q(P,'days')
        K = self.K #_Q(K, 'meter / second')
        e = self.e #_Q(e)
        s = "Planet(P={0:~P}, K={1:~P}, e={2:~P})".format(P, K, e)

        np.set_printoptions(**old_printoptions)
        return s

    def _get_time(self):
        # if self.grid and 'P' in self.grid_parameters:
        if 'P' in self.grid_parameters:
            P = self.P.mean()
        else:
            P = self.P
        return np.linspace(0, 3*P, 1000)


    def mass(self, star_mass=1.0):
        """ The mass of this planet.
        Provide star_mass in solar masses. Period is in days, semi-amplitude 
        in m/s, output is in Jupiter masses.
        """
        m_mj = 4.919e-3 * star_mass**(2./3) \
               * self.P**(1./3) * self.K * np.sqrt(1-self.e**2)
        return m_mj

    def getrv(self, t):
        if self.grid:
            args = []
            for var in ['P', 'K', 'e']:
                if var in self.grid_parameters:
                    args.append(getattr(self, var))
                else:
                    args.append([getattr(self, var)])
            args.append([self.w])
            args.append([self.Tp])

            pars = list(map(np.array, product(*args)))
            return kepler.rv_curve(t, pars)

        else:
            return kepler.rv_curve(t, self.orbital_parameters)

    def sample(self, t=None):
        if t is None:
            if self.sampling is None:
                raise ValueError('provide `t` or use set_sampling')
            t = self.sampling.get_times()
            return t, self.getrv(t)
        else:
            return self.getrv(t)

    def plotrv(self, t=None):
        if t is None:
            t = self._get_time()

        fig, ax = plt.subplots(1, 1)
        if self.grid:
            ax.plot(t, self.getrv(t), 'k', lw=2, alpha=0.4)
        else:
            ax.plot(t, self.getrv(t), 'k', lw=2)
        ax.set(xlabel='Time [days]', ylabel='RV [m/s]')
        plt.show()


class Offset(Component):
    """ A RV constant offset """
    def __init__(self, value):
        """ `value` should be in m/s """
        self.value = value

    def __repr__(self):
        return "Offset(%4.2f m/s)" % self.value

    def sample(self, t=None):
        if t is None:
            if self.sampling is None:
                raise ValueError('provide `t` or use set_sampling')
            t = self.sampling.get_times()
            return t, self.value * np.ones_like(t)
        else:
            return self.value * np.ones_like(t)


class Slope(Component):
    """ 
    A RV slope.
    This is implemented as RV = slope*(time - time[0])
    """
    def __init__(self, slope):
        """ slope should be in m/s/[units of time] """
        self.slope = slope

    def __repr__(self):
        return "Slope(%4.2f m/s/[unit of time])" % self.slope

    def sample(self, t=None):
        if t is None:
            if self.sampling is None:
                raise ValueError('provide `t` or use set_sampling')
            t = self.sampling.get_times()
            return t, self.slope * (t - t[0])
        else:
            return self.slope * (t - t[0])