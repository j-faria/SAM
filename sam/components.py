# -*- coding: utf-8 -*-
import os
import numpy as np
import matplotlib.pyplot as plt

from _sampling import TimeSampling


def deepgetattr(obj, attr):
    """Recurses through an attribute chain to get the ultimate value."""
    return reduce(getattr, attr.split('.'), obj)


class Component(object):
    """ """

    def __init__(self, *args):
        self.sampling = None
        # self.pars = []

    def __add__(self, b):
        return Sum(self, b)
    def __radd__(self, b):
        return self.__add__(b)

    def set_sampling(self, sampling):
        assert isinstance(sampling, TimeSampling), \
            'argument of set_sampling should be instance of TimeSampling.'

        self.sampling = sampling

    def save_rdb(self, filename, error=None):
        if os.path.exists(filename):
            print 'File "%s" exists. Replace? (y/n) ' % filename,
            answer = raw_input()
            if answer == 'y':
                pass
            else:
                print 'aborting'
                return

        if error is None:
            error = np.ones_like(self.sampling.time)

        header = 'jdb\tvrad\tsvrad\n---\t----\t-----'
        fmt = ['%12.6f', '%8.5f', '%7.5f']
        sample = self.sample()
        if isinstance(sample, tuple):
            X = zip(sample[0], sample[1], error)
        else:
            X = zip(self.sampling.time, sample, error)

        np.savetxt(filename, X=X, header=header, fmt=fmt, comments='',)


class Sum(Component):
    def __init__(self, *args):
        super(Sum, self).__init__()
        for i, c in enumerate(args):
            setattr(self, 'c%d' % (i+1), c)

    def __repr__(self):
        return "{0} \n+ {1}".format(self.c1, self.c2)

    @property
    def components(self):
        c = []
        c.append(self.c2)
        cdot = 'c1'
        while hasattr(deepgetattr(self, cdot), 'components'):
            att = deepgetattr(self, cdot+'.c2')
            c.append(att)
            cdot += '.c1'
        else:
            att = deepgetattr(self, cdot)
            c.append(att)

        return c

    def sample(self, t=None):
        if t is None:
            if self.sampling is None:
                raise ValueError('provide `t` or use set_sampling')
            t = self.sampling.get_times()

        # s1 = self.c1.sample(t)
        # s2 = self.c2.sample(t)
        # return self.c1.sample(t) + self.c2.sample(t)
        return np.vstack(self.c1.sample(t)) + np.vstack(self.c2.sample(t))
        # return np.hstack(np.hsplit(self.c1.sample(t), 4) + np.hsplit(self.c2.sample(t), 2))

    def plots(self, t=None, ntt=None):
        if t is None:
            if self.sampling is None:
                raise ValueError('provide `t` or use set_sampling')
            t = self.sampling.get_times()

        # get at least 10 points inside the smallest planet period
        Pmin = np.inf
        for c in self.components:
            try:
                if c.grid:
                    Pmin = min(Pmin, c.P.min())
                else:
                    Pmin = min(Pmin, c.P)
            except AttributeError:
                pass

        if ntt is None:
            ntt = int(50 * t.ptp() / Pmin)
            if ntt == 0:
                ntt = 1000
            ntt = min(10000, ntt)
        tt = np.linspace(t.min(), t.max(), ntt)

        fig, axes = plt.subplots(2, 1)
        axes[0].plot(tt, self.sample(tt), 'r', lw=1, alpha=0.3)
        axes[0].plot(t, self.sample(t), '-ok', lw=2)

        for c in self.components:
            axes[1].plot(tt, c.sample(tt), '-', alpha=0.5, label=c.__repr__())
        axes[1].legend()
