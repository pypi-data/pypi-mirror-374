from setuptools import setup, Extension
import pybind11

matrix_ops = Extension(
    'matrix_ops',
    sources=['matrix_ops.cpp'],
    include_dirs=[pybind11.get_include()],
    extra_compile_args=['-std=c++11'],
    language='c++'
)

# Setup
setup(
    name='matrix_ops',
    version='0.1',
    description='Python package for matrix operations',
    ext_modules=[matrix_ops]
)