#!/usr/local/bin/python3

import Lex
from VMConstant import *

# Parser assumes correctly-formed input - no error checking!  Expects program-generated input.
# Would do a recursive-descent parser for fun, but as with the assembler, it's just overkill for this.
# Parser just looks ahead one or two tokens to determine what's there.

class Parser(object):
    # Command types
    _command_type = {'add':C_ARITHMETIC, 'sub':C_ARITHMETIC, 'neg':C_ARITHMETIC,
                     'eq' :C_ARITHMETIC, 'gt' :C_ARITHMETIC, 'lt' :C_ARITHMETIC,
                     'and':C_ARITHMETIC, 'or' :C_ARITHMETIC, 'not':C_ARITHMETIC,
                     'label':C_LABEL,    'goto':C_GOTO,      'if-goto':C_IF, 
                     'push':C_PUSH,      'pop':C_POP, 
                     'call':C_CALL,      'return':C_RETURN,  'function':C_FUNCTION}
                     
    # VM commands can have 0, 1, or 2 arguments.
    _nullary = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not', 'return']
    _unary = ['label', 'goto', 'if-goto']
    _binary = ['push', 'pop', 'function', 'call']
    
    def __init__(self, file):
        self.lex = Lex.Lex(file)
        self._init_cmd_info()
    
    def _init_cmd_info(self):
        self._cmd_type = C_ERROR
        self._arg1 = ''
        self._arg2 = 0
        
    def __str__(self):
        pass
        
    def has_more_commands(self):
        return self.lex.has_more_commands()
    
    # Get the next entire command - each command resides on its own line.
    def advance(self):
        self._init_cmd_info()

        self.lex.next_command()
        tok, val = self.lex.cur_token
        
        if tok != Lex.ID:
            pass    # error
        if val in self._nullary:
            self._nullary_command(val)
        elif val in self._unary:
            self._unary_command(val)
        elif val in self._binary:
            self._binary_command(val)

    # The following methods contain the extracted parts of the command.
    
    def command_type(self):
        return self._cmd_type 
        
    def arg1(self):
        return self._arg1
    
    def arg2(self):
        return self._arg2

    # Parse the different kinds of commands
    def _set_cmd_type(self, id):
        self._cmd_type = self._command_type[id]
        
    def _nullary_command(self, id):
        self._set_cmd_type(id)
        if self._command_type[id] == C_ARITHMETIC:
            self._arg1 = id

    def _unary_command(self, id):
        self._nullary_command(id)
        tok, val = self.lex.next_token()
        self._arg1 = val
        
    def _binary_command(self, id):
        self._unary_command(id)
        tok, val = self.lex.next_token()
        self._arg2 = int(val)