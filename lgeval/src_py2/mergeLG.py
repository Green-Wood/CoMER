################################################################
# mergeLG.py
#
# Program that reads in two or more .lg (CSV) files, merge
# them and print the new LG graph on standard output.
#
# Author: H. Mouchere, July 2014
# Copyright (c) 2012-2014 Richard Zanibbi and Harold Mouchere
################################################################
import sys
import csv
from lg import *


def main():
	if len(sys.argv) < 3:
		print("Usage: [[python]] mergeLG.py <file1.lg> <file2.lg> ... ")
		print("reads in two or more .lg (CSV) files, merges")
		print("them and prints the new LG graph on standard output.")
		sys.exit(0)
	
	n1 = Lg(sys.argv[1])
	print '#'+sys.argv[1]
	for f in sys.argv[2:]:
		print '#'+f
		n2 = Lg(f)
		n1.addWeightedLabelValues(n2)
	print n1.csv()
		
main()
		

