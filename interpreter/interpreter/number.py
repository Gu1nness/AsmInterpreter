# -*- coding:utf8 -*-
class Number(object):
    types = {
        "f" : "8bits",
        "e" : "32bits",
        "r" : "64bits",
        "l" : "64bits",
        "q" : "64bits",
    }
    order = ('f', 'e', 'r', 'l', 'q')

    def __init__(self, ttype, value):
        self.type = ttype
        self.value = Number.types[ttype](value)

    def _get_res_type(self, other):
        left_order = Number.order.index(self.type)
        right_order = Number.order.index(other.type)
        ttype = Number.order[max(left_order, right_order)]
        return ttype, Number.types[ttype]

    def __add__(self, other):
        """ self + other """
        ttype, ctype = self._get_res_type(other)
        return Number(ttype, ctype(self.value) + ctype(other.value))

    def __sub__(self, other):
        """ self - other """
        ttype, ctype = self._get_res_type(other)
        return Number(ttype, ctype(self.value) - ctype(other.value))

    def __mul__(self, other):
        """ self * other """
        ttype, ctype = self._get_res_type(other)
        return Number(ttype, ctype(self.value) * ctype(other.value))

    def __truediv__(self, other):
        """ self / other """
        ttype, ctype = self._get_res_type(other)
        if ctype == int:
            return Number(ttype, ctype(self.value) // ctype(other.value))
        return Number(ttype, ctype(self.value) / ctype(other.value))

    def __mod__(self, other):
        """ self % other """
        ttype, ctype = self._get_res_type(other)

        if ctype != int:
            raise TypeError("invalid operands of types '{}' and '{}' to binary ‘operator %’".format(
                self.type,
                other.type
            ))
        return Number(ttype, ctype(self.value) % ctype(other.value))

    def __div_mod__(self, other):
        return (self.__truediv__(other), self.__mod__(other))


    def __cmp__(self, other):
        if self.value < other.value:
            return -2
        if self.value <= other.value:
            return -1
        if self.value == other.value:
            return 0
        if self.value >= other.value:
            return 1
        if self.value > other.value:
            return 2

    def __and__(self, other):
        """ self & other """
        ttype, ctype = self._get_res_type(other)
        return Number(ttype, int(ctype(self.value) & ctype(other.value)))

    def __or__(self, other):
        """ self | other """
        ttype, ctype = self._get_res_type(other)
        return Number(ttype, int(ctype(self.value) | ctype(other.value)))

    def __xor__(self, other):
        """ self ^ other """
        ttype, ctype = self._get_res_type(other)
        return Number(ttype, int(ctype(self.value) ^ ctype(other.value)))


    def __bool__(self):
        return bool(self.value)

    def __repr__(self):
        return '{} ({})'.format(
            self.type,
            self.value
        )

    def __str__(self):
        return self.__repr__()
