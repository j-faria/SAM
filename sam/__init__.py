"""
SAM: the Stellar Activity Machine
"""
__all__ = ['Planet', 'Earth', 'Jupiter', 
           'Offset', 'Slope',
           'WhiteNoise', 'DistributedNoise', 
           'TimeSampling', 'SOAP',
          ]

# units with Pint 
from pint import UnitRegistry as _UnitRegistry
units = _UnitRegistry()
_Q = units.Quantity

from ._planet import Planet, \
                     Earth, Jupiter, \
                     Offset, Slope
from ._noise import WhiteNoise, DistributedNoise
from ._sampling import TimeSampling
from ._soap import SOAP

