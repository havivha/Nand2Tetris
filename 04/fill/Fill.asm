// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

    @status
    M=-1        // status=0xFFFF
    D=0         // Argument - what to set screen bits to
    @SETSCREEN
    0;JMP

(LOOP)
    @KBD
    D=M         // D = current keyboard character
    @SETSCREEN
    D;JEQ       // If no key, set screen to zeroes (white)
    D=-1        // If key pressed, set screen to all 1 bits (black)
    
(SETSCREEN)     // Set D=new status before jumping here
    @ARG
    M=D         // Save new status arg
    @status     // FFFF=black, 0=white - status of entire screen
    D=D-M       // D=newstatus-status
    @LOOP
    D;JEQ        // Do nothing if new status == old status
    
    @ARG
    D=M
    @status
    M=D         // status = ARG
    
    @SCREEN
    D=A         // D=Screen address
    @8192
    D=D+A       // D=Byte just past last screen address
    @i
    M=D         // i=SCREEN address
    
(SETLOOP)    
    @i
    D=M-1
    M=D         // i=i-1
    @LOOP
    D;JLT       // if i<0 goto LOOP
    
    @status
    D=M         // D=status
    @i
    A=M         // Indirect
    M=D         // M[current screen address]=status
    @SETLOOP
    0;JMP