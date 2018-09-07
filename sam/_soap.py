import warnings
from copy import copy
import numpy as np
from .components import Component

try:
	from SOAP import Simulation
	from SOAP.classes import randomActReg, ActiveRegion
	from SOAP.defaults import _default_ACTIVE_REGIONS, _default_STAR
	SOAP_is_available = True
except ImportError:
	SOAP_is_available = False
	with warnings.catch_warnings():
		warnings.simplefilter("module")
		warnings.warn('module SOAP could not be imported.', ImportWarning)

__all__ = ['SOAP']

if SOAP_is_available:

	defaultAR = _default_ACTIVE_REGIONS[0]

	class SOAP(Component):
		def __init__(self, Prot=25, lat=0, lon=0, size=0.1, type='spot',
		             random=False):

			artype = 0 if type.lower() == 'spot' else 1
			ar = ActiveRegion(lon, lat, size, artype)
			
			self.simulation = Simulation(active_regions=[ar,])

			if random:
				self.simulation.active_regions = [randomActReg(),]
			
		def __repr__(self):
			return self.simulation.__repr__()
		def __condensed_repr__(self):
			return self.simulation.__repr__()


		def sample(self, t, *args):
			psi = t / self.simulation.star.prot

			_, rv = self.simulation.calculate_activity_signal(psi)
			return (rv - rv.mean()) * 1e3

else:

	class SOAP(Component):
		def __init__(self):
			raise ValueError('SOAP is not available!')
