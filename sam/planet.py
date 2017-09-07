import numpy as np
import numpy.random as rng
import matplotlib.pyplot as plt
from . import kepler

from components import Component

pi = np.pi


class Planet(Component):
	def __init__(self, P=None, K=None, e=None, w=None, Tp=None, orbital_pars=None):

		if orbital_pars is None:
			self.P, self.K, self.e, self.w, self.Tp = P,K,e,w,Tp
			self.orbital_pars = P,K,e,w,Tp
		else:
			assert isinstance(orbital_pars, list)
			self.orbital_pars = orbital_pars
			self.P, self.K, self.e, self.w, self.Tp = orbital_pars

		if self.P is None:
			self.P = rng.uniform(1.1, 1000.)
		if self.K is None:
			self.K = rng.uniform(0, 100.)
		if self.e is None:
			self.e = rng.uniform(0,1)

		if self.w is None or self.Tp is None:
			self.w = rng.uniform(0,2*pi)
			self.Tp = 57000.

		self.orbital_pars = self.P, self.K, self.e, self.w, self.Tp
		super(Planet, self).__init__()


	def __repr__(self):
		return "Planet(P=%4.2fdays, K=%4.2fm/s, e=%2.2f)" % \
		           (self.P, self.K, self.e)

	def _get_time(self):
		return np.linspace(0, 3*self.P, 1000)

	def getrv(self, t):
		return kepler.rv_curve(t, self.orbital_pars)

	def sample(self, t):
		return self.getrv(t)

	def plotrv(self, t=None):
		if t is None:
			t = self._get_time()

		fig, ax = plt.subplots(1,1)
		ax.plot(t, self.getrv(t), 'k', lw=2)
		ax.set(xlabel='Time [days]', ylabel='RV [m/s]')
		plt.show()