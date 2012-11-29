// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/mult/Mult.tst

load Mult.hack,
output-file Mult.out,
compare-to Mult.cmp,
output-list RAM[0]%D2.6.2 RAM[1]%D2.6.2 RAM[2]%D2.6.2;

set RAM[0] 0,
set RAM[1] 0;
repeat 20 {
  ticktock;
}
output;

set PC 0,
set RAM[0] 1,
set RAM[1] 0;
repeat 50 {
  ticktock;
}
output;

set PC 0,
set RAM[0] 0,
set RAM[1] 2;
repeat 80 {
  ticktock;
}
output;

set PC 0,
set RAM[0] 3,
set RAM[1] 1;
repeat 120 {
  ticktock;
}
output;

set PC 0,
set RAM[0] 2,
set RAM[1] 4;
repeat 150 {
  ticktock;
}
output;

set PC 0,
set RAM[0] 6,
set RAM[1] 7;
repeat 210 {
  ticktock;
}
output;
