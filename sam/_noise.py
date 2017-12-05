import numpy as np
import numpy.random as rng
from scipy import stats
from .components import Component

__all__ = ['WhiteNoise', 'DistributedNoise']

class WhiteNoise(Component):
    def __init__(self, sd=None, var=None):
        self._sd, self._var = None, None

        if sd is None and var is None:
            self.sd = 1.
        elif sd is None:
            self.var = float(var)
        elif var is None:
            self.sd = float(sd)

        self.random_state = rng.get_state()

    @property
    def sd(self):
        return self._sd
    @sd.setter
    def sd(self, value):
        assert value>0., 'Standard deviation of WhiteNoise should be positive.'
        self._sd = value
        self._var = self._sd**2

    @property
    def var(self):
        return self._var
    @var.setter
    def var(self, value):
        assert value>0., 'Standard deviation of WhiteNoise should be positive.'
        self._var = value
        self._sd = np.sqrt(self._var)


    def __repr__(self):
        if self.sd < 1e-2:
            return "WhiteNoise(sigma=%2.2e)" % self.sd
        else:
            return "WhiteNoise(sigma=%2.2f)" % self.sd
    def __condensed_repr__(self):
        return "WN(%.1f)" % self.sd

    def sample(self, t=None, change_random_state=False):
        if not change_random_state:
            rng.set_state(self.random_state)
        if t is None:
            if self.sampling is None:
                raise ValueError('provide `t` or use set_sampling')
            t = self.sampling.get_times()

        return rng.normal(loc=0., scale=self.sd, size=t.size)


class DistributedNoise(Component):
    def __init__(self, distribution, *args):
        self.distribution = distribution
        if isinstance(distribution, stats.rv_continuous):
            self.frozen = False
            self.args = args
        elif isinstance(distribution, stats._distn_infrastructure.rv_frozen):
            self.frozen = True
            self.args = distribution.args

        self.random_state = rng.get_state()

    def __repr__(self):
        if self.frozen:
            name = self.distribution.dist.name.capitalize()
        else:
            name = self.distribution.name.capitalize()

        return "%sNoise(args=%s)" % \
            (name, self.args)

    def sample(self, t=None, change_random_state=False):
        if t is None:
            if self.sampling is None:
                raise ValueError('provide `t` or use set_sampling')
            t = self.sampling.get_times()

        if not change_random_state:
            rng.set_state(self.random_state)

        if self.frozen:
            return self.distribution.rvs(size=t.size)
        else:
            return self.distribution.rvs(*self.args, size=t.size)
        # return rng.normal(loc=0., scale=self.sd, size=t.size)
