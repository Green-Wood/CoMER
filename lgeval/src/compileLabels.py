################################################################
# compileLabels.py
#
# Reads in a list of .lg files, and returns a file contining 
# node and edge labels used in the files.
#
# Author: H. Mouchere, June 2012
# Copyright (c) 2012-2014, Richard Zanibbi and Harold Mouchere
################################################################
import sys
import csv
from lg import *
import os
import time

def main( fileName ):
	try:
		fileReader = csv.reader(open(fileName))
	except:
		sys.stderr.write('  !! IO Error (cannot open): ' + fileName)
		sys.exit(1)

	nodeLabels = set()
	edgeLabels = set()
	for row in fileReader:
		# Skip blank lines.
		if len(row) == 0:
			continue

		nextFile = row[0].strip()
		
		lg = Lg( nextFile )

		# Collect all labels from node and edge label sets.
		for node in list(lg.nlabels):
			for label in list(lg.nlabels[ node ]):
				nodeLabels.add( label )

		for edge in list(lg.elabels):
			for label in list(lg.elabels[ edge ]):
				edgeLabels.add( label )

	outString = "NODE LABELS:"
	for label in sorted( list(nodeLabels )):
		outString += "\n" + label
	
	outString += "\n\nEDGE LABELS:"
	for label in sorted( list(edgeLabels)):
		outString += "\n" + label
	
	print( outString )

if len( sys.argv ) < 2:
	print("Usage: [[python]] compileLabels.py lgFileList")
	sys.exit(0)

main( sys.argv[1] )
