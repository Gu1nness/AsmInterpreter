# -*- coding:utf8 -*-
###############################################################################
#                                                                             #
#  SYMBOLS, TABLES                                                            #
#                                                                             #
###############################################################################
from collections import OrderedDict

class Symbol(object):
    def __init__(self, name):
        self.name = name

class AddrSymbol(Symbol):
    def __init__(self, name, addr, prog_counter):
        super(VarSymbol, self).__init__(name)
        self.addr = addr
        self.prog_counter = prog_counter

    def __str__(self):
        return "<{class_name}(name='{name}', addr='{addr}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            addr=self.addr,
        )

    __repr__ = __str__

class SectionSymbol(Symbol):
    def __init__(self, sec_name, prog_counter):
        Symbol.__init__(self, sec_name)
        self.prog_counter = prog_counter

class RegisterSymbol(Symbol):
    def __init__(self, name, value=None):
        super(Symbol, self).__init__()
        self.name = name
        self.value = value

    def __str__(self):
        return "<{class_name}(name='{name}', value='{value}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            value=self.value,
        )

REGISTERS = [
    ('ax', RegisterSymbol('ax', 0)),
    ('bx', RegisterSymbol('bx', 0)),
    ('cx', RegisterSymbol('cx', 0)),
    ('dx', RegisterSymbol('dx', 0)),
    ('rax', RegisterSymbol('rax', 0)),
    ('rbx', RegisterSymbol('rbx', 0)),
    ('rcx', RegisterSymbol('rcx', 0)),
    ('rdx', RegisterSymbol('rdx', 0)),
    ('eax', RegisterSymbol('eax', 0)),
    ('ebx', RegisterSymbol('ebx', 0)),
    ('ecx', RegisterSymbol('ecx', 0)),
    ('edx', RegisterSymbol('edx', 0)),
    ('esp', RegisterSymbol('esp', 0)),
    ('esi', RegisterSymbol('esi', 0)),
    ('edi', RegisterSymbol('edi', 0)),
    ('rbp', RegisterSymbol('rbp', 0)),
    ('rax', RegisterSymbol('rax', 0)),
    ('rbx', RegisterSymbol('rbx', 0)),
    ('rcx', RegisterSymbol('rcx', 0)),
    ('rdx', RegisterSymbol('rdx', 0)),
    ('rsp', RegisterSymbol('rsp', 0)),
    ('rsi', RegisterSymbol('rsi', 0)),
    ('rdi', RegisterSymbol('rdi', 0)),
    ('r8', RegisterSymbol('r8', 0)),
    ('r9', RegisterSymbol('r9', 0)),
    ('r10', RegisterSymbol('r10', 0)),
    ('r11', RegisterSymbol('r11', 0)),
    ('r12', RegisterSymbol('r12', 0)),
    ('r13', RegisterSymbol('r13', 0)),
    ('r14', RegisterSymbol('r14', 0)),
    ('r15', RegisterSymbol('r15', 0)),
]

class ScopedSymbolTable(object):
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbols = OrderedDict(REGISTERS)
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in (
            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level),
            ('Enclosing scope',
             self.enclosing_scope.scope_name if self.enclosing_scope else None
            )
        ):
            lines.append('%-15s: %s' % (header_name, header_value))
        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s

    __repr__ = __str__

    def insert(self, symbol):
        # print('Insert: %s' % symbol.name)
        self._symbols[symbol.name] = symbol

    def lookup(self, name, current_scope_only=False, struct=False):
        #print('Lookup: %s. (Scope name: %s)' % (name, self.scope_name))
        # 'symbol' is either an instance of the Symbol class or None
        symbol = self._symbols.get(name)

        if symbol is not None:
            return symbol

        if current_scope_only:
            return None

        # recursively go up the chain and lookup the name
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)
