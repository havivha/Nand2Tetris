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
        lextok, lexval = self.lex.next_token()
        if tok != lextok or ((tok == T_KEYWORD or tok == T_SYM) and val != lexval):
            raise ParserError(self._require_failed_msg(tok, val))
        else:
            return lexval
            
    def _require_failed_msg(self, tok, val):
        if val == None: val = tok
        return 'Expected '+val
    
    def _is_class(self):
        return self.lex.peek() == (T_KEYWORD, KW_CLASS)
        
    def compile_class(self):
        class_name = self._require(T_ID)
        self._require(T_SYM, '{')
        while self._is_class_var_dec():
            self.compile_class_var_dec()
        while self._is_subroutine():
            self.compile_subroutine()
        
    def _is_class_var_dec(self):
        tok, kwd = self.lex.peek()
        return tok == T_KEYWORD and (kwd == KW_STATIC or kwd == KW_FIELD)
        
    def compile_class_var_dec(self):
        pass
     
    def _is_subroutine(self):
        tok, kwd = self.lex.peek()
        return tok == T_KEYWORD and (kwd == KW_CONSTRUCTOR or kwd == KW_FUNCTION or kwd == KW_METHOD)
        
    def compile_subroutine(self):
        pass

    def _is_parameter_list(self):
        return self.lex.peek() == (T_SYM, '(')
                
    def compile_parameter_list(self):
        pass
        
    def _is_var_dec(self):
        return self.lex.peek() == (T_KEYWORD, KW_VAR)
        
    def compile_var_dec(self):
        pass
        
    def compile_statements(self):
        pass
    
    def _is_do(self):
        return self.lex.peek() == (T_KEYWORD, KW_DO)
        
    def compile_do(self):
        pass
        
    def _is_let(self):
        return self.lex.peek() == (T_KEYWORD, KW_LET)
        
    def compile_let(self):
        pass
        
    def _is_while(self):
        return self.lex.peek() == (T_KEYWORD, KW_WHILE)
        
    def compile_while(self):
        pass
        
    def _is_return(self):
        return self.lex.peek() == (T_KEYWORD, KW_RETURN)
        
    def compile_return(self):
        pass
        
    def _is_if(self):
        return self.lex.peek() == (T_KEYWORD, KW_IF)
        
    def compile_if(self):
        pass
        
    def compile_expression(self):
        pass
        
    def _is_term(self):
        pass
        
    def compile_term(self):
        pass
        
    def compile_expression_list(self):
        pass