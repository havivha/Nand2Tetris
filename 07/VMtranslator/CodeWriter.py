#!/usr/local/bin/python3

from VMCommands import *

# CodeWriter translates VM commands into Hack assembly code

class CodeWriter(object):    
    def __init__(self, outf):
        self._out_file = open(outf, 'w')
        self._vm_file = ''
        self._labelnum = 0

    def __str__(self):
        pass
        
    def set_file_name(self, filename):
        self._vm_file = filename        # VM file currently being processed    
                    
    def close_file(self):
        self._out_file.close()
        
    def write_arithmetic(self, command):
        if   command == 'add':  self._binary('D+A')
        elif command == 'sub':  self._binary('A-D')
        elif command == 'neg':  self._unary('-D')
        elif command == 'eq':   self._compare('JEQ')
        elif command == 'gt':   self._compare('JGT')
        elif command == 'lt':   self._compare('JLT')
        elif command == 'and':  self._binary('D&A')
        elif command == 'or':   self._binary('D|A')
        elif command == 'not':  self._unary('!D')
        
    def write_push_pop(self, command, segment, index):
        if command == C_PUSH:
            if segment == 'constant':
                self._val_to_stack(str(index))
                self._inc_sp()
        elif command == C_POP:
            pass

    # Pop args off stack, perform an operation, and push the result on the stack
    def _unary(self, comp):
        self._dec_sp()                      # --SP
        self._stack_to_dest('D')            # D=*SP
        self._c_command('D', comp)          # D=COMP
        self._comp_to_stack('D')            # *SP=D
        self._inc_sp()                      # ++SP
        
    def _binary(self, comp):
        self._dec_sp()                      # --SP
        self._stack_to_dest('D')            # D=*SP
        self._dec_sp()                      # --SP
        self._stack_to_dest('A')            # A=*SP
        self._c_command('D', comp)          # D=comp
        self._comp_to_stack('D')            # *SP=D
        self._inc_sp()                      # ++SP

    def _compare(self, jump):
        self._dec_sp()                      # --SP
        self._stack_to_dest('D')            # D=*SP
        self._dec_sp()                      # --SP
        self._stack_to_dest('A')            # A=*SP
        self._c_command('D', 'A-D')         # D=A-D
        label_eq = self._jump('D', jump)    # D;jump to label_eq
        self._comp_to_stack('0')            # *SP=0
        label_ne = self._jump('0', 'JMP')   # 0;JMP to label_ne
        self._l_command(label_eq)           # (label_eq)
        self._comp_to_stack('-1')           # *SP=-1
        self._l_command(label_ne)           # (label_ne)
        self._inc_sp()                      # ++SP

    # SP operations
    def _inc_sp(self):
        self._a_command('SP')               # A=&SP
        self._c_command('M', 'M+1')         # SP=SP+1
        
    def _dec_sp(self):
        self._a_command('SP')               # A=&SP
        self._c_command('M', 'M-1')         # SP=SP-1
        
    def _val_to_stack(self, val):
        self._a_command(val)                # A=val
        self._c_command('D', 'A')           # D=A
        self._comp_to_stack('D')            # *SP=D

    def _comp_to_stack(self, comp):
        self._load_sp()
        self._c_command('M', comp)          # *SP=comp
        
    def _stack_to_dest(self, dest):
        self._load_sp()
        self._c_command(dest, 'M')          # dest=*SP
        
    def _load_sp(self):
        self._a_command('SP')               # A=&SP
        self._c_command('A', 'M')           # A=SP
        
    # Jump to a new label and return the label for later definition
    def _jump(self, comp, jump):
        label = self._label()
        self._a_command(label)              # A=label
        self._c_command(None, comp, jump)   # comp;jump
        return label
    
    # Generate a new label    
    def _label(self):
        self._labelnum += 1
        return 'LABEL'+str(self._labelnum)
    
    # Write an assembler @ command   
    def _a_command(self, address):
        self._out_file.write('@'+address+'\n')
        
    # Write an assembler C command
    def _c_command(self, dest, comp, jump=None):
        if dest != None:
            self._out_file.write(dest+'=')
        self._out_file.write(comp)
        if jump != None:
            self._out_file.write(';'+jump)
        self._out_file.write('\n')
        
    # Write an assembler L command
    def _l_command(self, label):
        self._out_file.write('('+label+')\n')