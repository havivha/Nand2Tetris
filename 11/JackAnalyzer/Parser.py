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
        self.openout(file)
        self.compile_class()
        self.closeout()
        
    # VMWriter support    
    def openout(self, path):
        outdir = os.path.join(os.path.dirname(path), 'output')
        file = os.path.join(outdir, os.path.basename(path))
        try:
            os.mkdir(outdir)
        except OSError as e:
            pass
        self.vm.openout(file)
    
    def closeout(self):
        self.vm.closeout()

    def vm_function_name(self):
        return self._cur_class+'.'+self._cur_subroutine
        
    def vm_push_variable(self, name):
        (type, kind, index) = self.symbols.lookup(name)
        self.vm.write_push(segments[kind], index)
        
    def vm_pop_variable(self, name):
        (type, kind, index) = self.symbols.lookup(name)
        self.vm.write_pop(segments[kind], index)     

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
        return self.lex.advance()

    def _is_token(self, tok, val=None):
        lextok, lexval = self.lex.peek()
        return val == None and lextok == tok or (lextok, lexval) == (tok, val)
    
    def _is_keyword(self, *keywords):
        lextok, lexval = self.lex.peek()
        return lextok == T_KEYWORD and lexval in keywords
        
    def _is_sym(self, symbols):
        lextok, lexval = self.lex.peek()
        return lextok == T_SYM and lexval in symbols
        
    # Parser and compile Jack code    
    # class: 'class' className '{' classVarDec* subroutineDec* '}'    
    def compile_class(self):
        self._require(T_KEYWORD, KW_CLASS)
        self.compile_class_name()
        self._require(T_SYM, '{')
        while self._is_class_var_dec():
            self.compile_class_var_dec()
        while self._is_subroutine():
            self.compile_subroutine()
        self._require(T_SYM, '}')

    # className: identifier
    def compile_class_name(self):
        self._cur_class = self.compile_var_name()   # Class names don't have to go into the symbol table
        
    # Variable declarations
    def _is_class_var_dec(self):
        return self._is_keyword(KW_STATIC, KW_FIELD)
            
    # classVarDec: {'static'|'field'} type varName (',' varName)* ';'
    def compile_class_var_dec(self):
        tok, kwd = self._advance()      # static | field
        self._compile_dec(kwd_to_kind[kwd])
        
    # type varName (',' varName)* ';'
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

    # 'void' | type
    def compile_void_or_type(self):
        if self._is_keyword(KW_VOID):
            return self._advance()[1]
        else:
            return self.compile_type()

    # type: 'int' | 'char' | 'boolean' | className           
    def compile_type(self):
        if self._is_type(): 
            return self._advance()[1]
        else:               
            raise ParserError(self._require_failed_msg(*self.lex.peek()))
        
    def _is_var_name(self):
        return self._is_token(T_ID)
        
    # varName: identifier
    def compile_var_name(self):
        return self._require(T_ID)
        
    # Subroutine declarations
    def _is_subroutine(self):
        return self._is_keyword(KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD)
        
    # subroutineDec: ('constructor'|'function'|'method') ('void'|type) 
    #                subroutineName '(' parameterList ')' subroutineBody
    def compile_subroutine(self):
        tok, kwd = self._advance()
        type = self.compile_void_or_type()
        self.compile_subroutine_name()
        self.symbols.start_subroutine()
        if kwd == KW_METHOD:
            self.symbols.define('this', self._cur_class, SK_ARG)
        self._require(T_SYM, '(')
        self.compile_parameter_list()
        self._require(T_SYM, ')')
        self.compile_subroutine_body(kwd)
                
    # subroutineName: identifier
    def compile_subroutine_name(self):
        self._cur_subroutine = self.compile_var_name()  # subroutine names don't have to go in the symbol table
        
    # parameterList: (parameter (',' parameter)*)?
    def compile_parameter_list(self):
        if self._is_type():
            self.compile_parameter()
            while self._is_sym(','):
                self._advance()
                self.compile_parameter()
            
    # parameter: type varName  
    def compile_parameter(self):
        if self._is_type():
            type = self.compile_type()
            name = self.compile_var_name()
            self.symbols.define(name, type, SK_ARG)
            
    # subroutineBody: '{' varDec* statements '}'
    def compile_subroutine_body(self, kwd):
        self._require(T_SYM, '{')
        while self._is_var_dec():
            self.compile_var_dec()
        self.write_func_decl(kwd)
        self.compile_statements()
        self._require(T_SYM, '}')

    def write_func_decl(self, kwd):
        self.vm.write_function(self.vm_function_name(), self.symbols.var_count(SK_VAR))
        self.load_this_ptr(kwd)
        
    def load_this_ptr(self, kwd):
        if kwd == KW_METHOD:
            self.vm.push_arg(0)
            self.vm.pop_this_ptr()      # set up 'this' pointer to point to new object
        elif kwd == KW_CONSTRUCTOR:
            self.vm.push_const(self.symbols.var_count(SK_FIELD))    # object size
            self.vm.write_call('Memory.alloc', 1)
            self.vm.pop_this_ptr()      # set up 'this' pointer to point to new object
        
    def _is_var_dec(self):
        return self._is_keyword(KW_VAR)
        
    # varDec: 'var' type varName (',' varName)* ';'
    def compile_var_dec(self):
        self._require(T_KEYWORD, KW_VAR)
        return self._compile_dec(SK_VAR)
        
    # Statements
    # statement: statement*
    def compile_statements(self):
        while self._is_statement():
            self._compile_statement()
    
    def _is_statement(self):
        return self._is_let() or self._is_if() or self._is_while() or self._is_do() or self._is_return()
        
    # statement: letStatement | ifStatement | whileStatement | doStatement | returnStatement
    def _compile_statement(self):
        if   self._is_let():    self.compile_let()
        elif self._is_if():     self.compile_if()
        elif self._is_while():  self.compile_while()
        elif self._is_do():     self.compile_do()
        elif self._is_return(): self.compile_return()
        
    def _is_let(self):
        return self._is_keyword(KW_LET)
        
    # letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    def compile_let(self):
        self._require(T_KEYWORD, KW_LET)
        name = self.compile_var_name()
        subscript = self._is_sym('[')
        if subscript:
            self.compile_base_plus_index(name) # calculate base+index
        self._require(T_SYM, '=')
        self.compile_expression()           # calculate expression to assign
        self._require(T_SYM, ';')
        if subscript:
            self.pop_array_element()        # *(base+index) = expr
        else:
            self.vm_pop_variable(name)      # pop value directly into variable

    # ('[' expression ']')?
    def compile_base_plus_index(self, name):
        self.vm_push_variable(name)         # push array ptr onto stack
        self._advance()
        self.compile_expression()           # push index onto stack
        self._require(T_SYM, ']')
        self.vm.write_vm_cmd('add')         # base+index - leave on the stack for later

    def pop_array_element(self):
        self.vm.pop_temp(TEMP_ARRAY)        # Pop expr value to temp register
        self.vm.pop_that_ptr()              # Pop base+index into 'that' register
        self.vm.push_temp(TEMP_ARRAY)       # Push expr back onto stack
        self.vm.pop_that()                  # Pop value into *(base+index)

    def _is_if(self):
        return self._is_keyword(KW_IF)
        
    # ifStatement: 'if' '(' expression ')' '{' statements '}'
    #              ('else' '{' statements '}')?
    def compile_if(self):
        self._require(T_KEYWORD, KW_IF)
        end_label = self.new_label()
        self._compile_cond_expression_statements(end_label) # VM code for condition and if statements
        if self._is_keyword(KW_ELSE):
            self._advance()
            self._require(T_SYM, '{')
            self.compile_statements()   # VM code for else statements
            self._require(T_SYM, "}")
        self.vm.write_label(end_label)  # label end_label

    def _is_while(self):
        return self._is_keyword(KW_WHILE)
        
    # whileStatement: 'while' '(' expression ')' '{' statements '}'
    def compile_while(self):
        self._require(T_KEYWORD, KW_WHILE)
        top_label = self.new_label()
        self.vm.write_label(top_label)                      # label top_label
        self._compile_cond_expression_statements(top_label) # VM code for condition and while statements

    # '(' expression ')' '{' statements '}'
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

    label_num = 0
    def new_label(self):
        self.label_num += 1
        return 'label'+str(self.label_num)
        
    def _is_do(self):
        return self._is_keyword(KW_DO)

    # do_statement: 'do' subroutineCall ';'
    def compile_do(self):
        self._require(T_KEYWORD, KW_DO)
        name = self._require(T_ID)
        self.compile_subroutine_call(name)  # VM code for subroutine call
        self.vm.pop_temp(TEMP_RETURN)       # Pop return value and discard
        self._require(T_SYM, ';')
        
    def _is_return(self):
        return self._is_keyword(KW_RETURN)
        
    # returnStatement: 'return' expression? ';'
    def compile_return(self):
        self._require(T_KEYWORD, KW_RETURN)
        if not self._is_sym(';'):
            self.compile_expression()   # VM code for return expression if any
        else:
            self.vm.push_const(0)       # push 0 if not returning a value
        self._require(T_SYM, ';')
        self.vm.write_return()          # return
        
    # Expressions
    # expression: term (op term)*
    def compile_expression(self):
        self.compile_term()
        # Doesn't handle normal order of operations - just left to right for now
        while self._is_op():
            op = self._advance()
            self.compile_term()
            self.vm.write_vm_cmd(vm_cmds[op[1]])  # op
        
    def _is_term(self):
        return self._is_const() or self._is_var_name() or self._is_sym('(') or self._is_unary_op()
        
    # term: integerConstant | stringConstant | keywordConstant | varName
    #     | varName '[' expression ']' | subroutineCall | '(' expression ')'
    #     | unaryOp term
    def compile_term(self):
        if self._is_const():
            self.compile_const()
        elif self._is_sym('('):
            self._advance()
            self.compile_expression()               # VM code to evaluate expression
            self._require(T_SYM, ')')
        elif self._is_unary_op():
            tok, op = self._advance()
            self.compile_term()
            self.vm.write_vm_cmd(vm_unary_cmds[op]) # op
        elif self._is_var_name():
            tok, name = self._advance()
            if self._is_sym('['):
                self.compile_array_subscript(name)  # VM code for array subscript
            elif self._is_sym('(.'):
                self.compile_subroutine_call(name)  # VM code for subroutine call
            else:
                self.vm_push_variable(name)         # push variable on stack

    def _is_const(self):
        return self._is_token(T_NUM) or self._is_token(T_STR) or self._is_keyword_constant()
        
    def _is_keyword_constant(self):
        return self._is_keyword(KW_TRUE, KW_FALSE, KW_NULL, KW_THIS)

    def _is_op(self):
        return self._is_sym('+-*/&|<>=')    

    def _is_unary_op(self):
        return self._is_sym('-~')
        
    # integerConstant | stringConstant | keywordConstant
    def compile_const(self):
        tok, val = self._advance()
        if tok == T_NUM:
            self.vm.push_const(val)                 # push constant val
        elif tok == T_STR:
            self.write_string_const_init(val)       # initialize string & push str addr
        elif tok == T_KEYWORD:
            self.compile_kwd_const(val)             # push TRUE, FALSE, NULL etc.
    
    def write_string_const_init(self, val):
        self.vm.push_const(len(val))
        self.vm.write_call('String.new', 1)         # String.new(len(str))
        for c in val:
            self.vm.push_const(ord(c))
            self.vm.write_call('String.appendChar', 2)  # String.appendChar(nextchar)
            
    # keywordConstant: 'true' | 'false' | 'null' | 'this'
    def compile_kwd_const(self, kwd):
        if kwd == KW_THIS:
            self.vm.push_this_ptr()
        elif kwd == KW_TRUE:
            self.vm.push_const(1)
            self.vm.write_vm_cmd('neg')
        else:   # KW_FALSE or KW_NULL
            self.vm.push_const(0)
    
    # '[' expression ']'
    def compile_array_subscript(self, name):
        self.vm_push_variable(name)     # push array ptr onto stack
        self._require(T_SYM, '[')
        self.compile_expression()       # push index onto stack
        self._require(T_SYM, ']')
        self.vm.write_vm_cmd('add')     # base+index
        self.vm.pop_that_ptr()          # pop into 'that' ptr
        self.vm.push_that()             # push *(base+index) onto stack

    # subroutineCall: subroutineName '(' expressionList ')'
    #               | (className | varName) '.' subroutineName '(' expressionList ')'
    def compile_subroutine_call(self, name):
        (type, kind, index) = self.symbols.lookup(name)
        if self._is_sym('.'):
            num_args, name = self.compile_dotted_subroutine_call(name, type)
        else:
            num_args = 1
            self.vm.push_this_ptr()
            name = self._cur_class+'.'+name
        self._require(T_SYM, '(')
        num_args += self.compile_expr_list() # VM code to push arguments
        self._require(T_SYM, ')')
        self.vm.write_call(name, num_args)  # call name num_args

    def compile_dotted_subroutine_call(self, name, type):
        num_args = 0
        obj_name = name
        self._advance()
        name = self.compile_var_name()
        if self._is_builtin_type(type):     # e.g. int.func(123) not allowed
            ParserError('Cannot use "." operator on builtin type')
        elif type == None:                  # Calling using class name
            name = obj_name+'.'+name
        else:                               # Calling using object variable name
            num_args = 1
            self.vm_push_variable(obj_name) # push object ptr onto stack   
            name = self.symbols.type_of(obj_name)+'.'+name
        return num_args, name
                    
    def _is_builtin_type(self, type):
        return type in [KW_INT, KW_CHAR, KW_BOOLEAN, KW_VOID]
        
    # expressionList: (expression (',' expression)*)?
    def compile_expr_list(self):
        num_args = 0
        if self._is_term():
            self.compile_expression()
            num_args = 1
            while self._is_sym(','):
                self._advance()
                self.compile_expression()
                num_args += 1
        return num_args