#!/usr/local/bin/python3

import os, os.path

# VM code generator

class VMWriter(object):
    def __init__(self, file):
        self.openout(file)
    
    def openout(self, file):
        self._outfile = open(file.replace('.jack', '.vm'), 'w')
    
    def closeout(self):
        self._outfile.close()

    def write_push(self, segment, index):
        self.write_vm_cmd('push', segment, index)
        
    def write_pop(self, segment, index):
        self.write_vm_cmd('pop', segment, index)
        
    def write_arithmetic(self, op):
        self.write_vm_cmd(op)
        
    def write_label(self, label):
        self.write_vm_cmd('label', label)
        
    def write_goto(self, label):
        self.write_vm_cmd('goto', label)
        
    def write_if(self, label):
        self.write_vm_cmd('if-goto', label)
        
    def write_call(self, name, num_args):
        self.write_vm_cmd('call', name, num_args)
        
    def write_function(self, name, num_locals):
        self.write_vm_cmd('function', name, num_locals)
        
    def write_return(self):
        self.write_vm_cmd('return')
        
    def write_vm_cmd(self, cmd, arg1='', arg2=''):
        self._outfile.write(cmd+' '+str(arg1)+' '+str(arg2)+'\n')