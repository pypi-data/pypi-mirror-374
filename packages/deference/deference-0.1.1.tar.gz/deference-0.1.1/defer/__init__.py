"""
DEFER: DEnsity Function Estimation using Recursive partitioning

A Python library for efficient Bayesian inference on general problems
involving up to about ten random variables or dimensions.
"""

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"

__author__ = "Erik Bodin"
__email__ = "mail@erikbodin.com"

# Import main classes and functions for easy access
from .tree import MassTree
from .variables import Variable, Variables, VariableSlice
from .approximation import DensityFunctionApproximation
from .bounded_space import BoundedSpace
from .sampling import sampler_in_domains, sampler_of_indices

# Import helper functions
from .helpers import *

__all__ = [
    "MassTree",
    "Variable", 
    "Variables",
    "VariableSlice",
    "DensityFunctionApproximation",
    "BoundedSpace",
    "sampler_in_domains",
    "sampler_of_indices",
]
