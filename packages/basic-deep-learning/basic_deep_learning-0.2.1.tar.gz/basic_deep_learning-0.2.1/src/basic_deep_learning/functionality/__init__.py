"""Core tools for the functionality of basic-deep-learning, including 
encapsulation of matrices and activation function."""

from . import matrix_ops
from .matrix import Matrix
from .activations_registry import ActivationFunctionsRegistry

__all__ = ['Matrix', 'ActivationFunctionsRegistry', 'matrix_ops']