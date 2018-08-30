"""
SAM: the Stellar Activity Machine
"""
__all__ = ['Planet', 'Earth', 'Jupiter', 
           'Granulation',
           'Offset', 'Slope',
           'WhiteNoise', 'DistributedNoise', 
           'TimeSampling', 'SOAP',
          ]


# units with astropy
from astropy import units
from astropy import constants
ms = units.meter / units.second
kms = units.kilometer / units.second

from ._planet import Planet, Earth, Jupiter, \
                     Offset, Slope
from ._granulation import Granulation
from ._noise import WhiteNoise, DistributedNoise
from ._sampling import TimeSampling

from ._soap import SOAP

