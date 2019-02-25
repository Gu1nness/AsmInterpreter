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
        self.frame = None
        self.jmpd = False

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
            self.jmpd = True
            self.frame = frame
            return
        if node.op.type == JGE and self.cmp_reg == 1:
            self.jmpd = True
            self.frame = frame
            return
        if node.op.type == JE and self.cmp_reg == 0:
            self.jmpd = True
            self.frame = frame
            return
        if node.op.type == JLE and self.cmp_reg == -1:
            self.jmpd = True
            self.frame = frame
            return
        if node.op.type == JL and self.cmp_reg == -2:
            self.jmpd = True
            self.frame = frame
            return
        if node.op.type == JMPQ:
            self.jmpd = True
            self.frame = frame
            return


    def visit_CmpOp(self, node):
        node.right.pointer = False
        node.left.pointer = True
        left = self.visit(node.left)
        right = self.visit(node.right)
        self.cmp_reg = Number.__cmp__(right, left)

    def visit_CallQOp(self, node):
        addr = self.call_addr
        for (start, end) in self.memory.ranges.keys():
            if start <= addr and addr <= end:
                fct_frame = self.memory.ranges[(start,end)]
                break
        self.visit(fct_frame)

    def visit_RetStmt(self, node):
        ret_addr = self.memory.registers['rbp']
        if ret_addr == 0:
            raise EndOfExecution
        for (start, end) in self.memory.ranges.keys():
            if start <= addr and addr <= end:
                fct_frame = self.memory.ranges[(start,end)]
                break
        return self.visit(fct_frame, start=ret_addr)

    def visit_NullOp(self, node):
        return

    def visit_AddrExpression(self, node):
        return Number('l', node.value)

    def visit_TernaryAddrExpression(self, node):
        return self.visit(reg_1) + self.visit(offset) * self.visit(reg_2)

    def visit_CompoundAddrExpression(self, node):
        if node.token.type == NUMBER:
            if node.pointer:
                addr = self.visit(node.offset) + self.visit(node.register)
                res = self.memory.stack[self.visit(node.offset) + self.visit(node.register)]
                return Number(node.register.value[0], res)
            else:
                return self.visit(node.offset) + self.visit(node.register)
        if node.token.type == ASTERISK:
            return self.memory.stack[self.visit(node.register)]



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
