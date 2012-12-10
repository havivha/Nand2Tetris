#!/usr/local/bin/python3

import sys, os, os.path, glob
import Parser

class JackAnalyzer(object):
    def __init__(self):
        pass

    def analyze_all(self, infiles, outfile):
        if infiles != []:
            for infile in infiles:
                self._analyze(infile)

    def _analyze(self, infile):
        parser = Parser.Parser(infile)
        while parser.has_more_commands():
            parser.advance()
            self._gen_code(parser)
    
    def _gen_code(self, parser)
        pass
    
def main():
    if len(sys.argv) != 2:
        print( "Usage: JackAnalyzer [file.jack|dir]" )
    else:
        infiles, outfile = get_files( sys.argv[1] )
        analyzer = JackAnalyzer()
        analyzer.analyze_all(infiles, outfile)

def get_files( file_or_dir ):
    if file_or_dir.endswith('.jack'):
        return [file_or_dir], file_or_dir.replace('.jack', '.xml')
    else:
        return glob.glob(file_or_dir+'/*.jack'), file_or_dir+'/'+file_or_dir+'.xml'

main()