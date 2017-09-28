"""
SAM: the Stellar Activity Machine
"""

__all__ = ['Planet', 'WhiteNoise', 'Simulation']
__version__ = '0.0.1'

from _planet import Planet
from _noise import WhiteNoise
from _sampling import TimeSampling

# units with Pint 
from pint import UnitRegistry as _UnitRegistry
units = _UnitRegistry()
_Q = units.Quantity
