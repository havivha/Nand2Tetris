#!/usr/local/bin/python3

import re

NUM     = 1     # number e.g. '123'
ID      = 2     # symbol e.g. 'LOOP'
OP      = 3     # = ; ( ) @ + - & | !
ERROR   = 4     # error in file

# Lexer is very simple.  Almost no error checking! - Assumes input will be program-generated.
# Detects numbers, Ids, and operators.
# Reads the whole .asm program into memory and uses regular expressions to match lexical tokens.

class Lex(object):            
    def __init__(self, file_name):
        file = open(file_name, 'r')
        self._lines = file.read()
        self._tokens = self._tokenize(self._lines.split('\n'))
        self.cur_command = []        # list of tokens for current command
        self.cur_token = (ERROR,0)   # current token of current command   
    
    def __str__(self):
        pass
        
    def has_more_commands(self):
        return self._tokens != []
        
    def next_command(self):
        self.cur_command = self._tokens.pop(0)
        self.next_token()
        return self.cur_command
        
    def has_next_token(self):
        return self.cur_command != []
        
    def next_token(self):
        if self.has_next_token():
            self.cur_token = self.cur_command.pop(0)
        else:
            self.cur_token = (ERROR, 0)
        return self.cur_token
        
    def peek_token(self):
        if self.has_next_token():
            return self.cur_command[0]
        else:
            return (ERROR, 0)
        
    def _tokenize(self, lines):
        return [t for t in [self._tokenize_line(l) for l in lines] if t!=[]]
    
    def _tokenize_line(self, line):
        return [self._token(word) for word in self._split(self._remove_comment(line))]
	
    _comment = re.compile('//.*$')
    def _remove_comment(self, line):
        return self._comment.sub('', line)

    _num_re = r'\d+'
    _id_start = r'\w_.$:'
    _id_re = '['+_id_start+']['+_id_start+r'\d]*'
    _op_re = r'[=;()@+\-&|!]'
    _word = re.compile(_num_re+'|'+_id_re+'|'+_op_re)
    def _split(self, line):
        return self._word.findall(line)
		
    def _token(self, word):
        if   self._is_num(word):     return (NUM, word)
        elif self._is_id(word):      return (ID, word)
        elif self._is_op(word):      return (OP, word)
        else:                        return (ERROR, word)
			
    def _is_op(self, word):
        return self._is_match(self._op_re, word)
        
    def _is_num(self, word):
        return self._is_match(self._num_re, word)
        
    def _is_id(self, word):
        return self._is_match(self._id_re, word)
        
    def _is_match(self, re_str, word):
        return re.match(re_str, word) != None