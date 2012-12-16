#!/usr/local/bin/python3

import os, os.path

# VM code generator

class VMWriter(object):
    def __init__(self,):
        pass
        
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
        
    # Helpers to make things easier
    def push_const(self, val):
        self.write_push('constant', val)
        
    def push_arg(self, arg_num):
        self.write_push('argument', arg_num)
        
    def push_this_ptr(self):
        self.write_push('pointer', 0)
        
    def pop_this_ptr(self):
        self.write_pop('pointer', 0)
        
    def pop_that_ptr(self):
        self.write_pop('pointer', 1)
        
    def push_that(self):
        self.write_push('that', 0)
        
    def pop_that(self):
        self.write_pop('that', 0)
        
    def push_temp(self, temp_num):
        self.write_push('temp', temp_num)
        
    def pop_temp(self, temp_num):
        self.write_pop('temp', temp_num)