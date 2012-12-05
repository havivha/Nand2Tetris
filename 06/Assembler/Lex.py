#!/usr/local/bin/python3

import re

# Lexer is very simple.  Almost no error checking! - Assumes input will be program-generated.
# Detects numbers, Ids, and operators.
# Reads the whole .asm program into memory and uses regular expressions to match lexical tokens.

class Lex(object):
    def __init__(self, file_name):
        file = open(file_name, 'r')
        self.lines = file.read()
        self.tokens = self.tokenize(self.lines.split('\n'))
    
    def __str__(self):
        pass
        
    NUM     = 1     # number e.g. '123'
    ID      = 2     # symbol e.g. 'LOOP'
    OP      = 3     # = ; ( ) @ + - & | !
    ERROR   = 4     # error in file
            
    lines = []              # list of strings
    tokens = []             # list of token lists, one list per line
    cur_command = []        # list of tokens for current command
    cur_token = (ERROR,0)   # current token of current command
    
    def has_more_commands(self):
        return self.tokens != []
        
    def next_command(self):
        self.cur_command = self.tokens.pop(0)
        self.next_token()
        return self.cur_command
        
    def has_next_token(self):
        return self.cur_command != []
        
    def next_token(self):
        if self.has_next_token():
            self.cur_token = self.cur_command.pop(0)
        else:
            self.cur_token = (self.ERROR, 0)
        return self.cur_token
        
    def peek_token(self):
        if self.has_next_token():
            return self.cur_command[0]
        else:
            return (self.ERROR, 0)
        
    def tokenize(self, lines):
        return [t for t in [self.tokenize_line(l) for l in lines] if t!=[]]
    
    def tokenize_line(self, line):
        return [self.token(word) for word in self.split(self.remove_comment(line))]
	
    _comment = re.compile('//.*$')
    def remove_comment(self, line):
        return self._comment.sub('', line)

    _num_re = r'\d+'
    _id_start = r'\w_.$:'
    _id_re = '['+_id_start+']['+_id_start+r'\d]*'
    _op_re = r'[=;()@+\-&|!]'
    _word = re.compile(_num_re+'|'+_id_re+'|'+_op_re)
    def split(self, line):
        return self._word.findall(line)
		
    def token(self, word):
        if   self.is_num(word):     return (self.NUM, word)
        elif self.is_id(word):      return (self.ID, word)
        elif self.is_op(word):      return (self.OP, word)
        else:                       return (self.ERROR, word)
			
    def is_op(self, word):
        return self.is_match(self._op_re, word)
        
    def is_num(self, word):
        return self.is_match(self._num_re, word)
        
    def is_id(self, word):
        return self.is_match(self._id_re, word)
        
    def is_match(self, re_str, word):
        return re.match(re_str, word) != None