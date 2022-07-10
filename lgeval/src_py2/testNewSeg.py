################################################################
# testNewSeg.py
#
# Test program for new segmentation for label graphs.
#
# Authors: R. Zanibbi, H. Mouchere
#	June-August 2012
# Copyright (c) 2012-2014, Richard Zanibbi and Harold Mouchere
################################################################
from bg import *
from bestBG import *


def main():
	nodeLabels = {}
	nodeLabels['n1'] = { '2' : 1.0, '5' : False }
	nodeLabels['n2'] = { '+' : 1.0 }
	nodeLabels['n3'] = { '+' : 1.0 }
	nodeLabels['n4'] = { '2' : 1.0 }

	edgeLabels = {}
	edgeLabels[('n1','n2')] = { 'R' : 1.0, 'S' : 1.0 }
	edgeLabels[('n1','n3')] = { 'R' : 1.0 }
	edgeLabels[('n1','n4')] = { 'R' : 1.0 }
	edgeLabels[('n2','n3')] = { '*' : 1.0 }
	edgeLabels[('n2','n4')] = { 'R' : 1.0 }
	edgeLabels[('n3','n2')] = { '*' : 1.0 }
	edgeLabels[('n3','n4')] = { 'R' : 1.0 }
	#edgeLabels[('nAnon1','nAnon2')] = { 'Anon' : 'b'}

	bg = Bg(nodeLabels,edgeLabels)
	print(bg)
	print(bg.csv())
	
	(psM, spM, rootSegs, segEdges) = bg.segmentGraph()
	print('Primitives to Segments')
	print(psM)
	print('Segments to Primitives')
	print(spM)
	print('Root objects/segments')
	print(rootSegs)
	print('Edges between objects/segments')
	print(segEdges)

	bg = Bg('crohmeTest.bg')
	(psM, spM, rootSegs, segEdges) = bg.segmentGraph()
	print('Primitives to Segments')
	print(psM)
	print('Segments to Primitives')
	print(spM)
	print('Root objects/segments')
	print(rootSegs)
	print('Edges between objects/segments')
	print(segEdges)


main()
