from __future__ import division, absolute_import, print_function

from . import multiarray
from . import umath
from .umath import *
from . import numerictypes
from .numerictypes import *


import cPickle as pickle

loads = pickle.loads

__all__ = ['newaxis', 'ndarray', 'flatiter', 'nditer', 'nested_iters', 'ufunc',
           'arange', 'array', 'zeros', 'count_nonzero',
           'empty', 'broadcast', 'dtype', 'fromstring', 'fromfile',
           'frombuffer', 'int_asbuffer', 'where', 'copyto',
           'concatenate', 'fastCopyAndTranspose', 'lexsort', 'set_numeric_ops',
           'can_cast', 'promote_types', 'min_scalar_type', 'result_type',
           'asarray', 'asanyarray',
           'empty_like', 'zeros_like',
           'inner', 'dot', 'einsum',
           'fromiter',
           'loads',
           'compare_chararrays', 'putmask',
           'may_share_memory']

__all__.extend(['getbuffer', 'newbuffer'])

ndarray = multiarray.ndarray
flatiter = multiarray.flatiter
nditer = multiarray.nditer
nested_iters = multiarray.nested_iters
broadcast = multiarray.broadcast
dtype = multiarray.dtype
copyto = multiarray.copyto
ufunc = type(sin)


def zeros_like(a, dtype=None, order='K', subok=True):
    res = empty_like(a, dtype=dtype, order=order, subok=subok)
    multiarray.copyto(res, 0, casting='unsafe')
    return res

def extend_all(module):
    adict = {}
    for a in __all__:
        adict[a] = 1
    try:
        mall = getattr(module, '__all__')
    except AttributeError:
        mall = [k for k in module.__dict__.keys() if not k.startswith('_')]
    for a in mall:
        if a not in adict:
            __all__.append(a)

extend_all(umath)
extend_all(numerictypes)

newaxis = None
arange = multiarray.arange
array = multiarray.array
zeros = multiarray.zeros
count_nonzero = multiarray.count_nonzero
empty = multiarray.empty
empty_like = multiarray.empty_like
fromstring = multiarray.fromstring
fromiter = multiarray.fromiter
fromfile = multiarray.fromfile
frombuffer = multiarray.frombuffer
may_share_memory = multiarray.may_share_memory

newbuffer = multiarray.newbuffer
getbuffer = multiarray.getbuffer
int_asbuffer = multiarray.int_asbuffer
where = multiarray.where
concatenate = multiarray.concatenate
fastCopyAndTranspose = multiarray._fastCopyAndTranspose
set_numeric_ops = multiarray.set_numeric_ops
can_cast = multiarray.can_cast
promote_types = multiarray.promote_types
min_scalar_type = multiarray.min_scalar_type
result_type = multiarray.result_type
lexsort = multiarray.lexsort
compare_chararrays = multiarray.compare_chararrays
putmask = multiarray.putmask
einsum = multiarray.einsum

def asarray(a, dtype=None, order=None):

    return array(a, dtype, copy=False, order=order)

def asanyarray(a, dtype=None, order=None):
    return array(a, dtype, copy=False, order=order, subok=True)

inner = multiarray.inner
dot = multiarray.dot

from . import fromnumeric
from .fromnumeric import *
extend_all(fromnumeric)
