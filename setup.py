from setuptools import setup
from Cython.Build import cythonize
from pathlib import Path
import os

path = Path(os.getcwd()) / 'encrypt' / 'loader.py'
setup(
    ext_modules=cythonize(path.as_posix()),
)
