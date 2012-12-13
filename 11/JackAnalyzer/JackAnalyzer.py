#!/usr/local/bin/python3

import sys, os, os.path, glob
from Parser import *

class JackAnalyzer(object):
    def __init__(self):
        pass

    def analyze(self, infiles):
        for infile in infiles:
            Parser(infile)

def main():
    if len(sys.argv) != 2:
        print( "Usage: JackAnalyzer [file.jack|dir]" )
    else:
        infiles = get_files( sys.argv[1] )
        analyzer = JackAnalyzer()
        analyzer.analyze(infiles)

def get_files( file_or_dir ):
    if file_or_dir.endswith('.jack'):
        return [file_or_dir]
    else:
        return glob.glob(file_or_dir+'/*.jack')

main()