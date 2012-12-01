#!/usr/local/bin/python3

import re

class Lex(object):
    lines = 0
    tokens = []
    
    def __init__(self, file_name):
        file = open(file_name, 'r')
        self.lines = file.read()
        self.tokenize(self.lines.split('\n'))
    
    def __str__(self):
        pass
        
    NUM     = 1     # number e.g. '123'
    ID      = 2     # symbol e.g. 'LOOP'
    OP      = 3     # = ; ( ) @ - + ! & |
    EOF     = 4     # end of file
    ERROR   = 5     # error in file
    
    def cur_token(self):
        return self.tokens[0]
        
    def next_token(self):
        self.tokens.pop()
        
    def tokenize(self, lines):
        for l in lines:
            print( "tokenizing line: ", l )
            self.tokens += [self.tokenize_line(l)]
            
    def tokenize_line(self,line):
        line = self.remove_extra_white_space(line)
        line_tokens = []
        while len(line):
            if line[0].isdigit():
                (line, token) =  self.get_num(line, self.NUM)
            elif self.is_id_start(line[0]):
                (line, token) = self.get_id(line, self.ID)
            elif self.is_op(line[0]):
                (line, token) = self.get_op(line, self.OP)
            elif len(line) >= 2 and line[0]==line[1]=='/':
                break
            else:
                line_tokens += (self.ERROR,0)
                break
            print( "Found token ", token )
            line_tokens += token
        return line_tokens

    spaces = re.compile(r'\s')    
    def remove_extra_white_space(self, line):
        return line.strip(self.spaces.sub(' ', line))
    
    id_start_chars = r'\w_.$:'
    id_start = re.compile(id_start_chars)
    def is_id_start(self, c):
        return self.id_start.match(c)

    def is_op(self, c):
        return '=;()@-+!&|'.find(c) != -1
        
    digits = re.compile(r'\d+')        
    def get_num(self, line, token_type):
        return self.get_match(self.digits, line)
        
    id = re.compile('('+id_start_chars+')('+id_start_chars+r'\d)*')
    def get_id(self, line, token_type):
        return self.get_match(self.id, line, token_type)
                
    def get_match(self, re, line, token_type):
        match = re.match(line)
        return (line[match.end(0):], (token_type, match.group(0)))
        
    def get_op(self, line, token_type):
        return (line[1:], (token_type, line[0]))