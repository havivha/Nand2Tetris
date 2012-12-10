#!/usr/local/bin/python3

import re, os

# Token types
T_KEYWORD       = 1     # keyword e.g. 'class', 'false' etc
T_SYM           = 2     # symbol e.g. '{', '}' etc
T_NUM           = 3     # number e.g. '123' - from 0 to 32767
T_STR           = 4     # string e.g. "hello"
T_ID            = 5     # identifier e.g. 'name', 'id_42'
T_ERROR         = 6     # error in file

# Keywords for token type T_KEYWORD
KW_CLASS        = 'class'
KW_METHOD       = 'method'
KW_FUNCTION     = 'function'
KW_CONSTRUCTOR  = 'constructor'
KW_INT          = 'int'
KW_BOOLEAN      = 'boolean'
KW_CHAR         = 'char'
KW_VOID         = 'void'
KW_VAR          = 'var'
KW_STATIC       = 'static'
KW_FIELD        = 'field'
KW_LET          = 'let'
KW_DO           = 'do'
KW_IF           = 'if'
KW_ELSE         = 'else'
KW_WHILE        = 'while'
KW_RETURN       = 'return'
KW_TRUE         = 'true'
KW_FALSE        = 'false'
KW_NULL         = 'null'
KW_THIS         = 'this'
KW_NONE         = ''

keywords = [KW_CLASS, KW_METHOD, KW_FUNCTION, KW_CONSTRUCTOR, KW_INT, KW_BOOLEAN,
            KW_CHAR, KW_VOID, KW_VAR, KW_STATIC, KW_FIELD, KW_LET, KW_DO, KW_IF,
            KW_ELSE, KW_WHILE, KW_RETURN, KW_TRUE, KW_FALSE, KW_NULL, KW_THIS]

# Tokens for sample output
tokens = ['keyword', 'symbol', 'integerConstant', 'stringConstant', 'identifier']

# Symbols for token type T_SYM
symbols = '{}()[].,;+-*/&|<>=~'

# This lexer recognizes Jack tokens.  Attempts to generate helpful error messages.
# Reads the whole .jack program into memory and uses regular expressions to match lexical tokens.

class Lex(object):
    def __init__(self, file):
        infile = open(file, 'r')
        self._lines = infile.read()
        self._tokens = self._tokenize(self._lines)
        self._cur_token = (T_ERROR, 0)
        self._token_type = T_ERROR   # Current token type
        self._keyword = KW_NONE      # Current keyword
        self._symbol = ''            # Current symbol
        self._identifier = ''        # Current identifier
        self._int_val = 0            # Current int constant value
        self._string_val = ''        # Current string constant value
    
    def __str__(self):
        pass

    def openout(self, file):
        self._outfile = open('output/'+file.replace('.jack', 'T.xml'), 'w')
        self._outfile.write('<tokens>')

    def closeout(self):
        self._outfile.write('</tokens>')
        self._outfile.close()
        
    def has_more_tokens(self):
        return self._tokens != []
        
    def advance(self):
        if self.has_more_tokens():
            self._cur_token = self._tokens.pop(0)
        else:
            self._cur_token = (T_ERROR, 0)
        self._writexml()
        return self._cur_token
        
    def peek(self):
        if self.has_more_tokens():
            return self._tokens[0]
        else:
            return (T_ERROR, 0)

    def _writexml(self):
        tok = self._cur_token
        self._write_start_tag(tokens[tok])
        if   tok == T_KEYWORD:  self._outfile.write(self._keyword)
        elif tok == T_SYM:      self._outfile.write(self._symbol)
        elif tok == T_NUM:      self._outfile.write(self._int_val)
        elif tok == T_STR:      self._outfile.write(self._string_val)
        elif tok == T_ID:       self._outfile.write(self._identifier)
        elif tok == T_ERROR:    self._outfile.write('<<ERROR>>')
        self._write_end_tag(tokens[tok])
        
    def _write_start_tag(self, token):
        self._outfile.write('<'+token+'> ')
    
    def _write_end_tag(self, token):
        self._outfile.write(' </'+token+'>\n')
        
    def token_type(self):
        return self._token_type
        
    def keyword(self):
        return self._keyword
        
    def symbol(self):
        return self._symbol
        
    def identifier(self):
        return self._identifier
        
    def int_val(self):
        return self._int_val
        
    def string_val(self):
        return self._string_val
                
    def _tokenize(self, lines):
        return [self._token(word) for word in self._split(self._remove_comments(lines))]
	
    _comment_re = re.compile(r'//.*\n|/\*.*\*/')
    def _remove_comments(self, line):
        return self._comment_re.sub('', line)

    _keyword_re = '|'.join(keywords)
    _sym_re = '['+re.escape(symbols)+']'
    _num_re = r'\d+'
    _str_re = r'"[^"\n]*"'
    _id_re = r'[\w\-.]+'
    _word = re.compile(_keyword_re+'|'+_sym_re+'|'+_num_re+'|'+_str_re+'|'+_id_re)
    def _split(self, line):
        return self._word.findall(line)

    def _token(self, word):
        if   self._is_keyword(word):    return (T_KEYWORD, word)
        elif self._is_sym(word):        return (T_SYM, word)
        elif self._is_num(word):        return (T_NUM, word)
        elif self._is_str(word):        return (T_STR, word)
        elif self._is_id(word):         return (T_ID, word)
        else:                           return (T_ERROR, word)

    def _is_keyword(self, word):
        return self._is_match(self._keyword_re, word)
        
    def _is_sym(self, word):
        return self._is_match(self._sym_re, word)
        
    def _is_num(self, word):
        return self._is_match(self._num_re, word)
        
    def _is_str(self, word):
        return self._is_match(self._id_str, word)
        
    def _is_id(self, word):
        return self._is_match(self._id_re, word)
        
    def _is_match(self, re_str, word):
        return re.match(re_str, word) != None