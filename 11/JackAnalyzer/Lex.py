#!/usr/local/bin/python3

import re, os
from xml.sax.saxutils import escape
from JackConstant import *

# This lexer recognizes Jack tokens.  Attempts to generate helpful error messages.
# Reads the whole .jack program into memory and uses regular expressions to match lexical tokens.

class Lex(object):
    def __init__(self, file):
        infile = open(file, 'r')
        self._lines = infile.read()
        self._tokens = self._tokenize(self._lines)
        self._tokens.reverse()
        self._token_type = T_ERROR  # Current token type
        self._cur_val = 0           # Current token value
    
    def has_more_tokens(self):
        return self._tokens != []
        
    def advance(self):
        if self.has_more_tokens():
            self._token_type, self._cur_val = self._tokens.pop()
        else:
            self._token_type, self._cur_val = (T_ERROR, 0)
        return (self._token_type, self._cur_val)
        
    def peek(self):
        if self.has_more_tokens():
            return self._tokens[-1]
        else:
            return (T_ERROR, 0)

    def token_type(self):
        return self._token_type
        
    def keyword(self):
        return self._cur_val
        
    def symbol(self):
        return self._cur_val
        
    def identifier(self):
        return self._cur_val
        
    def int_val(self):
        return self._cur_val
        
    def string_val(self):
        return self._cur_val
                
    def _tokenize(self, lines):
        return [self._token(word) for word in self._split(self._remove_comments(lines))]
	
    _comment_re = re.compile(r'//[^\n]*\n|/\*(.*?)\*/', re.MULTILINE|re.DOTALL)
    def _remove_comments(self, line):
        return self._comment_re.sub('', line)

    _keyword_re = '|'.join([k+r'(?=\s)' for k in keywords])
    _sym_re = '['+re.escape(symbols)+']'
    _num_re = r'\d+'
    _str_re = r'"[^"\n]*"'
    _id_re = r'[a-zA-Z_]\w*'
    _word = re.compile(_keyword_re+'|'+_id_re+'|'+_sym_re+'|'+_num_re+'|'+_str_re)
    def _split(self, line):
        return self._word.findall(line)

    def _token(self, word):
        if   self._is_keyword(word):    return (T_KEYWORD, word)
        elif self._is_sym(word):        return (T_SYM, word)
        elif self._is_num(word):        return (T_NUM, word)
        elif self._is_str(word):        return (T_STR, word[1:-1])
        elif self._is_id(word):         return (T_ID, word)
        else:                           return (T_ERROR, word)

    def _is_keyword(self, word):
        return word in keywords     # Don't match _keyword_re in this case.
        
    def _is_sym(self, word):
        return self._is_match(self._sym_re, word)
        
    def _is_num(self, word):
        return self._is_match(self._num_re, word)
        
    def _is_str(self, word):
        return self._is_match(self._str_re, word)
        
    def _is_id(self, word):
        return self._is_match(self._id_re, word)
        
    def _is_match(self, re_str, word):
        return re.match(re_str, word) != None