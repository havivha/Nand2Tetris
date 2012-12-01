#!/usr/local/bin/python3

import Lex

class Parser(object):
    lex = 0
    
    def __init__(self, file):
        lex = Lex(file)
        lex.nextToken()
    
    def __str__(self):
        pass
        
    def hasMoreCommands(self):
        return False
    
    def advance(self):
        pass
    
    A_COMMAND=0
    C_COMMAND=1
    L_COMMAND=2
    
    def commandType(self):
        pass
        
    def symbol(self):
        pass
    
    def dest(self):
        pass
    
    def comp(self):
        pass
        
    def jmp(self):
        pass