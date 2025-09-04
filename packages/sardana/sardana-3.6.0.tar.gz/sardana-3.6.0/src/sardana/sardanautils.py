#!/usr/bin/env python

##############################################################################
##
# This file is part of Sardana
##
# http://www.sardana-controls.org/
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Sardana is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Sardana is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This module is part of the Python Sardana library. It defines some
utility methods"""



__all__ = ["is_pure_str", "is_non_str_seq", "is_integer", "is_number",
           "is_bool", "check_type", "assert_type", "str_to_value",
           "is_callable", "py2_round", "recur_map"]

__docformat__ = 'restructuredtext'

import math
import numpy
import numbers
import collections

from sardana.sardanadefs import DataType, DataFormat, DTYPE_MAP, R_DTYPE_MAP

__str_klasses = [str]
__int_klasses = [int, numpy.integer]
__number_klasses = [numbers.Number, numpy.number]

__DTYPE_MAP = dict(DTYPE_MAP)

__bool_klasses = [bool] + __int_klasses

__str_klasses = tuple(__str_klasses)
__int_klasses = tuple(__int_klasses)
__number_klasses = tuple(__number_klasses)
__bool_klasses = tuple(__bool_klasses)


def is_pure_str(obj):
    return isinstance(obj, __str_klasses)


def is_non_str_seq(obj):
    return isinstance(obj, collections.abc.Sequence) and not is_pure_str(obj)


def is_integer(obj):
    return isinstance(obj, __int_klasses)


def is_number(obj):
    return isinstance(obj, __number_klasses)


def is_bool(obj):
    return isinstance(obj, __bool_klasses)


def is_callable(obj):
    return hasattr(obj, "__call__")

__METH_MAP = {
    DataType.Integer: is_integer,
    DataType.Double: is_number,
    DataType.String: is_pure_str,
    DataType.Boolean: is_bool,
}


def check_type(type_info, value):
    tinfo = __DTYPE_MAP.get(type_info, type_info)
    tmeth = __METH_MAP.get(tinfo, type_info)
    return tmeth(value)


def assert_type(type_info, value):
    ret = check_type(type_info, value)
    if not ret:
        expected = R_DTYPE_MAP[type_info]
        recv = type(value)
        try:
            expected = expected.__name__
        except:
            expected = str(expected)
        try:
            recv = recv.__name__
        except:
            recv = str(recv)
        raise TypeError("Expected %s, but received %s" % (expected, recv))
    return ret

_DTYPE_FUNC = {
    DataType.Integer: int,
    DataType.Double: float,
    DataType.String: str,
    DataType.Boolean: bool,
}


def str_to_value(value, dtype=DataType.Double, dformat=DataFormat.Scalar):
    f = _DTYPE_FUNC[dtype]
    if dformat == DataFormat.Scalar:
        ret = f(value)
    elif dformat == DataFormat.OneD:
        ret = [f(v) for v in value]
    elif dformat == DataFormat.TwoD:
        ret = []
        for v1 in value:
            ret.append([f(v2) for v2 in v1])
    return ret


def py2_round(x, d=0):
    p = 10 ** d
    if x > 0:
        return float(math.floor((x * p) + 0.5)) / p
    else:
        return float(math.ceil((x * p) - 0.5)) / p


def recur_map(fun, data, keep_none=False):
    """Recursive map. Similar to map, but maintains the list objects structure

    :param fun: <callable> the same purpose as in map function
    :param data: <object> the same purpose as in map function
    :param keep_none: <bool> keep None elements without applying fun
    """
    if hasattr(data, "__iter__") and not isinstance(data, str):
        return [recur_map(fun, elem, keep_none) for elem in data]
    else:
        if keep_none is True and data is None:
            return data
        else:
            return fun(data)


def interleave_two_lists(lst1, lst2):
    """Merge the given lists in an interleaved fashion,
    provided that the two lists are of equal length.

    Example:

        Input : lst1 = [1, 2, 3]
                lst2 = ['a', 'b', 'c']
        Output : [1, 'a', 2, 'b', 3, 'c']
    """
    return list(sum(zip(lst1, lst2), ()))


def interleaved_list_to_dict(lst):
    """Convert interleaved list of keys and values to dict
    
    Example:

        Input :  [1, 'a', 2, 'b', 3, 'c']            
        Output : {1: 'a', 2: 'b', 3: 'c'}
    """
    keys = lst[::2]
    values = lst[1::2]
    return dict(zip(keys, values))
