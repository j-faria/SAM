"""
SAM: the Stellar Activity Machine
"""

__all__ = ['Planet', 'WhiteNoise', 'Simulation']
__version__ = '0.1.dev0'

from planet import Planet
from _noise import WhiteNoise
from _sampling import TimeSampling
