"""Machine limits for Float32 and Float64 and (long double) if available...

"""
from __future__ import division, absolute_import, print_function

__all__ = ['finfo', 'iinfo']

from . import numeric
from . import numerictypes as ntypes
from .numeric import array

class finfo(object):
    _finfo_cache = {}

    def __new__(cls, dtype):
        try:
            dtype = numeric.dtype(dtype)
        except TypeError:
            # In case a float instance was given
            dtype = numeric.dtype(type(dtype))

        obj = cls._finfo_cache.get(dtype, None)
        if obj is not None:
            return obj
        dtypes = [dtype]
        newdtype = numeric.obj2sctype(dtype)
        if newdtype is not dtype:
            dtypes.append(newdtype)
            dtype = newdtype
        if not issubclass(dtype, numeric.inexact):
            raise ValueError("data type %r not inexact" % (dtype))
        obj = cls._finfo_cache.get(dtype, None)
        if obj is not None:
            return obj
        if not issubclass(dtype, numeric.floating):
            newdtype = _convert_to_float[dtype]
            if newdtype is not dtype:
                dtypes.append(newdtype)
                dtype = newdtype
        obj = cls._finfo_cache.get(dtype, None)
        if obj is not None:
            return obj
        obj = object.__new__(cls)._init(dtype)
        for dt in dtypes:
            cls._finfo_cache[dt] = obj
        return obj

    def _init(self, dtype):
        self.dtype = numeric.dtype(dtype)
        if dtype is ntypes.double:
            itype = ntypes.int64
            fmt = '%24.16e'
            precname = 'double'
        elif dtype is ntypes.single:
            itype = ntypes.int32
            fmt = '%15.7e'
            precname = 'single'
        elif dtype is ntypes.longdouble:
            itype = ntypes.longlong
            fmt = '%s'
            precname = 'long double'
        elif dtype is ntypes.half:
            itype = ntypes.int16
            fmt = '%12.5e'
            precname = 'half'
        else:
            raise ValueError(repr(dtype))

        machar = MachAr(lambda v:array([v], dtype),
                        lambda v:_frz(v.astype(itype))[0],
                        lambda v:array(_frz(v)[0], dtype),
                        lambda v: fmt % array(_frz(v)[0], dtype),
                        'numpy %s precision floating point number' % precname)

        for word in ['precision', 'iexp',
                     'maxexp', 'minexp', 'negep',
                     'machep']:
            setattr(self, word, getattr(machar, word))
        for word in ['tiny', 'resolution', 'epsneg']:
            setattr(self, word, getattr(machar, word).flat[0])
        self.max = machar.huge.flat[0]
        self.min = -self.max
        self.eps = machar.eps.flat[0]
        self.nexp = machar.iexp
        self.nmant = machar.it
        self.machar = machar
        self._str_tiny = machar._str_xmin.strip()
        self._str_max = machar._str_xmax.strip()
        self._str_epsneg = machar._str_epsneg.strip()
        self._str_eps = machar._str_eps.strip()
        self._str_resolution = machar._str_resolution.strip()
        return self

    def __str__(self):
        return '''\
Machine parameters for %(dtype)s
---------------------------------------------------------------------
precision=%(precision)3s   resolution= %(_str_resolution)s
machep=%(machep)6s   eps=        %(_str_eps)s
negep =%(negep)6s   epsneg=     %(_str_epsneg)s
minexp=%(minexp)6s   tiny=       %(_str_tiny)s
maxexp=%(maxexp)6s   max=        %(_str_max)s
nexp  =%(nexp)6s   min=        -max
---------------------------------------------------------------------
''' % self.__dict__

    def __repr__(self):
        c = self.__class__.__name__
        d = self.__dict__.copy()
        d['klass'] = c
        return ("%(klass)s(resolution=%(resolution)s, min=-%(_str_max)s," \
               + " max=%(_str_max)s, dtype=%(dtype)s)") \
                % d


class iinfo(object):
    _min_vals = {}
    _max_vals = {}

    def __init__(self, int_type):
        try:
            self.dtype = numeric.dtype(int_type)
        except TypeError:
            self.dtype = numeric.dtype(type(int_type))
        self.kind = self.dtype.kind
        self.bits = self.dtype.itemsize * 8
        self.key = "%s%d" % (self.kind, self.bits)
        if not self.kind in 'iu':
            raise ValueError("Invalid integer data type.")

    def min(self):
        """Minimum value of given dtype."""
        if self.kind == 'u':
            return 0
        else:
            try:
                val = iinfo._min_vals[self.key]
            except KeyError:
                val = int(-(1 << (self.bits-1)))
                iinfo._min_vals[self.key] = val
            return val

    min = property(min)

    def max(self):
        """Maximum value of given dtype."""
        try:
            val = iinfo._max_vals[self.key]
        except KeyError:
            if self.kind == 'u':
                val = int((1 << self.bits) - 1)
            else:
                val = int((1 << (self.bits-1)) - 1)
            iinfo._max_vals[self.key] = val
        return val

    max = property(max)

    def __str__(self):
        """String representation."""
        return '''\
Machine parameters for %(dtype)s
---------------------------------------------------------------------
min = %(min)s
max = %(max)s
---------------------------------------------------------------------
''' % {'dtype': self.dtype, 'min': self.min, 'max': self.max}

    def __repr__(self):
        return "%s(min=%s, max=%s, dtype=%s)" % (self.__class__.__name__,
                                    self.min, self.max, self.dtype)
