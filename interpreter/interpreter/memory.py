# -*- coding:utf8 -*-
import random
from ctypes import c_int
from ..syntax_analysis.tree import Node

class Stack(object):
    def __init__(self, address):
        self._stack = dict({address: 0})

    def __bool__(self):
        return bool(self._stack)

    def __setitem__(self, key, value):
        self._stack[key] = value
        self._stack = dict({key : self._stack[key] for key in sorted(self._stack.key())})

    def __getitem___(self, key):
        return self._stack[key]

    def push(self, variable, length):
        if length == 1:
            self._stack.append(c_int(variable))
        elif length == 2:
            first = self.c_int(variable)
            second = self.c_int(variable >> 32)
            self._stack.append(first)
            self._stack.append(second)
        else:
            raise RuntimeError("Unknown int size")

    def pop(self, length):
        result = -1
        if length == 1 and self._stack:
            result = self._stack.pop()
        elif length == 2 and len(self._stack) >= 2:
            first = self._stack.pop() << 32
            second = self._stack.pop()
            return first + second
        else:
            raise RuntimeError("SEGFAULT")

    def __repr__(self):
        return '|'.join([self._stack[key] for key in sorted(self._stack.keys)])


class Registers():
    def __init__(self, rsp, rbp):
        self._store = dict()
        for reg in ['rax', 'rbx', 'rcx', 'rdx', 'eax', 'ebx', 'ecx', 'edx',
                  'rbp', 'rax', 'rbx', 'rcx', 'rdx', 'rsp', 'rsi', 'rdi',
                  'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15']
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

class Frame(Node):
    def __init__(self, instr):
        self.prog_counter = instr.prog_counter
        self.instr = instr

class FunctionFrame(Node):
    def __init__(self, section):
        self._start = section[0].prog_counter
        self._end = section[-1].prog_counter
        self._frames = [Frame(instr) for instr in section]

    @property
    def boundaries(self):
        return (self._start, self.end)

class Memory():
    def __init__(self):
        self.global_frame = Frame('GLOBAL_MEMORY', None)
        rbp = 0
        rsp = random.randrange(2**16, 2**32-1)
        self.stack = Stack(rsp)
        self.registers = Registers(rsp, rbp)
        self.cmp_reg = 0
        self.ranges = {}
        self.functions = OrderedDict()
        self.frames = []

    def _create_frames(self)
        for function in self.functions:
            for frame in function._frames:
                self.frames[frame.prog_counter] = frame

    def __setitem__(self, item, value):
        if isinstance(item, Register):
            self.registers[item.value] = value
        elif isinstance(item, AddrExpression):
            self.stack[item] = key

    def __getitem__(self, item):
        return self.functions[item]

    def __repr__(self):
        return "{}\nStack\n{}\n{}".format(
            self.global_frame,
            '=' * 40,
            self.stack
        )

    def __str__(self):
        return self.__repr__()

    def push(self, value, length):
        self.stack.push(value, length)

    def push(self, value, length):
        self.stack.push(value, length)

