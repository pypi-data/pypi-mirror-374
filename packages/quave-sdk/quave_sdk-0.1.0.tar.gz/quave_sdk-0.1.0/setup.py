from setuptools import setup
from Cython.Build import cythonize

setup(
    name="quave-sdk",
    version="0.1.0",
    packages=["quave_sdk"],
    ext_modules=cythonize(
        ["quave_sdk/**/*.py"],
        exclude=["**/__*.py"],
        language="c",
    ),
    zip_safe=False,
)