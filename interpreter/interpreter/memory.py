# -*- coding:utf8 -*-
import random
from collections import OrderedDict
from ctypes import c_int
from ..syntax_analysis.tree import Node, Register, AddrExpression
import sys

class Stack(object):
    def __init__(self, address):
        self._stack = dict({address: 0})
        self._max = address

    def __bool__(self):
        return bool(self._stack)

    def __getitem__(self, key):
        if isinstance(key, int):
            if not self._stack.get(key, False):
                self.__setitem__(key, 0)
            return self._stack[key]
        elif not self._stack.get(key.value, False):
            self.__setitem__(key.value, 0)
        return self._stack[key.value]

    def __setitem__(self, key, value):
        self._stack[key] = value
        self._stack = dict({key : self._stack[key] for key in sorted(self._stack.keys())})
        self._max = max(self._max, key + 4)

    def push(self, variable, length):
        if length == 1:
            key = self._max
            self._stack[key] = c_int(variable.value)
        elif length == 2:
            key = self._max
            key_2 = self._max + 4
            first = self.c_int(variable)
            second = self.c_int(variable >> 32)
            self._stack[key] = first
            self._stack[key_2] = second
            self._max = key_2
        else:
            raise RuntimeError("Unknown int size")

    def pop(self, length):
        result = -1
        if length == 1 and self._stack:
            result = self._stack[self._max]
            del self._stack[self._max]
            self._max -= 4
        elif length == 2 and len(self._stack) >= 2:
            first = self._stack[self._max] << 32
            del self._stack[self._max]
            second = self._stack[self._max - 4]
            del self._stack[self._max - 4]
            self._max -= 8
            return first + second
        else:
            raise RuntimeError("SEGFAULT")

    def __repr__(self):
        keys = [str(key) for key in self._stack.keys()]
        max_len = max(len(key) for key in keys)
        l_1 = "|".join(keys) + "\n"
        res = ""
        for i  in self._stack.keys():
            value = str(self._stack[i])
            remaining_len = max_len - len(value)
            res += value + " " * remaining_len + "|"
        return l_1 + res


class Registers():
    def __init__(self, rsp, rbp):
        self._store = dict()
        for reg in ['ax', 'bx', 'cx', 'dx', 'rax', 'rbx', 'rcx', 'rdx', 'rbp',
                    'rsp', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11', 'r12',
                    'r13', 'r14', 'r15', 'r8d', 'r9d', 'r10d', 'r11d', 'r12d',
                    'r13d', 'r14d', 'r15d','eax', 'ebx', 'ecx', 'edx', 'esp',
                    'esi', 'edi']:
            self._store[reg] = 0
        self.__setitem__('rsp', rsp)
        self.__setitem__('rbp', rbp)


    def __setitem__(self, key, value):
        self._store[key] = value

    def __getitem__(self, key):
        if key in self._store.keys():
            return self._store[key]
        else:
            raise KeyError("Register %s does not exists" % key)

    def __repr__(self):
        res = ""
        res = ["{} : {}\n".format(reg, self._store[reg]) for reg in sorted(self._store.keys())]
        return "".join(res)

class Frame(Node):
    def __init__(self, instr):
        self.prog_counter = instr.prog_counter
        self.instr = instr

class FunctionFrame(Node):
    def __init__(self, section):
        self._start = section.content[0].prog_counter
        self._end = section.content[-1].prog_counter
        self._frames = [Frame(instr) for instr in section.content]

    @property
    def boundaries(self):
        return (self._start, self._end)

class Memory():
    def __init__(self):
        rbp = 0
        rsp = random.randrange(2**16, 2**32-1, 4)
        self.stack = Stack(rsp)
        self.registers = Registers(rsp, rbp)
        self.cmp_reg = 0
        self.ranges = {}
        self.functions = OrderedDict()
        self.frames = {}
        self.prog_counters = []

    def _create_frames(self):
        for function in self.functions:
            for frame in self.functions[function]._frames:
                self.frames[frame.prog_counter] = frame
        self.prog_counters = sorted(self.frames.keys())


    def _check(self, break_points):
        return all([break_point in self.frames.keys() for break_point in break_points])

    def __setitem__(self, item, value):
        if item.register:
            self.registers[item.register] = value % 2**64
            if item.register.startswith('e'):
                self.registers[item.register] %= 2**32
                self.registers['r' + item.register[1:]] = value
                self.registers['r' + item.register[1:]] %= 2**32
            if item.register.endswith('d'):
                self.registers[item.register] %= 2**32
                self.registers[item.register[:-1]] = value
                self.registers[item.register[:-1]] %= 2**32
        else:
            self.stack[item.value] = value

    def __getitem__(self, item):
        return self.functions[item]

    def iadd(self, item, other):
        if item.register:
            self.registers[item.register] += other % 2**64
            if item.register.startswith('e'):
                self.registers[item.register] %= 2**32
                self.registers['r' + item.register[1:]] += other
                self.registers['r' + item.register[1:]] %= 2**32
            if item.register.endswith('d'):
                self.registers[item.register] %= 2**32
                self.registers[item.register[:-1]] += other
                self.registers[item.register[:-1]] %= 2**32
        else:
            self.stack[item.value] += other

    def imul(self, item, other):
        if item.register:
            self.registers[item.register] *= other % 2**64
            if item.register.startswith('e'):
                self.registers[item.register] %= 2**32
                self.registers['r' + item.register[1:]] *= other
                self.registers['r' + item.register[1:]] %= 2**32
            if item.register.endswith('d'):
                self.registers[item.register] %= 2**32
                self.registers[item.register[:-1]] *= other
                self.registers[item.register[:-1]] %= 2**32
        else:
            self.stack[item.value] *= other

    def mul(self, item, other, other_bis):
        if item.register:
            self.registers[item.register] = (other * other_bis) % 2**64
            if item.register.startswith('e'):
                self.registers[item.register] %= 2**32
                self.registers['r' + item.register[1:]] = other * other_bis
                self.registers['r' + item.register[1:]] %= 2**32
        else:
            self.stack[item.value] = other * other_bis

    def isub(self, item, other):
        if item.register:
            self.registers[item.register] -= other % 2**64
            if item.register.startswith('e'):
                self.registers[item.register] %= 2**32
                self.registers['r' + item.register[1:]] -= other
                self.registers['r' + item.register[1:]] %= 2**32
            if item.register.endswith('d'):
                self.registers[item.register] %= 2**32
                self.registers[item.register[:-1]] -= other
                self.registers[item.register[:-1]] %= 2**32
        else:
            self.stack[item.value] -= other

    def iand(self, item, other):
        if item.register:
            self.registers[item.register] &= other % 2**64
            if item.register.startswith('e'):
                self.registers[item.register] %= 2**32
                self.registers['r' + item.register[1:]] &= other
                self.registers['r' + item.register[1:]] %= 2**32
            if item.register.endswith('d'):
                self.registers[item.register] %= 2**32
                self.registers[item.register[:-1]] &= other
                self.registers[item.register[:-1]] %= 2**32
        else:
            self.stack[item.value] &= other

    def ixor(self, item, other):
        if item.register:
            self.registers[item.register] ^= other % 2**64
            if item.register.startswith('e'):
                self.registers[item.register] %= 2**32
                self.registers['r' + item.register[1:]] ^= other
                self.registers['r' + item.register[1:]] %= 2**32
            if item.register.endswith('d'):
                self.registers[item.register] %= 2**32
                self.registers[item.register[:-1]] ^= other
                self.registers[item.register[:-1]] %= 2**32
        else:
            self.stack[item.value] ^= other

    def inot(self, item):
        if item.register:
            self.registers[item.register] = ~self.registers[item.register] % 2**64
            if item.register.startswith('e'):
                self.registers[item.register] %= 2**32
                self.registers['r' + item.register[1:]] = ~self.registers['r' + item.register[1:]]
                self.registers['r' + item.register[1:]] %= 2**32
            if item.register.endswith('d'):
                self.registers[item.register] %= 2**32
                self.registers[item.register[:-1]] = ~self.registers[item.register[:-1]]
                self.registers[item.register[:-1]] %= 2**32
        else:
            self.stack[item.value] = ~self.stack[item.value]

    def ineg(self, item):
        if item.register:
            self.registers[item.register] = -self.registers[item.register] % 2**64
            if item.register.startswith('e'):
                self.registers[item.register] %= 2**32
                self.registers['r' + item.register[1:]] = -self.registers['r' + item.register[1:]]
                self.registers['r' + item.register[1:]] %= 2**32
            if item.register.endswith('d'):
                self.registers[item.register] %= 2**32
                self.registers[item.register[:-1]] = -self.registers[item.register[:-1]]
                self.registers[item.register[:-1]] %= 2**32
        else:
            self.stack[item.value] = -self.stack[item.value]

    def ishl(self, item, other):
        if item.register:
            self.registers[item.register] <<= other % 2**64
            if item.register.startswith('e'):
                self.registers[item.register] %= 2**32
                self.registers['r' + item.register[1:]] <<= other
                self.registers['r' + item.register[1:]] %= 2**32
            if item.register.endswith('d'):
                self.registers[item.register] %= 2**32
                self.registers[item.register[:-1]] <<= other
                self.registers[item.register[:-1]] %= 2**32
        else:
            self.stack[item.value] <<= other

    def ishr(self, item, other):
        if item.register:
            self.registers[item.register] >>= other % 2**64
            if item.register.startswith('e'):
                self.registers[item.register] %= 2**32
                self.registers['r' + item.register[1:]] >>= other
                self.registers['r' + item.register[1:]] %= 2**32
            if item.register.endswith('d'):
                self.registers[item.register] %= 2**32
                self.registers[item.register[:-1]] >>= other
                self.registers[item.register[:-1]] %= 2**32
        else:
            self.stack[item.value] >>= other

    def __repr__(self):
        return "{}\nStack\n{}\n{}".format(
            self.registers,
            '=' * 40,
            self.stack
        )

    def __str__(self):
        return self.__repr__()

    def push(self, value, length):
        self.stack.push(value, length)

    def pop(self, length):
        self.stack.pop(length)

