"""Module containing non-deprecated functions borrowed from Numeric.

"""
from __future__ import division, absolute_import, print_function

import types
from .numeric import asarray


# functions that are methods
__all__ = [
        'amax', 'amin',
        'mean',
        'round_'
        ]

try:
    _gentype = types.GeneratorType
except AttributeError:
    _gentype = type(None)

# save away Python sum

def amax(a, axis=None, out=None, keepdims=False):
    if type(a) is not mu.ndarray:
        try:
            amax = a.max
        except AttributeError:
            return _methods._amax(a, axis=axis,
                                out=out, keepdims=keepdims)
        # NOTE: Dropping the keepdims parameter
        return amax(axis=axis, out=out)
    else:
        return _methods._amax(a, axis=axis,
                            out=out, keepdims=keepdims)

def amin(a, axis=None, out=None, keepdims=False):
    if type(a) is not mu.ndarray:
        try:
            amin = a.min
        except AttributeError:
            return _methods._amin(a, axis=axis,
                                out=out, keepdims=keepdims)
        # NOTE: Dropping the keepdims parameter
        return amin(axis=axis, out=out)
    else:
        return _methods._amin(a, axis=axis,
                            out=out, keepdims=keepdims)

def round_(a, decimals=0, out=None):
    try:
        round = a.round
    except AttributeError:
        return _wrapit(a, 'round', decimals, out)
    return round(decimals, out)

def mean(a, axis=None, dtype=None, out=None, keepdims=False):
    if type(a) is not mu.ndarray:
        try:
            mean = a.mean
            return mean(axis=axis, dtype=dtype, out=out)
        except AttributeError:
            pass

    return _methods._mean(a, axis=axis, dtype=dtype,
                            out=out, keepdims=keepdims)

