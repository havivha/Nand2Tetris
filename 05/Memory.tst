// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/05/Memory.tst

load Memory.hdl,
output-file Memory.out,
compare-to Memory.cmp,
output-list in%D1.6.1 load%B2.1.2 address%D2.5.2 out%D1.6.1;

echo "Before running this script, select the 'Screen' option from the 'View' menu";

set in 0,
set load 0,
set address 0,
tick,
output;
tock,
output;

set load 1,
tick,
output;
tock,
output;

set in 4444,
set load 0,
tick,
output;
tock,
output;

set load 1,
set address 4444,
tick,
output;
tock,
output;

set load 0,
set address 0,
tick,
output;
tock,
output;

set in 13131,
set address 13131,
tick,
output;
tock,
output;

set load 1,
tick,
output;
tock,
output;

set load 0,
tick,
output;
tock,
output;

set address 4444,
eval,
output;

set in 16383,
tick,
output;
tock,
output;

set load 1,
set address 16383,
tick,
output;
tock,
output;

set load 0,
tick,
output;
tock,
output;

set address 13131,
eval,
output;

set address 16383,
eval,
output;

set address 24576,
echo "Click the Keyboard icon and hold down the 'K' key (uppercase) until you see the next message (it should appear shortly after that) ...",
// It's important to keep holding the key down since if the system is busy,
// the memory will zero itself before being outputted.

while out <> 75 {
    eval,
}

clear-echo,
output;

set load 1,
set in -1,
set address 20431,
tick,
tock,
output,

set address 20559,
tick,
tock,
output,

set load 0,
set address 24576,
echo "Make sure that you see two horizontal lines in the middle of the screen. Hold down 'Y' (uppercase) until you see the next message ...",
// It's important to keep holding the key down since if the system is busy,
// the memory will zero itself before being outputted.

while out <> 89 {
    eval,
}

clear-echo,
output;
