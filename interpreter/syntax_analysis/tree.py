# -*- coding:utf8 -*-
import sys

class Node(object):
    def __init__(self, prog_counter, line):
        self.line = line
        self.prog_counter = prog_counter


class NoOp(Node):
    pass

class Section(Node):
    def __init__(self, name, prog_counter, content, line):
        Node.__init__(self, prog_counter, line)
        self.prog_counter = prog_counter # A struct name
        self.name = name
        self.content = content

class AddrExpression(Node):
    def __init__(self, token, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.token = token
        self.value = token.value

class TernaryAddrExpression(Node):
    def __init__(self, token, reg_1, reg_2, offset, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.token = token
        self.reg_1, self.reg_2 = reg_1, reg_2
        self.offset = offset
        self.value = token.value

class CompoundAddrExpression(Node):
    def __init__(self, token, offset, register, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.token = token
        self.offset = offset
        self.register = register

class Register(Node):
    def __init__(self, token, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.token = token
        self.value = token.value

class BinOp(Node):
    def __init__(self, left, op, right, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.left = left
        self.token = self.op = op
        self.right = right

class UnOp(Node):
    def __init__(self, operand, op, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.operand = operand
        self.token = self.op = op

class XchgOp(Node):
    def __init__(self, left, op, right, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.left = left
        self.token = self.op = op
        self.right = right

class MovOp(Node):
    def __init__(self, left, op, right, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.left = left
        self.token = self.op = op
        self.right = right

class CmpOp(Node):
    def __init__(self, left, op, right, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.left = left
        self.token = self.op = op
        self.right = right

class NullOp(Node):
    def __init__(self, op, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.token = self.op = op

class StackOp(Node):
    def __init__(self, op, expr, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.token = self.op = op
        self.expr = expr

class CallQOp(Node):
    def __init__(self, call_addr, ret_addr, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.call_addr = call_addr


class JmpStmt(Node):
    def __init__(self, op, jmpaddr, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.token = self.op = op
        self.jmpaddr = jmpaddr
        self.line = line

class RetStmt(Node):
    def __init__(self, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.prog_counter= prog_counter
        self.line = line

class Program(Node):
    def __init__(self, sections, prog_counter, line):
        Node.__init__(self, prog_counter, line)
        self.children = sections


###############################################################################
#                                                                             #
#  AST visitors (walkers)                                                     #
#                                                                             #
###############################################################################

class NodeVisitor(object):
    def visit(self, node, dtype=None):
        #sys.stderr.write("%s\n" % self.__dict__)
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

