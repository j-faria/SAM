"""
SAM: the Stellar Activity Machine
"""
__all__ = ['Planet', 'Offset',
           'WhiteNoise', 'DistributedNoise', 
           'TimeSampling'
          ]

_version_major = 0
_version_minor = 1
_version_micro = 1  # use '' for first of series, number for 1 and above
_version_extra = 'dev'  # use '' for full releases, 'dev' for development

# Construct full version string
_ver = [_version_major, _version_minor]
if _version_micro:
    _ver.append(_version_micro)
if _version_extra:
    _ver.append(_version_extra)
__version__ = '.'.join(map(str, _ver))


# units with Pint 
from pint import UnitRegistry as _UnitRegistry
units = _UnitRegistry()
_Q = units.Quantity

from _planet import Planet, Offset
from _noise import WhiteNoise, DistributedNoise
from _sampling import TimeSampling

