# -*- coding:utf8 -*-
from .memory import *
from .number import Number
from ..lexical_analysis.lexer import Lexer
from ..lexical_analysis.token_type import *
from ..syntax_analysis.parser import Parser
from ..syntax_analysis.tree import *
from ..semantic_analysis.analyzer import SemanticAnalyzer
from ..utils.utils import get_functions, MessageColor

class EndOfExecution(BaseException):
    pass

class Interpreter(NodeVisitor):

    def __init__(self):
        self.memory = Memory()

    def preload_functions(self, tree):
        for child in tree.children:
            frame = FunctionFrame(node)
            self.memory.functions[node.name] = frame
            self.memory.ranges[frame.boundariess] = node.name
        self.memory._create_frames()

    def visit_FunctionFrame(self, node, start=0):
        current = [frame for frame in self._frames if frame.prog_counter >= start]
        for content in current:
            self.visit(content)

    def visit_Frame(self, node):
        self.visit(node.instr)


    def visit_BinOp(self, node):
        if node.op.type == ADD_OP:
            return self.visit(node.left) + self.visit(node.right)
        if node.op.type == SUB_OP:
            return self.visit(node.left) - self.visit(node.right)
        if node.op.type == AND_OP:
            return self.visit(node.left) & self.visit(node.right)
        if node.op.type == XOR_OP:
            return self.visit(node.left) ^ self.visit(node.right)

    def visit_MovOp(self, node):
        self.memory[self.visit(self.node.left)] = self.visit(self.node.right)

    def visit_StackOp(self, node):
        value = self.visit(node.expr)
        if node.op.type == PUSH:
            self.memory.push(value, length=1)
        if node.op.type == PUSHQ:
            self.memory.push(value, length=2)
        if node.op.type == POP:
            self.memory.pop(value, length=1)
        if node.op.type == POPQ:
            self.memory.pop(value, length=2)

    def visit_JmpStmt(self, node):
        addr = node.jmpaddr
        for (start, end) in self.memory.ranges.keys():
            if start <= addr and addr <= end:
                fct_frame = self.memory.ranges[(start,end)]
                break
        if node.op.type == JG and self.cmp_reg == 2:
            self.visit(fct_frame, start=addr)
        if node.op.type == JGE and self.cmp_reg == 1:
            self.visit(fct_frame, start=addr)
        if node.op.type == JE and self.cmp_reg == 0:
            self.visit(fct_frame, start=addr)
        if node.op.type == JLE and self.cmp_reg == -1:
            self.visit(fct_frame, start=addr)
        if node.op.type == JL and self.cmp_reg == -2:
            self.visit(fct_frame, start=addr)

    def interpret(self, tree):
        self.preload_functions(tree)
        node = self.memory['main']
        res = self.visit(node)
        return res

    @staticmethod
    def run(program):
        try:
            lexer = Lexer(program)
            parser = Parser(lexer)
            tree = parser.parse()
            SemanticAnalyzer.analyze(tree)
            status = Interpreter().interpret(tree)
        except Exception as message:
            print("{}[{}] {} {}".format(
                MessageColor.FAIL,
                type(message).__name__,
                message,
                MessageColor.ENDC
            ))
            status = -1
        print()
        print(MessageColor.OKBLUE + "Process terminated with status {}".format(status) + MessageColor.ENDC)
