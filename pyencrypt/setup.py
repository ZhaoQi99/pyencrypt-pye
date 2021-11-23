import os
from pathlib import Path

from Cython.Build import cythonize
from setuptools import setup

path = Path(os.getcwd()) / 'encrypted' / 'loader.py'
setup(ext_modules=cythonize(path.as_posix()), )
