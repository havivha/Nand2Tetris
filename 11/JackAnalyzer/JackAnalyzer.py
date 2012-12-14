#!/usr/local/bin/python3

import sys, os, os.path, glob
from Parser import *

def main():
    if len(sys.argv) != 2:
        print( "Usage: JackAnalyzer [file.jack|dir]" )
    else:
        infiles = get_files( sys.argv[1] )
        analyze(infiles)

def get_files( file_or_dir ):
    if file_or_dir.endswith('.jack'):
        return [file_or_dir]
    else:
        return glob.glob(file_or_dir+'/*.jack')

def analyze(infiles):
    for infile in infiles:
        Parser(infile)
            
main()