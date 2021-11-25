import os
from pathlib import Path

from setuptools import setup
from Cython.Build import cythonize

path = Path(os.getcwd()) / 'encrypted' / 'loader.py'
setup(ext_modules=cythonize(path.as_posix()), )
