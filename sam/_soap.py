import numpy as np
from components import Component

from SOAP import Simulation
from SOAP.classes import randomActReg
__all__ = ['SOAP']

class SOAP(Component):
	def __init__(self, random=False):
		self.sim = Simulation()
		if random:
			self.sim.active_regions = [randomActReg(),]


	def __repr__(self):
		return self.sim.__repr__()


	def sample(self, t):
		psi = t / self.sim.star.prot
		# try:
		# 	if np.allclose(self.sim.PSI, psi): 
		# 		return self.sim.rv_tot * 1e3
		# except AttributeError:
		# 	pass

		rv, _ = self.sim.calculate_activity_RV_signal(psi)
		return rv * 1e3
