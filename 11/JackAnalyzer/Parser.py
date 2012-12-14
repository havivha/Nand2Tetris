#!/usr/local/bin/python3

import os, os.path
from xml.sax.saxutils import escape
from Lex import *
from SymbolTable import *
from VMWriter import *
from JackConstant import *

# Parses Jack source code and generates VM code for it.

class ParserError(Exception):
    def __init__(self, message):
        self.message = message
    
class Parser(object):
    def __init__(self, file):
        self.lex = Lex(file)
        self.symbols = SymbolTable()
        self.vm = VMWriter()
        self.label_num = 0
        self.openout(file)
        self.compile_class()
        self.closeout()
        #print(self.symbols)
        
    # Parsing context
    def cur_class(self):
        return self._cur_class
        
    def cur_subroutine(self):
        return self._cur_subroutine
    
    # VMWriter support
    
    # TO FIX:
    vm_cmds = {'+':'add', '-':'sub', '*':'call Math.multiply 2', '/':'call Math.divide 2',
               '<':'lt', '>':'gt', '=':'eq', '&':'and', '|':'or'}
    vm_unary_cmds = {'-':'neg', '~':'not'}
    segments = {SK_STATIC:'static', SK_FIELD:'this', SK_ARG:'argument', SK_VAR:'local', None:'ERROR'}
    
    def vm_function_name(self):
        return self.cur_class()+'.'+self.cur_subroutine()
        
    def vm_push_variable(self, name):
        (type, kind, index) = self.symbols.lookup(name)
        #print('push_variable: name=',name,'type=',type,'kind=',kind,'index=',index)
        if kind == None:
            raise ParserError('bad push')
        self.vm.write_push(self.segments[kind], index)
        
    def vm_pop_variable(self, name):
        (type, kind, index) = self.symbols.lookup(name)
        self.vm.write_pop(self.segments[kind], index)        
        
    # Routines to advance the token
    def _require(self, tok, val=None):
        lextok, lexval = self._advance()
        if tok != lextok or tok in (T_KEYWORD, T_SYM) and val != lexval:
            raise ParserError(self._require_failed_msg(tok, val))
        else:
            return lexval
            
    def _require_failed_msg(self, tok, val):
        if val == None: val = tokens[tok]
        return 'Expected '+val
    
    def _advance(self):
        tok, val = self.lex.advance()
        self._write_terminal(tok, val)
        return tok, val

    def _is_token(self, tok, val=None):
        lextok, lexval = self.lex.peek()
        return val == None and lextok == tok or (lextok, lexval) == (tok, val)
    
    def _is_keyword(self, *keywords):
        lextok, lexval = self.lex.peek()
        return lextok == T_KEYWORD and lexval in keywords
        
    def _is_sym(self, symbols):
        lextok, lexval = self.lex.peek()
        return lextok == T_SYM and lexval in symbols
        
    # Write XML output        
    def openout(self, path):
        outdir = os.path.join(os.path.dirname(path), 'output')
        file = os.path.join(outdir, os.path.basename(path))
        try:
            os.mkdir(outdir)
        except OSError as e:
            pass
        self._outfile = open(file.replace('.jack', '.xml'), 'w')
        self.lex.openout(file)
        self.vm.openout(file)
    
    def closeout(self):
        self.vm.closeout()
        self.lex.closeout()
        self._outfile.close()

    def _write_terminal(self, tok, val):
        self._outfile.write('<'+tokens[tok]+'> '+escape(val)+' </'+tokens[tok]+'>\n')
        
    _parsed_rules = []
    def _start_non_terminal(self, rule):
        self._outfile.write('<'+rule+'>\n')
        self._parsed_rules.append(rule)
        
    def _end_non_terminal(self):
        rule = self._parsed_rules.pop()
        self._outfile.write('</'+rule+'>\n')

    # Parser and compile Jack code        
    def compile_class(self):
        self._start_non_terminal('class')
        self._require(T_KEYWORD, KW_CLASS)
        self._cur_class = self._require(T_ID)    # Class names don't have to go into the symbol table
        self._require(T_SYM, '{')
        while self._is_class_var_dec():
            self.compile_class_var_dec()
        while self._is_subroutine():
            self.compile_subroutine()
        self._require(T_SYM, '}')
        self._end_non_terminal()

    # Variable declarations
    def _is_class_var_dec(self):
        return self._is_keyword(KW_STATIC, KW_FIELD)
            
    def compile_class_var_dec(self):
        self._start_non_terminal('classVarDec')
        tok, kwd = self._advance()      # static | field
        if kwd == KW_STATIC: kind = SK_STATIC
        else:                kind = SK_FIELD
        self._compile_dec(kind)
        self._end_non_terminal()
        
    def _compile_dec(self, kind):
        type = self.compile_type();
        name = self.compile_var_name()
        self.symbols.define(name, type, kind)
        while self._is_sym(','):
            self._advance()
            name = self.compile_var_name()
            self.symbols.define(name, type, kind)
        self._require(T_SYM, ';')
    
    def _is_type(self):
        return self._is_token(T_ID) or self._is_keyword(KW_INT, KW_CHAR, KW_BOOLEAN)

    def compile_void_or_type(self):
        if self._is_keyword(KW_VOID):
            return self._advance()[1]
        else:
            return self.compile_type()
            
    def compile_type(self):
        if self._is_type(): 
            return self._advance()[1]
        else:               
            raise ParserError(self._require_failed_msg(*self.lex.peek()))
        
    def _is_var_name(self):
        return self._is_token(T_ID)
        
    def compile_var_name(self):
        return self._require(T_ID)
        
    # Subroutine declarations
    def _is_subroutine(self):
        return self._is_keyword(KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD)
        
    def compile_subroutine(self):
        self._start_non_terminal('subroutineDec')
        tok, kwd = self._advance()
        type = self.compile_void_or_type()
        self._cur_subroutine = self.compile_var_name()
        self.symbols.start_subroutine()
        if kwd == KW_METHOD:
            self.symbols.define('this', self.cur_class(), SK_ARG)
        self._require(T_SYM, '(')
        self.compile_parameter_list()
        self._require(T_SYM, ')')
        self.compile_subroutine_body(kwd)
        self._end_non_terminal()
                
    def compile_parameter_list(self):
        self._start_non_terminal('parameterList')
        if self._is_type():
            self.compile_parameter()
            while self._is_sym(','):
                self._advance()
                self.compile_parameter()
        self._end_non_terminal()
              
    def compile_parameter(self):
        if self._is_type():
            type = self.compile_type()
            name = self.compile_var_name()
            self.symbols.define(name, type, SK_ARG)
            
    def compile_subroutine_body(self, kwd):
        self._start_non_terminal('subroutineBody')
        self._require(T_SYM, '{')
        while self._is_var_dec():
            self.compile_var_dec()
        self.write_func_decl(kwd)
        self.compile_statements()
        self._require(T_SYM, '}')
        self._end_non_terminal()

    def write_func_decl(self, kwd):
        self.vm.write_function(self.vm_function_name(), self.symbols.var_count(SK_VAR))
        if kwd == KW_METHOD:
            self.vm.write_push('argument', 0)   # Set up 'this' to point at current object
            self.vm.write_pop('pointer', 0)
        elif kwd == KW_CONSTRUCTOR:
            self.vm.write_push('constant', self.symbols.var_count(SK_FIELD))
            self.vm.write_call('Memory.alloc', 1)   # call Memory.alloc(object_size)
            self.vm.write_pop('pointer', 0)         # set up 'this' pointer to point to new object
        
    def _is_var_dec(self):
        return self._is_keyword(KW_VAR)
        
    def compile_var_dec(self):
        self._start_non_terminal('varDec')
        self._require(T_KEYWORD, KW_VAR)
        num_vars = self._compile_dec(SK_VAR)
        self._end_non_terminal()
        return num_vars
        
    # Statements
    def compile_statements(self):
        self._start_non_terminal('statements')
        while self._is_statement():
            self._compile_statement()
        self._end_non_terminal()
    
    def _is_statement(self):
        return self._is_do() or self._is_let() or self._is_if() or self._is_while() or self._is_return()
        
    def _compile_statement(self):
        if   self._is_do():     self.compile_do()
        elif self._is_let():    self.compile_let()
        elif self._is_if():     self.compile_if()
        elif self._is_while():  self.compile_while()
        elif self._is_return(): self.compile_return()
        
    def _is_do(self):
        return self._is_keyword(KW_DO)
        
    def compile_do(self):
        self._start_non_terminal('doStatement')
        self._require(T_KEYWORD, KW_DO)
        name = self._require(T_ID)
        self.compile_subroutine_call(name)  # VM code for subroutine call
        self.vm.write_pop('temp', 0)        # Pop return value and discard
        self._require(T_SYM, ';')
        self._end_non_terminal()
        
    def _is_let(self):
        return self._is_keyword(KW_LET)
        
    def compile_let(self):
        self._start_non_terminal('letStatement')
        self._require(T_KEYWORD, KW_LET)
        name = self.compile_var_name()
        subscript = self._is_sym('[')
        if subscript:
            self.vm_push_variable(name)     # push array ptr onto stack
            self._advance()
            self.compile_expression()       # push index onto stack
            self._require(T_SYM, ']')
            self.vm.write_vm_cmd('add')     # base+index
            self.vm.write_pop('temp', 1)    # save base+index into temp register
        self._require(T_SYM, '=')
        self.compile_expression()
        self._require(T_SYM, ';')
        if subscript:
            self.vm.write_push('temp', 1)   # push base+index
            self.vm.write_pop('pointer', 1) # pop base+index into 'that' register
            self.vm.write_pop('that', 0)    # pop value into *(base+index)
        else:
            self.vm_pop_variable(name)      # pop value directly into variable
        self._end_non_terminal()

    def _is_while(self):
        return self._is_keyword(KW_WHILE)
        
    def compile_while(self):
        self._start_non_terminal('whileStatement')
        self._require(T_KEYWORD, KW_WHILE)
        top_label = self.new_label()
        self.vm.write_label(top_label)          # label top_label
        self._compile_cond_expression_statements(top_label) # VM code for condition and while statements
        self._end_non_terminal()
        
    def new_label(self):
        self.label_num += 1
        return 'label'+str(self.label_num)
        
    def _is_return(self):
        return self._is_keyword(KW_RETURN)
        
    def compile_return(self):
        self._start_non_terminal('returnStatement')
        self._require(T_KEYWORD, KW_RETURN)
        if not self._is_sym(';'):
            self.compile_expression()   # VM code for return expression if any
        else:
            self.vm.write_push('constant', 0) # push 0 if not returning a value
        self._require(T_SYM, ';')
        self.vm.write_return()          # return
        self._end_non_terminal()
        
    def _is_if(self):
        return self._is_keyword(KW_IF)
        
    def compile_if(self):
        self._start_non_terminal('ifStatement')
        self._require(T_KEYWORD, KW_IF)
        end_label = self.new_label()
        self._compile_cond_expression_statements(end_label) # VM code for condition and if statements
        if self._is_keyword(KW_ELSE):
            self._advance()
            self._require(T_SYM, '{')
            self.compile_statements()   # VM code for else statements
            self._require(T_SYM, "}")
        self.vm.write_label(end_label)  # label end_label
        self._end_non_terminal()

    def _compile_cond_expression_statements(self, label):
        self._require(T_SYM, '(')
        self.compile_expression()
        self._require(T_SYM, ')')
        self.vm.write_vm_cmd('not')     # ~(cond)
        notif_label = self.new_label()
        self.vm.write_if(notif_label)   # if-goto notif_label
        self._require(T_SYM, '{')
        self.compile_statements()       # VM code for if statements
        self._require(T_SYM, '}')
        self.vm.write_goto(label)       # goto label
        self.vm.write_label(notif_label)# label notif_label

    # Expressions
    def compile_expression(self):
        self._start_non_terminal('expression')
        self.compile_term()
        # Doesn't handle normal order of operations - just left to right for now
        while self._is_op():
            op = self._advance()
            self.compile_term()
            self.vm.write_vm_cmd(self.vm_cmds[op[1]])  # op
        self._end_non_terminal()
        
    def _is_term(self):
        return self._is_const() or self._is_var_name() or self._is_sym('(') or self._is_unary_op()
        
    def _is_const(self):
        return self._is_token(T_NUM) or self._is_token(T_STR) or self._is_keyword_constant()
        
    def _is_keyword_constant(self):
        return self._is_keyword(KW_TRUE, KW_FALSE, KW_NULL, KW_THIS)

    def compile_term(self):
        self._start_non_terminal('term')
        if self._is_const():
            self.push_const()
        elif self._is_sym('('):
            self._advance()
            self.compile_expression()               # VM code to evaluate expression
            self._require(T_SYM, ')')
        elif self._is_unary_op():
            tok, op = self._advance()
            self.compile_term()
            self.vm.write_vm_cmd(self.vm_unary_cmds[op])    # op
        elif self._is_var_name():
            tok, name = self._advance()
            if self._is_sym('['):
                self._compile_array_subscript(name) # VM code for array subscript
            elif self._is_sym('(.'):
                self.compile_subroutine_call(name)  # VM code for subroutine call
            else:
                self.vm_push_variable(name)             # push variable on stack
        self._end_non_terminal()

    def push_const(self):
        tok, val = self._advance()
        if tok == T_NUM:
            self.vm.write_push('constant', val)     # push constant val
        elif tok == T_STR:
            self.vm.write_push('constant', len(val))
            self.vm.write_call('String.new', 1)     # String.new(len(str))
            for c in val:
                self.vm.write_push('constant', ord(c))
                self.vm.write_call('String.appendChar', 2)  # String.appendChar(nextchar)
        elif tok == T_KEYWORD:
            self.push_kwd_const(val)
            
    def push_kwd_const(self, kwd):
        if kwd == KW_THIS:
            self.vm.write_push('pointer', 0)
        elif kwd == KW_TRUE:
            self.vm.write_push('constant', 1)
            self.vm.write_vm_cmd('neg')
        else:   # KW_FALSE or KW_NULL
            self.vm.write_push('constant', 0)
    
    def _compile_array_subscript(self, name):
        self.vm_push_variable(name)     # push array ptr onto stack
        self._require(T_SYM, '[')
        self.compile_expression()       # push index onto stack
        self._require(T_SYM, ']')
        self.vm.write_vm_cmd('add')     # base+index
        self.vm.write_pop('pointer', 1) # pop into 'that' ptr
        self.vm.write_push('that', 0)   # push *(base+index) onto stack

    def compile_subroutine_call(self, name):
        (type, kind, index) = self.symbols.lookup(name)
        num_args = 0
        if self._is_sym('.'):
            object_name = name
            self._advance()
            name = self._require(T_ID)
            if self._is_builtin_type(type):     # e.g. int.func(123) not allowed
                ParserError('Cannot use "." operator on builtin type')
            elif type == None:                  # Calling using class name
                name = object_name+'.'+name
            else:                               # Calling using object variable name
                self.vm_push_variable(object_name)     # push object ptr onto stack   
                num_args = 1
                name = self.symbols.type_of(object_name)+'.'+name
        else:
            self.vm.write_push('pointer', 0)    # push this
            num_args = 1
            name = self.cur_class()+'.'+name
        self._require(T_SYM, '(')
        num_args += self.compile_expr_list() # VM code to push arguments
        self._require(T_SYM, ')')
        self.vm.write_call(name, num_args)  # call name num_args
    
    def _is_builtin_type(self, type):
        return type in [KW_INT, KW_CHAR, KW_BOOLEAN, KW_VOID]
        
    def _is_unary_op(self):
        return self._is_sym('-~')
        
    def _is_op(self):
        return self._is_sym('+-*/&|<>=')
    
    def compile_expr_list(self):
        num_args = 0
        self._start_non_terminal('expressionList')
        if self._is_term():
            self.compile_expression()
            num_args = 1
            while self._is_sym(','):
                self._advance()
                self.compile_expression()
                num_args += 1
        self._end_non_terminal()
        return num_args