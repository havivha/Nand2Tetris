#!/usr/local/bin/python3

import Lex

# Parser assumes correctly-formed input - no error checking!  Expects program-generated input.
# Would do a recursive-descent parser for fun, but it's just overkill for this.
# Parser just looks ahead one or two tokens to determine what's there.

class Parser(object):
    A_COMMAND = 0
    C_COMMAND = 1
    L_COMMAND = 2
    
    def __init__(self, file):
        self.lex = Lex.Lex(file)
        self._init_cmd_info()
    
    def _init_cmd_info(self):
        self._cmd_type = -1
        self._symbol = ''
        self._dest = ''
        self._comp = ''
        self._jmp = ''
    
    def __str__(self):
        pass
        
    def has_more_commands(self):
        return self.lex.has_more_commands()
    
    # Get the next entire command - each command resides on its own line.
    def advance(self):
        self._init_cmd_info()

        self.lex.next_command()
        tok, val = self.lex.cur_token

        if tok == Lex.OP and val == '@':
            self._a_command()
        elif tok == Lex.OP and val == '(':
            self._l_command()
        else:
            self._c_command(tok, val)
    
    # The following functions contain the extracted parts of the command.
    
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
        
    # @symbol or @number
    def _a_command(self):
        self._cmd_type = Parser.A_COMMAND
        tok_type, self._symbol = self.lex.next_token()
        
    # (symbol)
    def _l_command(self):
        self._cmd_type = Parser.L_COMMAND
        tok_type, self._symbol = self.lex.next_token()

    # dest=comp;jump
    # dest=comp         omitting jump
    # comp;jump         omitting dest
    # comp              omitting dest and jump
    def _c_command(self, tok1, val1):
        self._cmd_type = Parser.C_COMMAND
        comp_tok, comp_val = self._get_dest(tok1, val1)
        self._get_comp(comp_tok, comp_val)
        self._get_jump()

    # Get the 'dest' part if any.  Return the first token of the 'comp' part.
    def _get_dest(self, tok1, val1):
        tok2, val2 = self.lex.peek_token()
        if tok2 == Lex.OP and val2 == '=':
            self.lex.next_token()
            self._dest = val1
            comp_tok, comp_val = self.lex.next_token()
        else:
            comp_tok, comp_val = tok1, val1
        return (comp_tok, comp_val)
    
    # Get the 'comp' part - must be present.
    def _get_comp(self, tok, val):
        if tok == Lex.OP and (val == '-' or val == '!'):
            tok2, val2 = self.lex.next_token()
            self._comp = val+val2
        elif tok == Lex.NUM or tok == Lex.ID:
            self._comp = val
            tok2, val2 = self.lex.peek_token()
            if tok2 == Lex.OP and val2 != ';':
                self.lex.next_token()
                tok3, val3 = self.lex.next_token()
                self._comp += val2+val3
        
    # Get the 'jump' part if any
    def _get_jump(self):
        tok, val = self.lex.next_token()
        if tok == Lex.OP and val == ';':
            jump_tok, jump_val = self.lex.next_token()
            self._jmp = jump_val