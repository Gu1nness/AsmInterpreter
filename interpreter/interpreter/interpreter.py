# -*- coding:utf8 -*-
from queue import Queue
from copy import deepcopy
from .memory import *
from .number import Number
from ..lexical_analysis.lexer import Lexer
from ..lexical_analysis.token_type import *
from ..syntax_analysis.parser import Parser
from ..syntax_analysis.tree import *
from ..semantic_analysis.analyzer import SemanticAnalyzer
from ..utils.utils import MessageColor
import sys

AsmQueue = Queue()

class EndOfExecution(BaseException):
    pass

class Interpreter(NodeVisitor):

    def __init__(self, break_points, event):
        self.memory = Memory()
        self.break_points = break_points
        self.cmp_reg = 0
        self.frame = None
        self.jmpd = False
        self.can_run = event
        self.can_run.set()

    def preload_functions(self, tree):
        for child in tree.children:
            frame = FunctionFrame(child)
            self.memory.functions[child.name.value] = frame
            self.memory.ranges[frame.boundaries] = child.name
        self.memory._create_frames()
        if not self.memory._check(self.break_points):
            sys.stderr.write(str(["0x%08x" % key for key in
                                  self.memory.frames.keys()]) + '\n')
            res = ["0x%08x" % break_point for break_point in self.break_points if not
                   break_point in self.memory.frames.keys()]
            sys.stderr.write(str(res) + "\n")
            sys.stderr.flush()
            raise Exception("Breakpoints are not all in the frames")

    def visit_Register(self, node):
        reg = self.memory.registers[node.value]
        return Number(node.value[0], reg, register=node.value)

    def visit_Frame(self, node):
        self.visit(node.instr)

    def visit_UnOp(self, node):
        node.operand.pointer = True
        if node.op.type == NOT_OP:
            self.memory.inot(self.visit(node.operand))
        if node.op.type == NEG_OP:
            self.memory.ineg(self.visit(node.operand))
        if node.op.type == DEC_OP:
            value = self.visit(node.operand)
            self.memory.idec(value)
            if value == 0:
                self.cmp_reg = 0
            else:
                self.cmp_reg = 1
        if node.op.type == INC_OP:
            value = self.visit(node.operand)
            self.memory.iinc(value)
            if value == 0:
                self.cmp_reg = 0
            else:
                self.cmp_reg = 1


    def visit_BinOp(self, node):
        node.right.pointer = False
        node.left.pointer = True
        if node.op.type in [ADD_OP, ADDL_OP]:
            value = self.visit(node.left).value
            self.memory.iadd(self.visit(node.right), value)
            if value == 0:
                self.cmp_reg = 0
            else:
                self.cmp_reg = 1
        if node.op.type == LEA_OP:
            node.right.pointer = False
            node.left.pointer = False
            addr = self.visit(node.right)
            value = self.visit(node.left).value
            self.memory[addr] = self.visit(node.left).value
        if node.op.type == MUL_OP:
            value = self.visit(node.left).value
            self.memory.imul(self.visit(node.right), value)
        if node.op.type == SUB_OP:
            value = self.visit(node.left).value
            self.memory.isub(self.visit(node.right), value)
            if value == 0:
                self.cmp_reg = 0
            else:
                self.cmp_reg = 1
        if node.op.type == AND_OP:
            value = self.visit(node.left).value
            self.memory.iand(self.visit(node.right), value)
            if value == 0:
                self.cmp_reg = 0
            else:
                self.cmp_reg = 1
        if node.op.type == XOR_OP:
            value = self.visit(node.left).value
            self.memory.ixor(self.visit(node.right), value)
            if value == 0:
                self.cmp_reg = 0
            else:
                self.cmp_reg = 1
        if node.op.type == SHL_OP:
            value = self.visit(node.left).value
            self.memory.ishl(self.visit(node.right), value)
            if value == 0:
                self.cmp_reg = 0
            else:
                self.cmp_reg = 1
        if node.op.type == SHR_OP:
            value = self.visit(node.left).value
            self.memory.ishr(self.visit(node.right), value)
            if value == 0:
                self.cmp_reg = 0
            else:
                self.cmp_reg = 1
        if node.op.type == TEST:
            right = self.visit(node.right).value
            left = self.visit(node.left).value
            self.cmp_reg = int(right & left)

    def visit_TernOp(self, node):
        node.right.pointer = False
        node.middle.pointer = True
        node.left.pointer = True
        if node.op.type in [MUL_OP]:
            self.memory.mul(self.visit(node.right),
                            self.visit(node.left).value,
                            self.visit(node.middle).value,
                            )

    def visit_XchgOp(self, node):
        node.right.pointer = False
        node.left.pointer = True
        left = self.visit(node.right)
        right = self.visit(node.left)
        if left.register:
            self.memory.registers[left.register] = right
            if left.register.startswith('e'):
                self.memory.registers['r' + left.register[1:]] = right
        else:
            self.stack[right.value] = left
        if right.register:
            self.memory.registers[right.register] = left
            if right.register.startswith('e'):
                self.memory.registers['r' + right.register[1:]] = left
        else:
            self.stack[right.value] = left


    def visit_MovOp(self, node):
        node.right.pointer = False
        node.left.pointer = True
        addr = self.visit(node.right)
        print("====")
        print(node.right)
        print(addr)
        value = self.visit(node.left).value
        print(value)
        self.memory[addr] = value

    def visit_StackOp(self, node):
        value = self.visit(node.expr)
        if node.op.type == PUSH:
            self.memory.push(value, length=1)
        if node.op.type == PUSHQ:
            self.memory.push(value, length=2)
        if node.op.type == POP:
            self.memory.pop(length=1)
        if node.op.type == POPQ:
            self.memory.pop(length=2)

    def visit_JmpStmt(self, node):
        addr = int(node.jmpaddr.value, 16)
        frame = self.memory.frames[addr]
        if node.op.type == JG and self.cmp_reg == 2:
            self.jmpd = True
            self.frame = frame
            return
        if node.op.type == JGE and self.cmp_reg >= 1:
            self.jmpd = True
            self.frame = frame
            return
        if node.op.type == JE and self.cmp_reg == 0:
            self.jmpd = True
            self.frame = frame
            return
        if node.op.type == JNE and self.cmp_reg != 0:
            self.jmpd = True
            self.frame = frame
            return
        if node.op.type == JLE and self.cmp_reg <= -1:
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
        if node.op.type == JMP:
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
        if node.reg_1:
            return self.visit(node.reg_1) + self.visit(node.offset) * self.visit(node.reg_2)
        else:
            return self.visit(node.offset) * self.visit(node.reg_2)

    def visit_CompoundAddrExpression(self, node):
        if node.token.type == NUMBER:
            if node.pointer:
                #print(node.offset)
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
        self.frame = self.memory.frames[node._start]
        try:
            while True:
                self.can_run.wait()
                self.visit(self.frame)
                if self.frame.prog_counter in self.break_points:
                    AsmQueue.put((self.frame.prog_counter, deepcopy(self.memory)))
                    self.can_run.clear()
                if self.jmpd:
                    self.jmpd = False
                else:
                    index = self.memory.prog_counters.index(self.frame.prog_counter)
                    try:
                        self.frame = self.memory.frames[self.memory.prog_counters[index + 1]]
                    except IndexError:
                        raise EndOfExecution
        except EndOfExecution as _:
            return self.memory.registers['rax']

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
