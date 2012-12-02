#!/usr/local/bin/python3

import Lex

# Parser assumes correctly-formed input - no error checking!

class Parser(object):
    lex = 0
    
    _cmd_type = -1
    _symbol = ''
    _dest = ''
    _comp = ''
    _jmp = ''
    
    def __init__(self, file):
        self.lex = Lex.Lex(file)
    
    def __str__(self):
        pass
        
    def has_more_commands(self):
        return self.lex.has_more_commands()
    
    def advance(self):
        self.lex.next_command()
        (tok_type, value) = self.lex.cur_token
        self._symbol = self._dest = self._comp = self._jmp = ''
        if tok_type == self.lex.OP and value == '@':
            self.a_command()
        elif tok_type == self.lex.OP and value == '(':
            self.l_command()
        else:
            self.c_command(tok_type, value)
    
    A_COMMAND = 0
    C_COMMAND = 1
    L_COMMAND = 2
    
    # @symbol or @number
    def a_command(self):
        self._cmd_type = self.A_COMMAND
        (tok_type, self._symbol) = self.lex.next_token()
        
    # (symbol)
    def l_command(self):
        self._cmd_type = self.L_COMMAND
        (tok_type, self._symbol) = self.lex.next_token()

    # dest=comp;jump
    # dest=comp         omitting jump
    # comp;jump         omitting dest
    # comp              omitting dest and jump
    def c_command(self, tok1, val1):
        self._cmd_type = self.C_COMMAND
        comp_tok, comp_val = self.get_dest(tok1, val1)
        jump_tok, jump_val = self.get_comp(comp_tok, comp_val)
        self.get_jump(jump_tok, jump_val)

    def get_dest(self, tok1, val1):
        tok2, val2 = self.lex.next_token()
        if tok2 == self.lex.OP and val2 == '=':
            self._dest = val1
            comp_tok, comp_val = self.lex.next_token()
        else:
            comp_tok, comp_val = tok1, val1
        return (comp_tok, comp_val)
    
    def get_comp(self, tok, val):
        if tok == self.lex.OP and (val == '-' or val == '!'):
            tok2, val2 = self.lex.next_token()
            self._comp = val+val2
        elif tok == self.lex.NUM or tok == self.lex.ID:
            self._comp = val
            tok2, val2 = self.lex.next_token()
            if tok2 == self.lex.OP and val2 != ';':
                tok3, val3 = self.lex.next_token()
                self._comp += val2+val3
        jump_tok, jump_val = self.lex.next_token()
        return (jump_tok, jump_val)
        
    def get_jump(self, tok, val):
        if self.lex.has_next_token():
            jump_tok, jump_val = self.lex.next_token()
            self._jmp = jump_val
        
    def command_type(self):
        return self._cmd_type 
        
    def symbol(self):
        return self._symbol
    
    def dest(self):
        return self._dest
    
    def comp(self):
        return self._comp
        
    def jmp(self):
        return self._jmp