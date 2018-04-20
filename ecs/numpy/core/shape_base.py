from __future__ import division, absolute_import, print_function

__all__ = ['atleast_2d']

from .numeric import asanyarray, newaxis

def atleast_2d(*arys):
    res = []
    for ary in arys:
        ary = asanyarray(ary)
        if len(ary.shape) == 0 :
            result = ary.reshape(1, 1)
        elif len(ary.shape) == 1 :
            result = ary[newaxis,:]
        else :
            result = ary
        res.append(result)
    if len(res) == 1:
        return res[0]
    else:
        return res



