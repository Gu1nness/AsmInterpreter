# -*- coding:utf8 -*-
""" SAI - Simple Assembly Interpreter """
from string import hexdigits
from .token_type import PUSH, PUSHQ, POP, POPQ, SUB_OP, MOV, MOVL, XOR_OP, AND_OP, CALLQ
from .token_type import SHL_OP, SHR_OP
from .token_type import NOT_OP, NEG_OP
from .token_type import DEC_OP
from .token_type import CMP_OP, CMPL_OP, JLE, JE, JNE, JL, JG, JGE, JMP, JMPQ
from .token_type import NOPW, NOPL, NOP, XCHG, ADD_OP, ADDL_OP, RETQ, HLT, TEST, MUL_OP
from .token_type import LEA_OP
from .token_type import NUMBER, REGISTER, ID, ASTERISK, DOLLAR, LPAREN, RPAREN, COMMA
from .token_type import COLON
from .token import Token

RESERVED_KEYWORDS = {
    'push': Token(PUSH, 'push'),
    'pushq': Token(PUSHQ, 'pushq'),
    'pop': Token(POP, 'pop'),
    'popq': Token(POPQ, 'popq'),
    'sub': Token(SUB_OP, 'sub'),
    'imul': Token(MUL_OP, 'imul'),
    'mov' : Token(MOV, "mov"),
    'movl' : Token(MOVL, "movl"),
    'xor' : Token(XOR_OP, "xor"),
    'shl' : Token(SHL_OP, "shl"),
    'shr' : Token(SHR_OP, "shr"),
    'and' : Token(AND_OP, "and"),
    'not' : Token(NOT_OP, "not"),
    'neg' : Token(NEG_OP, "neg"),
    'dec' : Token(DEC_OP, "dec"),
    'callq' : Token(CALLQ, "callq"),
    'cmp': Token(CMP_OP, 'cmp'),
    'cmpl': Token(CMPL_OP, 'cmpl'),
    'jle': Token(JLE, 'jle'),
    'je': Token(JE, 'je'),
    'jne': Token(JNE, 'jne'),
    'jl': Token(JL, 'jl'),
    'jg': Token(JG, 'jg'),
    'jge': Token(JGE, 'jge'),
    'jmp': Token(JMP, 'jmp'),
    'jmpq': Token(JMPQ, 'jmpq'),
    'nopw': Token(NOPW, 'nopw'),
    'nop': Token(NOP, 'nop'),
    'nopl': Token(NOPL, 'nopl'),
    'xchg': Token(XCHG, 'xchg'),
    'add': Token(ADD_OP, 'add'),
    'addl': Token(ADDL_OP, 'addl'),
    'lea': Token(LEA_OP, 'lea'),
    'retq': Token(RETQ, 'retq'),
    'hlt': Token(HLT, 'hlt'),
    'test': Token(TEST, 'test'),
}

class LexicalError(Exception):
    """ Class was created to isolate lexical errors """

def error(message):
    """ Raise an error. """
    raise LexicalError(message)

class OperationLexer():
    """ Lexer for an assembly operation. """
    def __init__(self, line, line_data):
        self.pos = 0
        self.line = line
        self.current_line = line_data
        self.current_char = self.current_line[0]
        self.tokens = []
        self.parse_operation()


    def advance(self):
        """ Advance the `pos` pointer and set the `current_char` variable. """
        self.pos += 1
        if self.pos >= len(self.current_line):
            self.current_char = None
            return False
        self.current_char = self.current_line[self.pos]
        return True

    def peek(self, n_pos):
        """ Check next n-th char but don't change state. """

        peek_pos = self.pos + n_pos
        if peek_pos > len(self.current_line) - 1:
            self.current_char = None
            return None
        return self.current_line[peek_pos]

    def skip(self, n_pos):
        """ Advance the `pos` pointer of `n` chars, and set the `current_char`
        variable.
        """
        self.pos += n_pos
        if self.pos >= len(self.current_line):
            return False
        self.current_char = self.current_line[self.pos]
        return True

    def skip_whitespace(self):
        """ Skip all whitespaces between tokens from input """
        while self.current_char is not None and self.current_char.isspace():
            if self.current_char == '\n':
                return False
            self.advance()

    def skip_comment(self):
        """ Skip all whitespaces between tokens from input """
        while self.current_char is not None:
            if self.current_char == '\n':
                return False
            self.advance()


    def number(self):
        """ Returns a number written either in hexadecimal or in decimal """
        result = ''
        if self.current_char == "-":
            result = "-"
            self.advance()
        while self.current_char is not None and \
              (self.current_char in hexdigits \
               or self.current_char == 'x'):
            result += self.current_char
            self.advance()
        token = Token(NUMBER, result)
        return token

    def _id(self, register=False):
        """ Handle identifiers and reserved keywords """
        result = ''
        if self.current_char == '<':
            self.advance()
        while self.current_char is not None and (self.current_char.isalnum()\
                                                 or self.current_char == '_'):
            result += self.current_char
            self.advance()
        if register:
            token = Token(REGISTER, result)
        else:
            token = RESERVED_KEYWORDS.get(result, Token(ID, result))

        return token

    def tokenize_operands(self):
        """ Tokenize the operands of an asm operation. """
        res = []
        while self.current_char is not None:
            if self.current_char == '\n':
                return res
            next_token = self.get_next_token()
            if next_token:
                res.append(next_token)

    def parse_operation(self):
        """ Tokenize an asm operation. """
        self.skip_whitespace()
        number = self.number()
        self.pc = number
        res = self.skip(24)
        operation = self._id()
        if not res:
            self.tokens = None
        if operation.value == '' or operation.type in [RETQ, HLT]:
            self.tokens = [number, operation]
            return
        self.skip_whitespace()
        operands = self.tokenize_operands()
        self.tokens = [number, operation] + operands

    def get_next_token(self):
        """ Lexical analyzer (also known as scanner or tokenizer)
        This method is responsible for breaking a sentence
        apart into tokens. One token at a time. """

        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '#':
                self.skip_comment()
                return False

            if self.current_char == "%":
                self.advance()
                return self._id(register=True)

            if self.current_char == "-":
                return self.number()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == '<':
                self.skip_comment()
                return False

            if self.current_char == '*':
                self.advance()
                return Token(ASTERISK, '*')

            if self.current_char == "$":
                self.advance()
                return Token(DOLLAR, "$")

            if self.current_char == "(":
                self.advance()
                return Token(LPAREN, "(")

            if self.current_char == ")":
                self.advance()
                return Token(RPAREN, ")")

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ",")

            if self.current_char == ':':
                self.advance()
                return Token(COLON, ":")

            error(
                message="Invalid char {} at line {}:{}({})".format(
                    self.current_char, self.line, self.pos, self.current_line
                )
            )

class SectionLexer():
    """ Lexer for an assembly section. """
    def __init__(self, line, line_data, source_func):
        self.file_line = line
        self.source_func = source_func
        self.code = line_data
        self.start_line = line_data[0]
        self.line = 0
        self.pos = 0
        self.current_line = self.start_line
        self.current_char = self.current_line[0]
        self.name = ""
        self.operations = []
        self.start_addr = -1
        self.res = self.parse_section()

    def parse_section(self):
        """ Parses the information describing a section. """
        num = self.number()
        self.skip_whitespace()
        identifier = self._id()
        self.start_addr = num
        self.name = identifier
        if self.name.value in self.source_func:
            self.advance()
            self.line += 1
            if self.line >= len(self.code):
                return
            self.current_line = self.code[self.line]
            self.pos = 0
            self.parse_operations()
            return True
        return False

    def number(self):
        """ Returns a number either written in hex of decimal. """
        result = ''
        while self.current_char is not None and \
              (self.current_char in hexdigits \
               or self.current_char == 'x'):
            result += self.current_char
            self.advance()
        token = Token(NUMBER, result)
        return token

    def _id(self, register=False):
        """ Handle identifiers and reserved keywords """
        result = ''
        if self.current_char == '<':
            self.advance()
        while self.current_char is not None and (self.current_char.isalnum()\
                                                 or self.current_char == '_'):
            result += self.current_char
            self.advance()
        if register:
            token = Token(REGISTER, result)
        else:
            token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token

    def advance(self):
        """ Advance the `pos` pointer and set the `current_char` variable. """
        self.pos += 1
        if self.pos >= len(self.current_line) and self.current_line == self.code[-1]:
            self.current_char = None
        elif self.pos >= len(self.current_line):
            self.line += 1
            self.pos = 0
            self.current_line = self.code[self.line]
        self.current_char = self.current_line[self.pos]

    def skip_whitespace(self):
        """ Skip all whitespaces between tokens from input """
        while self.current_char is not None and self.current_char.isspace():
            if self.current_char == '\n':
                return False
            self.advance()

    def parse_operations(self):
        """ parses the operations of the section. """
        while self.current_line is not None:
            self.operations.append(OperationLexer(self.file_line + self.line, self.current_line))
            self.line += 1
            if self.line >= len(self.code):
                return
            self.current_line = self.code[self.line]
            self.pos = 0
            if self.line >= len(self.code):
                self.current_line = None


class Lexer():
    """ The assembly lexer. """
    def __init__(self, text_lines, source_func):
        self.text_lines = text_lines
        self.source_func = source_func
        self.pos = 0
        self.line = 0
        self.section = 0
        self.sections = [[]]
        self.current_line = ""
        self.current_char = ''
        self.parse_file()

    def accumulate_next_section(self):
        """ Accumulate the operations of the next section. """
        start_line = self.line + 1
        while self.current_char != '\n':
            self.sections[-1].append(self.current_line)
            self.line += 1
            if self.line >= len(self.text_lines):
                break
            else:
                self.current_line = self.text_lines[self.line]
                self.current_char = self.current_line[0]
                self.pos = 0
        self.sections[-1] = SectionLexer(start_line, self.sections[-1],
                                         self.source_func)
        if not self.sections[-1].res:
            self.sections[-1] = []
        self.sections += [[]]

    def skip_disassemble_comment(self):
        """ Skip unnecessary data from dissasembly."""
        self.line += 1
        self.current_line = self.text_lines[self.line]
        self.pos = 0
        self.current_char = self.current_char[0]

    def parse_file(self):
        """ Parses the whole file. """
        while self.line < len(self.text_lines):
            if self.line >= len(self.text_lines):
                return
            self.current_line = self.text_lines[self.line]
            self.pos = 0
            self.current_char = self.current_line[self.pos]
            if self.current_line[0].isalpha():
                self.skip_disassemble_comment()
            elif self.current_line[0].isdigit():
                self.accumulate_next_section()
            elif self.current_char == '\n':
                self.line += 1
                self.current_line = self.text_lines[self.line]
                self.pos = 0
                self.current_char = self.current_char[0]
        self.sections = [sec for sec in self.sections if isinstance(sec, SectionLexer)]
