#!/usr/local/bin/python3

import Lex

# Parses Jack input.  Tries to give useful error messages.

class ParserError(Exception):
    pass
    
class Parser(object):
    def __init__(self, file):
        self.lex = Lex.Lex(file)
        self._openout(file)
        self.lex.openout(file)
        self._require(T_KEYWORD, KW_CLASS)
        self.compile_class()
        self._closeout()
        
    def __str__(self):
        pass
        
    def _openout(self, file):
        try:
            os.mkdir('output')
        except IOError as e:
            pass
        self._outfile = open('output/'+file.replace('jack', 'xml'), 'w')
        self._outfile.write('<tokens>')
    
    def _closeout(self):
        self.lex.closeout()
        self._outfile.close()

    def _require(self, tok, val=None):
        lextok, lexval = self.lex.advance()
        if tok != lextok or ((tok == T_KEYWORD or tok == T_SYM) and val != lexval):
            raise ParserError(self._require_failed_msg(tok, val))
        else:
            return lexval
            
    def _require_failed_msg(self, tok, val):
        if val == None: val = tok
        return 'Expected '+val
    
    def _is_token(self, tok, val=None):
        lextok, lexval = self.lex.peek()
        if val == None:
            return lextok == tok
        else:
            return (lextok, lexval) == (tok, val)
        
    def compile_class(self):
        self._require(T_KEYWORD, KW_CLASS)
        class_name = self._require(T_ID)
        self._require(T_SYM, '{')
        while self._is_class_var_dec():
            self.compile_class_var_dec()
        while self._is_subroutine():
            self.compile_subroutine()
        
    def _is_class_var_dec(self):
        return self._is_token(T_KEYWORD, KW_STATIC) or self._is_token(T_KEYWORD, KW_FIELD)
        
    def compile_class_var_dec(self):
        tok, kwd = self.lex.advance()
        self._compile_dec()
        
    def _compile_dec(self):
        self._compile_type()
        self._compile_var_name()
        while self._is_token(T_SYM, ','):
            self._require(T_SYM, ',')
            self._compile_var_name()
        self._require(T_SYM, ';')
    
    def _is_type(self):
        tok, val = self.lex.peek()
        return tok == T_KEYWORD and (val == KW_INT or val == KW_CHAR or val == KW_BOOLEAN) or tok == T_ID

    def _compile_type(self):
        if self._is_type():
            return self.lex.advance()
        else:
            raise ParserError(self._require_failed_msg(*self.lex.peek()))
        
    def _compile_void_or_type(self):
        if self._is_token(T_KEYWORD, KW_VOID):
            return self.lex.advance()
        else:
            self._compile_type()
            
    def _is_var_name(self):
        return self._is_token(T_ID)
        
    def _compile_var_name(self):
        self._require(T_ID)
        
    def _is_subroutine(self):
        tok, kwd = self.lex.peek()
        return tok == T_KEYWORD and (kwd == KW_CONSTRUCTOR or kwd == KW_FUNCTION or kwd == KW_METHOD)
        
    def compile_subroutine(self):
        tok, kwd = self.lex.advance()
        self._compile_void_or_type()
        self._compile_var_name()
        self._require(T_SYM, '(')
        self.compile_parameter_list()
        self._require(T_SYM, ')')
        self._compile_subroutine_body()
                
    def compile_parameter_list(self):
        while self._is_type():
            self._compile_type()
            self._compile_var_name()
              
    def _compile_subroutine_body(self):
        self._require(T_SYM, '{')
        while self._is_var_dec():
            self.compile_var_dec()
        self.compile_statements()
        self._require(T_SYM, '}')
        
    def _is_var_dec(self):
        return self._is_token(T_KEYWORD, KW_VAR)
        
    def compile_var_dec(self):
        self._require(T_KEYWORD, KW_VAR)
        self._compile_dec()
        
    def compile_statements(self):
        while self._is_statement():
            self._compile_statement()
    
    def _is_statement(self):
        return self._is_do() or self._is_let() or self._is_if() or self._is_while() or self._is_return()
        
    def _is_do(self):
        return self._is_token(T_KEYWORD, KW_DO)
        
    def compile_do(self):
        self._require(T_KEYWORD, KW_DO)
        self._compile_subroutine_call()
        self._require(T_SYM, ';')
        
    def _is_let(self):
        return self._is_token(T_KEYWORD, KW_LET)
        
    def compile_let(self):
        self._require(T_KEYWORD, KW_LET)
        self._compile_var_name()
        if self._is_token(T_SYM, '['):
            self._require(T_SYM, '[')
            self.compile_expression()
            self._require(T_SYM, ']')
        self._require(T_SYM, '=')
        self.compile_expression()
        self._require(T_SYM, ';')
        
    def _is_while(self):
        return self._is_token(T_KEYWORD, KW_WHILE)
        
    def compile_while(self):
        self._require(T_KEYWORD, T_WHILE)
        self._compile_cond_expression_statements()
        
    def _is_return(self):
        return self._is_token(T_KEYWORD, KW_RETURN)
        
    def compile_return(self):
        self._require(T_KEYWORD, KW_RETURN)
        if not self._is_token(T_SYM, ';'):
            self.compile_expression()
        self._require(T_SYM, ';')
        
    def _is_if(self):
        return self._is_token(T_KEYWORD, KW_IF)
        
    def compile_if(self):
        self._require(T_KEYWORD, KW_IF)
        self._compile_cond_expression_statement()
        if self._is_token(T_KEYWORD, KW_ELSE):
            self._require(T_KEYWORD, KW_ELSE)
            self.compile_statements()

    def _compile_cond_expression_statements():
        self._require(T_SYM, '(')
        self.compile_expression()
        self._require(T_SYM, ')')
        self._require(T_SYM, '{')
        self.compile_statements()
        self._require(T_SYM, '}')

    def compile_expression(self):
        self.compile_term()
        while self._is_op():
            self._compile_op()
            self.compile_term()
        
    def _is_term(self):
        return self._is_token(T_NUM) or self._is_token(T_STR) or self._is_keyword_constant()    \
            or self._is_var_name() or self._is_token(T_SYM, '(') or self._is_unary_op()
        
    def compile_term(self):
        if self._is_token(T_NUM) or self._is_token(T_STR) or self._is_keyword_constant():
            self.lex.advance()
        elif self._is_var_name():
            pass
        elif self._is_token(T_SYM, '('):
            self.compile_expression()
            self._require(')')
        elif self._is_unary_op():
            self.lex.advance()
            self.compile_term()
        elif self._is_var_name():
            self._require(T_ID)
            if self._is_token(T_SYM, '['):
                self._compile_array_subscript()
            elif self._is_token(T_SYM, '(') or self._is_token(T_SYM, '.'):
                self._compile_subroutine_call()

    def _compile_array_subscript(self):
        self._require(T_SYM, '[')
        self.compile_expression()
        self._require(T_SYM, ']')

    def _compile_subroutine_call(self):
        if self._is_token(T_SYM, '.'):
            self._require(T_SYM, '.')
            self._require(T_ID)
        self._require(T_SYM, '(')
        self.compile_expression_list()
        self._require(T_SYM, ')')
        
    def _is_keyword_constant(self):
        tok, kwd = self.lex.peek()
        return tok == T_KEYWORD and kwd in [KW_TRUE, KW_FALSE, KW_NULL, KW_THIS]

    def _is_unary_op(self):
        return self._is_token(T_SYM, '-') or self._is_token(T_SYM, '~')
        
    def _is_op(self):
        tok, sym = self.lex.peek()
        return tok == T_SYM and sym in '+-*/&|<>='
        
    def compile_expression_list(self):
        self.compile_expression()
        while self._is_token(T_SYM, ','):
            self._require(T_SYM, ',')
            self.compile_expression()