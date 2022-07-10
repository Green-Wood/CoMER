##################################################################################

3 converters provided for CROHME 2019 Task 2. Offline Handwritten Formula Recognition 
April 2019 - Mahshad

##################################################################################
[Description]

For task2 in which primitive level information (connected components) are not provided, we evaluate the systems based on the correct symbols and correct relation between symbols (symbolic evaluation). 

For Symbol level evaluation, instead of primitives to identify the symbols, we use the absolut path in trees for each symbol/node. This should be written in the place of primitives in the last column of the label graph format. We call this new format symLG:
	
	LG FORMAT: O, Object ID, Label, Weight, [ Primitive ID List ]
     symLG FORMAT: O, Object ID, Label, Weight, [ absolute path ]


Example of a symbol level LG:

# IUD, filename
# Objects(3):
O, z_1, z, 1.0, OSub
O, F_1, F, 1.0, O
O, x_1, x, 1.0, ORight

# Relations from SRT:
R, F_1, z_1, Sub, 1.0
R, F_1, x_1, Right, 1.0

###################################################################################
[Files]

In this package, we provide three converters:

1) tex2symlg: Converts the LaTex outputs to symbol level LG format.
 -----------------------------------------	   
Usage: tex2symlg <texdir> <lgdir>
 -----------------------------------------

2) mml2symlg: Conver MathML outputs to symbol level LG format.
 -----------------------------------------
Usage: mml2symlg <mmldir> <outdir>
 -----------------------------------------

3) lg2symlg: Convert LG files with primitives to symbol level LG format. Make sure that the input LGs are in OR format (participants can use "lg2OR" from lgeval library to convert the input lg formats into OR).
 -----------------------------------------
Usage: lg2symlg <lgdir> <outdir>
 -----------------------------------------
	  
