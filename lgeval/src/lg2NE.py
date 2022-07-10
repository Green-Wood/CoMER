################################################################
# lg2NE.py
#
# Convert a given .lg file to Node-Edge format.
#
# Author: R. Zanibbi Oct. 2014
# Copyright (c) 2012-2014, Richard Zanibbi and Harold Mouchere
################################################################
import sys
from lg import *

def main(fileName):
	inputFile = Lg(fileName)
	print(inputFile.csv())

fileName = sys.argv[1]
main(fileName)
