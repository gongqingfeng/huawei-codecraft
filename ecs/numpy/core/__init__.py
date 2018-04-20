from __future__ import division, absolute_import, print_function


from . import multiarray
from . import umath
from . import numerictypes as nt
multiarray.set_typeDict(nt.sctypeDict)
from . import numeric
from .numeric import *
from . import fromnumeric
from .fromnumeric import *

from . import getlimits
from .getlimits import *
from . import shape_base
from .shape_base import *
del nt

from .fromnumeric import amax as max, amin as min, \
     round_ as round
from .numeric import absolute as abs

__all__ = []
__all__ += numeric.__all__
__all__ += fromnumeric.__all__
__all__ += getlimits.__all__
__all__ += shape_base.__all__


# Make it possible so that ufuncs can be pickled
#  Here are the loading and unloading functions
# The name numpy.core._ufunc_reconstruct must be
#   available for unpickling to work.
def _ufunc_reconstruct(module, name):
    mod = __import__(module)
    return getattr(mod, name)

def _ufunc_reduce(func):
    from pickle import whichmodule
    name = func.__name__
    return _ufunc_reconstruct, (whichmodule(func, name), name)


import sys
import copy_reg as copyreg

copyreg.pickle(ufunc, _ufunc_reduce, _ufunc_reconstruct)
# Unclutter namespace (must keep _ufunc_reconstruct for unpickling)
del copyreg
del sys
del _ufunc_reduce
