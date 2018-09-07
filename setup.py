# -*- coding: utf-8 -*-
from setuptools import setup, Extension
# from Cython.Build import cythonize
# from numpy import get_include

extensions = [
    Extension("sam._kepler", ["kepler/_kepler.pyx"],)
]


## SAM version
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


setup(name='sam',
      version=__version__,
      description='The Stellar Activity Machine',
      url='http://github.com/j-faria/SAM',
      author='João Faria',
      author_email='joao.faria@astro.up.pt',
      license='MIT',
      packages=['sam'],
      install_requires=['astropy',],
      # ext_modules = cythonize(extensions),
      # extra_compile_args = ["-O2 -w"], 
      # include_dirs = [get_include()],
      include_package_data=True,
      zip_safe=False)
