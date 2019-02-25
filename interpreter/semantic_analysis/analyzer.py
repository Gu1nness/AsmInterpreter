# -*- coding:utf8 -*-
from ..syntax_analysis.tree import NodeVisitor
#from ..syntax_analysis.parser import
from .table import *
from ..lexical_analysis.token_type import POP, POPQ, PUSH, PUSHQ
from ..utils.utils import get_functions, get_name, MessageColor
import sys


class SemanticError(Exception):
    pass

def error(message):
    raise SemanticError(message)

def warning(message):
    print(MessageColor.WARNING + message + MessageColor.ENDC)

class SemanticAnalyzer(NodeVisitor):

    class Sizes():
        types = {
            "e" : "32bits",
            "r" : "64bits",
            "l" : "64bits",
            "q" : "64bits",
        }
        order = ('e', 'r', 'l', 'q')

        def __init__(self, ttype):
            self.type = ttype

        def _calc_type(self, other):
            left_order = SemanticAnalyzer.Sizes.order.index(self.type)
            right_order = SemanticAnalyzer.Sizes.order.index(self.type)
            return SemanticAnalyzer.Sizes(SemanticAnalyzer.Sizes.order[max(left_order, right_order)])

        def __add__(self, other):
            return self._calc_type(other)

        def __eq__(self, other):
            return SemanticAnalyzer.Sizes.types[self.type] == SemanticAnalyzer.Sizes.types[other.type]

        def __repr__(self):
            return '{}'.format(self.types[self.order])

        def __str__(self):
            return self.__repr__()

    def __init__(self):
        self.current_scope = None

    def visit_Program(self, node):
        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=self.current_scope,
        )
        self.current_scope = global_scope

        for child in node.children:
            self.visit(child)

        print(self.current_scope)
        if not self.current_scope.lookup('main'):
            error(
                "Error: Undeclared mandatory function main"
            )

        self.current_scope = self.current_scope.enclosing_scope

    def visit_Section(self, node):
        """ type_node  func_name ( params ) body """


        sec_name = node.name.value
        if self.current_scope.lookup(sec_name):
            error(
                "Error: Duplicate identifier '{}' found at line {}".format(sec_name, node.line)
            )
        sec_symbol = SectionSymbol(sec_name, prog_counter=node.prog_counter)
        self.current_scope.insert(sec_symbol)

        for content in node.content:
            self.visit(content)

    def visit_Register(self, node):
        """ A register name """
        reg_name = node.value
        if not self.current_scope.lookup(reg_name):
            error(
                "Error: Unknown register '{}' found at line {}".format(reg_name, node.line)
            )
        return SemanticAnalyzer.Sizes(reg_name[0])

    def _binop(self, node):
        """ A binary operation """
        right_op = node.right
        left_op = node.left
        rtype = self.visit(right_op)
        ltype = self.visit(left_op)
        if node.op.type.endswith("L"):
            return (ltype + SemanticAnalyzer.Sizes("l")) + rtype

    def visit_BinOp(self, node):
        """ A binary operation """
        return self._binop(node)

    def visit_MovOp(self, node):
        """ A mov[l] operation """
        return self._binop(node)

    def visit_CmpOp(self, node):
        """ A cmp[l] operation """
        return self._binop(node)

    def visit_NullOp(self, node):
        return

    def visit_StackOp(self, node):
        expr_type = self.visit(node.expr)
        if node.op.type in [POP, PUSH]:
            return expr_type + SemanticAnalyzer.Sizes("r")
        if node.op.type in [POPQ, PUSHQ]:
            return expr_type + SemanticAnalyzer.Sizes("q")

    def visit_CallQOp(self, node):
        return

    def visit_JmpStmt(self, node):
        return

    def visit_RetStmt(self, node):
        return

    def visit_NoOp(self, node):
        return

    def visit_CompoundAddrExpression(self, node):
        return self.visit(node.register)

    def visit_AddrExpression(self, node):
        return SemanticAnalyzer.Sizes("l")

    def visit_TernaryAddrExpression(self, node):
        reg_1 = self.visit(node.ref_1)
        reg_2 = self.visit(node.ref_2)
        return reg_1 + reg_2

    @staticmethod
    def analyze(tree):
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.visit(tree)
