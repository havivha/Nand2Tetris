#!/usr/local/bin/python3

from JackConstant import *

# A list of symbol tables, one per scope
class SymbolTable(object):
    def __init__(self):
        self.class_symbols = {}
        self.subroutine_symbols = {}
        self.symbols = {SK_STATIC:self.class_symbols, SK_FIELD:self.class_symbols, 
                        SK_ARG:self.subroutine_symbols, SK_VAR:self.subroutine_symbols}
        self.index = {SK_STATIC:0, SK_FIELD:0, SK_ARG:0, SK_VAR:0}
    
    def __str__(self):
        return self.symbol_string('class', self.class_symbols)    \
             + self.symbol_string('subroutine', self.subroutine_symbols)
        
    def symbol_string(self, name, table):
        result = 'symbol table '+name+':\n'
        for n, (t, k, i) in table.items():
            result += 'symbol name:'+n+', type:'+t+', kind:'+k+', index:'+str(i)+'\n'
        return result
            
    def start_subroutine(self):
        self.subroutine_symbols.clear()
        self.index[SK_ARG] = self.index[SK_VAR] = 0
        
    def define(self, name, type, kind):
        self.symbols[kind][name] = (type, kind, self.index[kind])
        self.index[kind] += 1

    def var_count(self, kind):
        return sum(1 for n, (t, k, i) in self.symbols[kind].items() if k == kind)
        
    def type_of(self, name):
        (type, kind, index) = self.lookup(name)
        return type
        
    def kind_of(self, name):
        (type, kind, index) = self.lookup(name)
        return kind
    
    def index_of(self, name):
        (type, kind, index) = self.lookup(name)
        return index
        
    def lookup(self, name):
        if name in self.subroutine_symbols:
            return self.subroutine_symbols[name]
        elif name in self.class_symbols:
            return self.class_symbols[name]
        else:
            return (None, None, None)