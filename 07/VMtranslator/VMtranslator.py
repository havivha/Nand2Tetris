#!/usr/local/bin/python3

import sys, os, os.path, glob
import Parser, CodeWriter
from VMCommands import *

class VMTranslator(object):
    def __init__(self):
        pass
        
    def translate_all(self, infiles):
        code_writer = CodeWriter.CodeWriter(self._outfile(infiles[0]))
        for infile in infiles:
            self._translate(infile, code_writer)
        code_writer.close_file()
        
    def _translate(self, infile, code_writer):
        parser = Parser.Parser(infile)
        code_writer.set_file_name(os.path.basename(infile))
        while parser.has_more_commands():
            parser.advance()
            self._gen_code(parser, code_writer)
            
    def _gen_code(self, parser, code_writer):
        cmd = parser.command_type()
        if cmd == C_ARITHMETIC:
            code_writer.write_arithmetic(parser.arg1())
        elif cmd == C_PUSH or cmd == C_POP:
            code_writer.write_push_pop(cmd, parser.arg1(), parser.arg2())
    
    def _outfile(self, infile):
        if infile.endswith( '.vm' ):
            return infile.replace( '.vm', '.asm' )
        else:
            return infile + '.asm'

def main():
    if len(sys.argv) != 2:
        print( "Usage: VMtranslator [file.vm|dir]" )
    else:
        infiles = get_input_files( sys.argv[1] )
        trans = VMTranslator()
        trans.translate_all(infiles)

def get_input_files( file_or_dir ):
    if file_or_dir.endswith('.vm'):
        return [file_or_dir]
    else:
        return glob.glob(file_or_dir+'/*.vm')

main()