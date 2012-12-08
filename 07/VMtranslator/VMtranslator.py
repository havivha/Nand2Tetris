#!/usr/local/bin/python3

import Parser, CodeWriter, sys
from VMCommands import *

class VMTranslator(object):
    def __init__(self):
        pass
        
    def translate(self, infile):
        parser = Parser.Parser(infile)
        code_writer = CodeWriter.CodeWriter(self._outfile(infile))
        
        while parser.has_more_commands():
            parser.advance()
            cmd = parser.command_type()
            if cmd == C_ARITHMETIC:
                code_writer.write_arithmetic(parser.arg1())
            elif cmd == C_PUSH or cmd == C_POP:
                code_writer.write_push_pop(cmd, parser.arg1(), parser.arg2())

        code_writer.close_file()
    
    def _outfile(self, infile):
        if infile.endswith( '.vm' ):
            return infile.replace( '.vm', '.asm' )
        else:
            return infile + '.asm'

infile = sys.argv[1]
trans = VMTranslator()
trans.translate(infile)