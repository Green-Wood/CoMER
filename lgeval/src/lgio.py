################################################################
# lgio.py
#
# Input/Output routines for label graphs.
#
# Author: Richard Zanibbi
# Copyright (c) 2012-2014 Richard Zanibbi and Harold Mouchere
################################################################
import sys
import csv
from lg import *

def writeDiff(ndiffs, sdiffs, ediffs, streamFile):
	"""Write differences for label graphs and (implicit) trees
	to the passed stream."""
	for ndiff in ndiffs:
		streamFile.write('*N,' + ndiff[0] + ',')
		for symbol in ndiff[1]:
			streamFile.write(symbol[0] + ',')
			streamFile.write(str(symbol[1]) + ',')
		streamFile.write(':vs:,')

		for i in range(0,len(ndiff[2])):
			streamFile.write(ndiff[2][i][0] + ',')
			streamFile.write(str(ndiff[2][i][1]))
			if i < len(ndiff[2][i]) - 2:
				streamFile.write(',')
		streamFile.write('\n')

	# Edges
	for ediff in ediffs:
		streamFile.write('*E,' + ediff[0][0] + ',' + ediff[0][1] + ',')
		for symbol in ediff[1]:
			streamFile.write(symbol[0] + ',')
			streamFile.write(str(symbol[1]) + ',')
		streamFile.write(':vs:,')

		for i in range(0,len(ediff[2])):
			streamFile.write(str(ediff[2][i][0]) + ',')
			streamFile.write(str(ediff[2][i][1]))
			if i < len(ediff[2]) - 1:
				streamFile.write(',')
		streamFile.write('\n')

	# Segmentation graph edges. Simply construct all pairs,
	# as disagreeing edges are common.
	for sdiff in list(sdiffs):
		primitiveEndSet = sdiffs[sdiff]
		for end in primitiveEndSet[0]:
			streamFile.write('*S,' + str(sdiff) + ',' + str(end) + '\n')
		for end in primitiveEndSet[1]:
			streamFile.write('*S,' + str(sdiff) + ',' + str(end) + '\n')


def writeCSVTuple(tuple, secondComma, streamFile):
	for i in range(0,len(tuple) - 1):
		streamFile.write(str(tuple[i]))
		streamFile.write(',')
	streamFile.write(str(tuple[len(tuple) - 1]))
	if secondComma:
		streamFile.write(',')

def writeMetrics(metrics, streamFile):
	"""Computes numerical metrics (for node and edge labels, and segmentation
	graph edge disagreements), and writes them to standard output."""
	numMetrics = len(metrics[0])
	for i in range(0,numMetrics - 1):
		writeCSVTuple(metrics[0][i],True, streamFile)
	writeCSVTuple(metrics[0][numMetrics - 1],False, streamFile)
	streamFile.write('\n')

################################################################
# Input
################################################################
def fileListToLgs(fileName):
	"""Given a file containing a list of .lg files, return the
	list of corresponding label graphs."""
	file = open(fileName)
	fileReader = csv.reader(file)

	lgList = []
	for row in fileReader:
		# Skip comments and empty lines.
		if not row == [] and not row[0].strip()[0] == "#":
			lgfile1 = row[0].strip() # remove leading/trailing whitespace
			lg1 = Lg(lgfile1)
			lgList += [ lg1 ]

	file.close()
	return lgList

