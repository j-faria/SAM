# -*- coding: utf-8 -*-
from setuptools import setup, Extension
# from Cython.Build import cythonize
# from numpy import get_include

extensions = [
    Extension("sam._kepler", ["kepler/_kepler.pyx"],)
]

from sam import __version__

setup(name='sam',
      version=__version__,
      description='The Stellar Activity Machine',
      url='http://github.com/j-faria/SAM',
      author='João Faria',
      author_email='joao.faria@astro.up.pt',
      license='MIT',
      packages=['sam'],
      # ext_modules = cythonize(extensions),
      # extra_compile_args = ["-O2 -w"], 
      # include_dirs = [get_include()],
      zip_safe=False)
