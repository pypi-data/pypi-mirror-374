from setuptools import setup, Extension
import pybind11

ext_args = {
    'extra_compile_args': ['-std=c++11', '-O3'],
    'extra_link_args': [],
}

matrix_ops = Extension(
    'matrix_ops',
    sources=['matrix_ops.cpp'],
    include_dirs=[pybind11.get_include()],
    language='c++',
    **ext_args
)

# Setup
setup(
    name='matrix_ops',
    version='0.1',
    description='Python package for matrix operations',
    ext_modules=[matrix_ops],
    zip_safe=False,
)