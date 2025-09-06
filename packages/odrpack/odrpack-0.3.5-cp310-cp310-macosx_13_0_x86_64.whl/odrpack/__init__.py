"""`odrpack` is a package for weighted orthogonal distance regression (ODR), also
known as errors-in-variables regression. It is designed primarily for instances
when both the explanatory and response variables have significant errors.
The package implements a highly efficient algorithm for minimizing the sum of
the squares of the weighted orthogonal distances between each data point and the
curve described by the model equation, subject to parameter bounds. The nonlinear
model can be either explicit or implicit. Additionally, `odrpack` can be used to
solve the ordinary least squares problem where all of the errors are attributed
to the observations of the dependent variable.
"""
import importlib.metadata

from odrpack.exceptions import *
from odrpack.odr_fortran import *
from odrpack.odr_scipy import *
from odrpack.result import *

__version__ = importlib.metadata.version(__name__)
