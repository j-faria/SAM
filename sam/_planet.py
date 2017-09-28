from collections import namedtuple
from functools import partial
import numpy as np
import numpy.random as rng
import matplotlib.pyplot as plt
from scipy.stats import beta

import kepler
from components import Component
from . import units, _Q

orb_pars = namedtuple('orbital_parameters', 'P K e w Tp')
pi = np.pi
ecc_prior = beta(a=0.867, b=3.03)


class Planet(Component):
    def __init__(self, P=None, K=None, e=None, w=None, Tp=None, lam=None,
                 orbital_parameters=None):

        if orbital_parameters is None:
            self.P, self.K, self.e, self.w, self.Tp, self.lam = P, K, e, w, Tp, lam
            self.orbital_parameters = orb_pars(P, K, e, w, Tp)
        else:
            assert isinstance(orbital_parameters, list)
            self.orbital_parameters = orb_pars(*orbital_parameters)
            self.P, self.K, self.e, self.w, self.Tp = orbital_parameters

        if self.P is None:
            self.P = rng.uniform(1.1, 1000.)
        if self.K is None:
            self.K = rng.uniform(0, 100.)
        if self.e is None:
            self.e = ecc_prior.rvs()

        if self.w is None:
            self.w = rng.uniform(0, 2*pi)

        if self.Tp is None and self.lam is None:
            self.Tp = 57000.
        elif self.lam is not None:
            self.Tp = (self.P*(self.w - self.lam))/(2*np.pi) + 2454000.0

        # create range of parameters
        self.grid, self.grid2d = False, False
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
            P = _Q(self.P,'days')
            K = _Q(self.K, 'meter / second')
            e = _Q(self.e)
            return "Planet(P={0:~P}, K={1:~P}, e={2:~P})".format(P, K, e)

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

        P, K, e = map(atleast_1d_new, [self.P, self.K, self.e])
        P = _Q(P,'days')
        K = _Q(K, 'meter / second')
        e = _Q(e)
        s = "Planet(P={0:~P}, K={1:~P}, e={2:~P})".format(P, K, e)

        np.set_printoptions(**old_printoptions)
        return s

    def _get_time(self):
        if self.grid and self.grid_parameter=='P':
            P = self.P.max()
        else:
            P = self.P
        return np.linspace(0, 3*P, 1000)

    def getrv(self, t):
        if self.grid:
            # if self.grid_parameter=='P':
            #     tile = partial(np.tile, reps=self.P.size)
            #     pars = [self.P] + map(tile, [self.K, self.e, self.w, self.Tp ])
            #     print pars
            other_par_names = ['P', 'K', 'e', 'w', 'Tp']
            other_par_values = [self.P, self.K, self.e, self.w, self.Tp]
            for var in ['P', 'K', 'e']:
                if self.grid_parameter == var:
                    i = other_par_names.index(var)
                    grid_var = other_par_values.pop(i)
                    tile = partial(np.tile, reps=grid_var.size)
                    pars = map(tile, other_par_values)
                    pars.insert(i, grid_var)

            return kepler.rv_curve(t, pars)

        else:
            return kepler.rv_curve(t, self.orbital_parameters)

    def sample(self, t):
        return self.getrv(t)

    def plotrv(self, t=None):
        if t is None:
            t = self._get_time()

        fig, ax = plt.subplots(1,1)
        if self.grid:
            alpha = 0.4
            ax.plot(t, self.getrv(t), 'k', lw=2, alpha=alpha)
        else:    
            ax.plot(t, self.getrv(t), 'k', lw=2)
        ax.set(xlabel='Time [days]', ylabel='RV [m/s]')
        plt.show()
