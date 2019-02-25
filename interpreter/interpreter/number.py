# -*- coding:utf8 -*-
"""
Defines a number, with all the computations associated to it.
"""
class Number():
    """ A number.
    """

    types = {
        "f" : "8bits",
        "e" : "32bits",
        "r" : "64bits",
        "l" : "64bits",
        "q" : "64bits",
    }
    order = ('f', 'e', 'r', 'l', 'q')

    def __init__(self, ttype, value, register=""):
        self.type = ttype
        self.register = register
        if isinstance(value, str):
            self.value = int(value, 16)
        else:
            self.value = value

    def _get_res_type(self, other):
        left_order = Number.order.index(self.type)
        right_order = Number.order.index(other.type)
        ttype = Number.order[max(left_order, right_order)]
        return ttype, Number.types[ttype]

    def __add__(self, other):
        """ self + other """
        ttype, _ = self._get_res_type(other)
        return Number(ttype, self.value + other.value)

    def __sub__(self, other):
        """ self - other """
        ttype, _ = self._get_res_type(other)
        return Number(ttype, self.value - other.value)

    def minus(self):
        """ - self """
        return  Number(self.type, - self.value)

    def __mul__(self, other):
        """ self * other """
        ttype, _ = self._get_res_type(other)
        return Number(ttype, self.value * other.value)

    def __truediv__(self, other):
        """ self / other """
        ttype, _ = self._get_res_type(other)
        return Number(ttype, self.value // other.value)

    def __mod__(self, other):
        """ self % other """
        ttype, _ = self._get_res_type(other)
        return Number(ttype, self.value % other.value)

    def __div_mod__(self, other):
        """ Div and Mod in the same time. """
        return (self.__truediv__(other), self.__mod__(other))


    def __cmp__(self, other):
        """ Compares two integers """
        if self.value < other.value:
            return -2
        if self.value <= other.value:
            return -1
        if self.value == other.value:
            return 0
        if self.value > other.value:
            return 2
        if self.value >= other.value:
            return 1
        raise Exception("Impossible")

    def __and__(self, other):
        """ self & other """
        ttype, _ = self._get_res_type(other)
        return Number(ttype, int(self.value & other.value))

    def __or__(self, other):
        """ self | other """
        ttype, _ = self._get_res_type(other)
        return Number(ttype, int(self.value | other.value))

    def __xor__(self, other):
        """ self ^ other """
        ttype, _ = self._get_res_type(other)
        return Number(ttype, int(self.value ^ other.value))

    def __bool__(self):
        return bool(self.value)

    def __repr__(self):
        return '{} ({})'.format(
            self.type,
            self.value
        )

    def __str__(self):
        return self.__repr__()
