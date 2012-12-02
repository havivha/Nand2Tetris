#!/usr/local/bin/python3
        
import Parser, Code, SymbolTable

#import Lex
#lex = Lex.Lex('Add.asm')

parser = Parser.Parser('Add.asm')
code = Code.Code()
while parser.has_more_commands():
	parser.advance()
	print( 'type=', parser.command_type(), 'sym=', parser.symbol(), 
			'dest=', parser.dest(), 'comp=', parser.comp(), 'jmp=', parser.jmp() )
	if parser.command_type() == parser.A_COMMAND:
		print( code.gen_a(parser.symbol()) )
	elif parser.command_type() == parser.C_COMMAND:
		print( code.gen_c(parser.dest(), parser.comp(), parser.jmp()) )
	elif parser.command_type() == parser.L_COMMAND:
		print( 'Label', parser.symbol() )