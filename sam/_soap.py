import warnings
import numpy as np
from .components import Component

try:
	from SOAP import Simulation
	from SOAP.classes import randomActReg
	SOAP_is_available = True
except ImportError:
	SOAP_is_available = False
	with warnings.catch_warnings():
		warnings.simplefilter("module")
		warnings.warn('module SOAP could not be imported.', ImportWarning)

__all__ = ['SOAP']

if SOAP_is_available:

	class SOAP(Component):
		def __init__(self, random=False):
			self.sim = Simulation()
			if random:
				self.sim.active_regions = [randomActReg(),]



		def __repr__(self):
			return self.sim.__repr__()
		def __condensed_repr__(self):
			return self.sim.__repr__()


		def sample(self, t):
			psi = t / self.sim.star.prot

			rv, _ = self.sim.calculate_activity_RV_signal(psi)
			return (rv - rv.mean()) * 1e3

else:

	class SOAP(Component):
		def __init__(self):
			raise ValueError('SOAP is not available!')
