#!/usr/local/bin/python3

import sys, os, os.path, glob
import Parser, CodeWriter
from VMConstant import *

class VMTranslator(object):
    def __init__(self):
        pass
        
    def translate_all(self, infiles, outfile):
        if infiles != []:
            code_writer = CodeWriter.CodeWriter(outfile)
            code_writer.write_init()
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
        elif cmd == C_LABEL:
            code_writer.write_label(parser.arg1())
        elif cmd == C_GOTO:
            code_writer.write_goto(parser.arg1())
        elif cmd == C_IF:
            code_writer.write_if(parser.arg1())
        elif cmd == C_FUNCTION:
            code_writer.write_function(parser.arg1(), parser.arg2())
        elif cmd == C_RETURN:
            code_writer.write_return()
        elif cmd == C_CALL:
            code_writer.write_call(parser.arg1(), parser.arg2())
    
def main():
    if len(sys.argv) != 2:
        print( "Usage: VMtranslator [file.vm|dir]" )
    else:
        infiles, outfile = get_files( sys.argv[1] )
        trans = VMTranslator()
        trans.translate_all(infiles, outfile)

def get_files( file_or_dir ):
    if file_or_dir.endswith('.vm'):
        return [file_or_dir], file_or_dir.replace('.vm', '.asm')
    else:
        return glob.glob(file_or_dir+'/*.vm'), file_or_dir+'/'+file_or_dir+'.asm'

main()