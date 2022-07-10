###########################################################################
#
# lgfilter.py
#	- Warning: this assumes that edges and nodes have a single label.
#
# Author: R. Zanibbi, March 2013
# Copyright (c) 2012-2014 Richard Zanibbi and Harold Mouchere
###########################################################################

import sys
from lg import *

def main():
	if (len(sys.argv) < 2):
		print("Usage: python lgfilter.py <infile> [outfile]")
		print("")
		print("Removes non-tree edges in the graph (assuming a tree is present!)")
		print("and produces an .lg file with objects and relationships defined")
		print("at the bottom of the file.")
		print("")
		print("Warning: this assumes that each node and edge has a single label.")
		return
	
	fileName = sys.argv[1]
	lg = Lg(fileName)

	(segmentPrimitiveMap, primitiveSegmentMap, noparentSegments, segmentEdges) = \
			lg.segmentGraph()
	(rootNodes, treeEdges, otherEdges) = lg.separateTreeEdges()

	# Remove all edges that aren't from the set of treeEdges between segments.
	removedNotes = ''
	for (seg1, seg2) in otherEdges:
		seg1prims = segmentPrimitiveMap[ seg1 ][0]
		seg2prims = segmentPrimitiveMap[ seg2 ][0]

		for prim1 in seg1prims:
			for prim2 in seg2prims:
				removedNotes += '#   Removed (' + str(prim1) + ',' + str(prim2) \
						+ ') ' + str(lg.elabels[(prim1,prim2)]) + '\n'
				del lg.elabels[(prim1,prim2)]
	
	topString = '# Created by lgfilter.py from ' + fileName + '\n' 
	topString += removedNotes
	topString += lg.csv() +'\n'

	# Create a list of segments and relationships.
	objectList = '# [ OBJECTS ]\n#   Format: [Label] prim1 ... primN\n'
	for segment in list(segmentPrimitiveMap):
		segString =''
		segLabel = 'ERROR'
		for stroke in segmentPrimitiveMap[segment][0]:
			segString += str(stroke) + ' '
			segLabel = str(list(lg.nlabels[stroke])[0])
		objectList += '# ' + segLabel + ' ' + segString + '\n'

	objectList += '# [ RELS ]\n#   Format:  [Label] parentPrim1 ... parentPrimN :: childPrim1 ... childPrimM\n'

	for (seg1,seg2) in treeEdges:
		seg1prims = segmentPrimitiveMap[ seg1 ][0]
		seg2prims = segmentPrimitiveMap[ seg2 ][0]

		list1 = ''
		p1 = ''
		for prim1 in seg1prims:
			list1 += prim1 + ' '
			p1 = prim1

		list2 = ''
		for prim2 in seg2prims:
			list2 += prim2 + ' '
			p2 = prim2

		objectList += '# ' + str(list(lg.elabels[(p1,p2)])[0]) + ' ' + list1 + ':: ' + list2 + '\n'

	# Generate output.
	if (len(sys.argv) > 2):
		# To file if output file name provided.
		outFileHandle = open( sys.argv[2],'w')
		outFileHandle.write(topString + objectList)
		outFileHandle.close()
	else:
		# Otherwise to standard output.
		print(topString + objectList)


main()

