import numpy as np
import numpy.random as rng

from components import Component

class WhiteNoise(Component):
	def __init__(self, sd=None, var=None):
		if sd is None and var is None:
			sd, var = 1., 1.
		elif sd is None:
			var = float(var)
			sd = np.sqrt(var)
		elif var is None:
			sd = float(sd)
			var = sd**2

		self.sd = sd
		self.var = var


	def __repr__(self):
		return "WhiteNoise(sigma=%2.2f)" % self.sd


	def sample(self, t):
		t = np.atleast_1d(t)
		return rng.normal(loc=0., scale=self.sd, size=t.size)
