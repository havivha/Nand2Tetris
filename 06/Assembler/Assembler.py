#!/usr/local/bin/python3
        
import Parser, Code, SymbolTable
import Lex

lex = Lex.Lex('Add.asm')
print(lex.lines)
print(lex.tokens)