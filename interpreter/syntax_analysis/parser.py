# -*- coding:utf8 -*-
""" SCI - Simple C Interpreter """

from ..lexical_analysis.token_type import ID
from ..lexical_analysis.token_type import XOR_OP, AND_OP, ADD_OP, ADDL_OP, SUB_OP, MUL_OP
from ..lexical_analysis.token_type import NOT_OP, NEG_OP, DEC_OP, INC_OP
from ..lexical_analysis.token_type import LEA_OP
from ..lexical_analysis.token_type import SHL_OP, SHR_OP
from ..lexical_analysis.token_type import CMP_OP, CMPL_OP, CMPB_OP, TEST
from ..lexical_analysis.token_type import JL, JG, JGE, JLE, JE, JNE, JMP, JMPQ
from ..lexical_analysis.token_type import POP, POPQ, PUSH, PUSHQ, MOV, MOVL
from ..lexical_analysis.token_type import CALLQ, HLT, RETQ
from ..lexical_analysis.token_type import NOP, NOPW, NOPL, XCHG, DATA16_OP
from ..lexical_analysis.token_type import REGISTER
from ..lexical_analysis.token_type import COMMA, DOLLAR, LPAREN, RPAREN, NUMBER, ASTERISK
from .tree import *

class ProgrammSyntaxError(Exception):
    """ A syntax error in the assembly program. """

def error(message):
    """ An error message. """
    raise ProgrammSyntaxError(message)

class Parser():
    """ The effective Assembly parser, which relies on the lexer. """
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token_line = []
        self.current_token = None

    def eat(self, token_type):
        """ Compare the current token type with the passed token
        type and if they match then "eat" the current token
        and assign the next token to the self.current_token,
        otherwise raise an exception. """
        if self.current_token.type == token_type and self.current_token_line:
            self.current_token_line.pop(0)
            if self.current_token_line:
                self.current_token = self.current_token_line[0]
                return True
            return False
        error(
            'Expected token <{}> but found <{}> at line {}.'.format(
                token_type, self.current_token.type, self.lexer.line
            )
        )

    def program(self):
        """
        program                     : declarations
        """
        root = Program(
            sections=self.sections(),
            line=self.lexer.line,
            prog_counter=0
        )
        return root

    def sections(self):
        """
        sections                    : section+
        """
        sections = []

        for section in self.lexer.sections:
            sections.append(self.section(section))
        return sections

    def section(self, section):
        """
        section                     : NUM ID operations+
        """
        num = section.start_addr
        name = section.name
        content = self.operations(section.operations)
        return Section(
            name=name,
            prog_counter=int(num.value, 16),
            content=content,
            line=section.file_line,
        )

    def operations(self, operations):
        """
        operations                  : operation+
        """
        result = []
        for operation in operations:
            line = operation.line
            prog_counter = int(operation.pc.value, 16)
            self.current_token_line = operation.tokens[1:]
            oper = self.operation(prog_counter=prog_counter, line=line)
            if oper:
                result.append(oper)
        return result

    def operation(self, prog_counter, line):
        """
        operation                   : operator addr_expression{,2}
        """
        self.current_token = self.current_token_line[0]
        if self.current_token.type is CALLQ:
            return self.callqop(prog_counter, line)
        if self.current_token.type in [SUB_OP, XOR_OP, AND_OP, ADD_OP, ADDL_OP,
                                       SHL_OP, TEST]:
            return self.binop(prog_counter, line)
        if self.current_token.type is MUL_OP:
            return self.ternaryop(prog_counter, line)
        if self.current_token.type in [NOT_OP, NEG_OP, DEC_OP, INC_OP]:
            return self.unop(prog_counter, line)
        if self.current_token.type is LEA_OP:
            return self.binop(prog_counter, line)
        if self.current_token.type in [JL, JG, JGE, JLE, JE, JNE, JMP, JMPQ]:
            return self.jmpop(prog_counter, line)
        if self.current_token.type in [CMP_OP, CMPL_OP, CMPB_OP]:
            return self.cmpop(prog_counter, line)
        if self.current_token.type in [POP, POPQ, PUSH, PUSHQ]:
            return self.stackop(prog_counter, line)
        if self.current_token.type in [MOV, MOVL]:
            return self.movop(prog_counter, line)
        if self.current_token.type in [NOP, NOPW, NOPL, DATA16_OP]:
            return self.noop(prog_counter, line)
        if self.current_token.type is XCHG:
            return self.xchgop(prog_counter, line)
        if self.current_token.type is HLT:
            return self.hltop(prog_counter, line)
        if self.current_token.type is RETQ:
            return self.retqop(prog_counter, line)
        if self.current_token.type is ID:
            return None
        error("Unkown operation {} at line {}"
              .format(self.current_token, line)
              )


    def callqop(self, prog_counter, line):
        """
        callqop                     : CALLQ ADDR
        """
        operation = self.current_token
        self.eat(operation.type)
        if self.current_token_line:
            call_addr = self.addr_expression(prog_counter, line)
            if self.current_token.type is COMMA:
                error("incompatible operand with callq operator at line {}"
                      .format(line))
        else:
            error("incompatible operand with callq operator at line {}"
                  .format(self.lexer.line))
        return CallQOp(
            call_addr=call_addr,
            ret_addr=str(int(prog_counter, 16)+0x8),
            prog_counter=prog_counter,
            line=line
        )



    def binop(self, prog_counter, line):
        """
        binqop                      : BINOP ADDR COMMA ADDR
        """
        operation = self.current_token
        self.eat(operation.type)
        left = self.addr_expression(prog_counter, line)
        if self.current_token.type is COMMA:
            self.eat(COMMA)
        else:
            error("Incompatible Operand {} with binary operator {} at line{}"
                  .format(left, operation.value, line)
                  )
        return BinOp(
            left=left,
            op=operation,
            right=self.addr_expression(prog_counter, line),
            prog_counter=prog_counter,
            line=line
        )

    def ternaryop(self, prog_counter, line):
        """
        ternaryop                      : BINOP ADDR COMMA ADDR (COMMA ADDR)?
        """
        operation = self.current_token
        self.eat(operation.type)
        left = self.addr_expression(prog_counter, line)
        if self.current_token.type is COMMA:
            self.eat(COMMA)
        else:
            error("Incompatible Operand {} with binary operator {} at line{}"
                  .format(left, operation.value, line)
                  )
        middle = self.addr_expression(prog_counter, line)
        if self.current_token.type is COMMA:
            self.eat(COMMA)
            right = self.addr_expression(prog_counter, line)
            return TernOp(
                left=left,
                op=operation,
                middle=middle,
                right=right,
                prog_counter=prog_counter,
                line=line
            )
        else:
            return BinOp(
                left=left,
                op=operation,
                right=middle,
                prog_counter=prog_counter,
                line=line
            )

    def unop(self, prog_counter, line):
        """
        unop                        : UNOP ADDR
        """
        operation = self.current_token
        self.eat(operation.type)
        operand  = self.addr_expression(prog_counter, line)
        return UnOp(
            operand=operand,
            op=operation,
            prog_counter=prog_counter,
            line=line
        )


    def jmpop(self, prog_counter, line):
        """
        jmpop                       : JMPOP ADDR
        """
        operation = self.current_token
        self.eat(operation.type)
        addr = self.addr_expression(prog_counter, line)
        if self.current_token.type is COMMA:
            error("Incompatible operand with jump operator {} at line{}"
                  .format(operation.value, line)
                  )
        return JmpStmt(
            op=operation,
            jmpaddr=addr,
            line=line,
            prog_counter=prog_counter
        )

    def cmpop(self, prog_counter, line):
        """
        cmpop                       : CMPOP ADDR COMMA ADDR
        """
        operation = self.current_token
        self.eat(operation.type)
        left = self.addr_expression(prog_counter, line)
        if self.current_token.type is COMMA:
            self.eat(COMMA)
        else:
            error("Incompatible operands with binary operator {} at line{}"
                  .format(operation.value, line)
                  )
        return CmpOp(
            op=operation,
            left=left,
            right=self.addr_expression(prog_counter, line),
            line=line,
            prog_counter=prog_counter
        )

    def stackop(self, prog_counter, line):
        """
        stackop                     : STACKOP ADDR
        """
        operation = self.current_token
        self.eat(operation.type)
        addr = self.addr_expression(prog_counter, line)
        if self.current_token.type is COMMA:
            error("Incompatible operand with stack operator {} at line{}"
                  .format(operation.value, line)
                  )
        return StackOp(
            op=operation,
            expr=addr,
            line=line,
            prog_counter=prog_counter
        )

    def movop(self, prog_counter, line):
        """
        movop                       : MOVOP ADDR COMMA ADDR
        """
        operation = self.current_token
        self.eat(operation.type)
        left = self.addr_expression(prog_counter, line)
        if self.current_token.type is COMMA:
            self.eat(COMMA)
        else:
            error("Incompatible operand with operator {} at line {}:{}"
                  .format(operation.value, line, self.current_token.value)
                  )
        return MovOp(
            left=left,
            op=operation,
            right=self.addr_expression(prog_counter, line),
            prog_counter=prog_counter,
            line=line
        )

    def noop(self, prog_counter, line):
        """
        noop                        : NOP
        """
        operation = self.current_token
        self.eat(operation.type)
        if self.current_token_line:
            _ = self.addr_expression(prog_counter, line)
        return NullOp(
            op=operation,
            line=line,
            prog_counter=prog_counter
        )

    def xchgop(self, prog_counter, line):
        """
        xchgop                      : XCHG ADDR COMMA ADDR
        """
        operation = self.current_token
        self.eat(operation.type)
        left = self.addr_expression(prog_counter, line)
        if self.current_token.type is COMMA:
            self.eat(COMMA)
        else:
            error("Incompatible Operand {} with binary operator xchg at line{}"
                  .format(left, line)
                  )
        return XchgOp(
            left=left,
            op=operation,
            right=self.addr_expression(prog_counter, line),
            prog_counter=prog_counter,
            line=line
        )

    def hltop(self, prog_counter, line):
        """
        hltop                       : HLT
        """
        operation = self.current_token
        res = self.eat(operation.type)
        if not res:
            _ = self.addr_expression(prog_counter, line)
        return NullOp(
            op=operation,
            prog_counter=prog_counter,
            line=line,
        )


    def retqop(self, prog_counter, line):
        """
        retqop                      : RETQ
        """
        operation = self.current_token
        self.eat(operation.type)
        if self.current_token_line:
            _ = self.addr_expression(prog_counter, line)
        return NullOp(
            op=operation,
            prog_counter=prog_counter,
            line=line,
        )

    def addr_expression(self, prog_counter, line):
        """
        addr_exp                    : <HARD STUFF>
        """
        if self.current_token.type is DOLLAR:
            self.eat(DOLLAR)
            if self.current_token.type is NUMBER:
                token = self.current_token
                self.eat(NUMBER)
                return AddrExpression(token, prog_counter, line)
            error("Invalid offset at line %s" % line)
        if self.current_token.type is REGISTER:
            token = self.current_token
            self.eat(REGISTER)
            return Register(token, prog_counter, line)
        if self.current_token.type is NUMBER:
            token = self.current_token
            self.eat(NUMBER)
            if self.current_token.type is LPAREN:
                self.eat(LPAREN)
                register = self.addr_expression(prog_counter, line)
                if self.current_token.type is COMMA:
                    self.eat(COMMA)
                    second_reg = self.addr_expression(prog_counter, line)
                    if self.current_token.type is COMMA:
                        self.eat(COMMA)
                        number = AddrExpression(self.current_token,
                                                prog_counter=prog_counter,
                                                line=line)
                        self.eat(NUMBER)
                        self.eat(RPAREN)
                        return TernaryAddrExpression(
                            token=token,
                            reg_1=register,
                            reg_2=second_reg,
                            offset=number,
                            prog_counter=prog_counter,
                            line=line
                        )
                    error("Wrong compound expression")
                self.eat(RPAREN)
                return CompoundAddrExpression(
                    token,
                    AddrExpression(token, prog_counter, line),
                    register,
                    prog_counter,
                    line
                )
            return AddrExpression(token, prog_counter, line)
        if self.current_token.type is ASTERISK:
            token = self.current_token
            self.eat(ASTERISK)
            compound = self.addr_expression(prog_counter, line)
            return CompoundAddrExpression(
                token,
                AddrExpression(token.value, prog_counter, line),
                compound,
                prog_counter,
                line
            )
        if self.current_token.type is LPAREN:
            self.eat(LPAREN)
            register = self.addr_expression(prog_counter, line)
            if self.current_token.type is COMMA:
                token = self.current_token
                self.eat(COMMA)
                second_reg = self.addr_expression(prog_counter, line)
                if self.current_token.type is COMMA:
                    self.eat(COMMA)
                    number = AddrExpression(self.current_token,
                                            prog_counter=prog_counter,
                                            line=line)
                    self.eat(NUMBER)
                    self.eat(RPAREN)
                    return TernaryAddrExpression(
                        token=token,
                        reg_1=register,
                        reg_2=second_reg,
                        offset=number,
                        prog_counter=prog_counter,
                        line=line
                    )
                error("Wrong compound expression")
            self.eat(RPAREN)



    def parse(self):
        """
        program                     : declarations

        declarations                : declaration operations+

        declaration                 : NUMBER ID

        operations                  : operation | stmt

        operation                   : unop | binop | nullop | noop | stackop | functioncall

        stmt                        : jmpstmt | retstmt

        """
        node = self.program()

        return node
