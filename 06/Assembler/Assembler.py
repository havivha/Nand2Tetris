#!/usr/local/bin/python3
        
import Parser, Code, SymbolTable, sys

# Usage: Assembler.py file.asm
# Reads file.asm and outputs file.hack - the assembled machine code as a text file.

class Assembler(object):
    def __init__(self):
        self.symbols = SymbolTable.SymbolTable()
        self.symbol_addr = 16
    
    # First pass: determine memory locations of label definitions: (LABEL)
    def pass0(self, file):
        parser = Parser.Parser(file)
        cur_address = 0
        while parser.has_more_commands():
            parser.advance()
            cmd = parser.command_type()
            if cmd == parser.A_COMMAND or cmd == parser.C_COMMAND:
                cur_address += 1
            elif cmd == parser.L_COMMAND:
                self.symbols.add_entry( parser.symbol(), cur_address )
    
    # Second pass: generate code and write result to output file.
    def pass1(self, infile, outfile):
        parser = Parser.Parser(infile)
        outf = open( outfile, 'w' )
        code = Code.Code()
        while parser.has_more_commands():
            parser.advance()
            cmd = parser.command_type()
            if cmd == parser.A_COMMAND:
                outf.write( code.gen_a(self._get_address(parser.symbol())) + '\n' )
            elif cmd == parser.C_COMMAND:
                outf.write( code.gen_c(parser.dest(), parser.comp(), parser.jmp()) + '\n' )
            elif cmd == parser.L_COMMAND:
                pass
        outf.close()
    
    # Lookup an address - may be symbolic, or already numeric
    def _get_address(self, symbol):
        if symbol.isdigit():
            return symbol
        else:
            if not self.symbols.contains(symbol):
                self.symbols.add_entry(symbol, self.symbol_addr)
                self.symbol_addr += 1
            return self.symbols.get_address(symbol)
    
    # Drive the assembly process
    def assemble(self, file):
        self.pass0( file )
        self.pass1( file, self._outfile(file) )
        
    def _outfile(self, infile):
        if infile.endswith( '.asm' ):
            return infile.replace( '.asm', '.hack' )
        else:
            return infile + '.hack'    

main():
    if len(sys.argv) != 2:
        print( "Usage: Assembler file.asm" )
    else:
        infile = sys.argv[1]
        
    asm = Assembler()
    asm.assemble( infile )
    
main()