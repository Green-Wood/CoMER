################################################################
# lg2txt.py
#
# Translate a label graph to a text file of different formats.
#
# NOTE: this program assumes that horizontal adjacency 
#   is indicated using 'HOR' or 'R' edge labels, superscripts
#   and subscripts by 'SUP' and 'SUB.'
#
# Author: R. Zanibbi, June 2012
# Copyright (c) 2012-2014 Richard Zanibbi and Harold Mouchere
################################################################

import sys
import csv
from lg import *

def readMapFile(fileName):
	"""Read in symbol and structure mappings from a file."""
	try:
		fileReader = csv.reader(open(fileName))
	except:
		sys.stderr.write('  !! IO Error (cannot open): ' + fileName + '\n')
		return

	symbolMap = {}
	structureMap = {}
	readingSymbols = True
	for row in fileReader:
		# Skip blank lines and comments.
		if len(row) == 0:
			continue
		elif row[0].strip()[0] == '#':
			continue
		elif row[0].strip() == 'SYMBOLS':
			readingSymbols = True
		elif row[0].strip() == 'STRUCTURE':
			readingSymbols = False
		else:
			pattern = []
			replacement = []
			
			i = 0
			while not row[i].strip() == '->':
				pattern += [ row[i] ]
				i += 1
			i += 1
			while i < len(row):
				replacement += [ row[i] ]
				i += 1

			if len(pattern) > 1:
				relations = sorted( pattern[1:len(pattern)] )
				ptuple = tuple( [ pattern[0] ] + relations )
			else:
				ptuple = ( pattern[0] )

			if len(replacement) > 1:
				rtuple = tuple(replacement)
			else:
				rtuple = ( replacement[0] )

			if readingSymbols:
				symbolMap[ptuple] = rtuple
			else:
				structureMap[ptuple] = rtuple

	return (symbolMap, structureMap)


def translateStructure( lg, label, nodeRelationPairs, structureMap,\
		segPrimMap, edgeMap, symbolMap, segId, nodeString):
	"""Generate a string for a given structure."""
	strString = ""
	byValue = lambda pair: pair[1]  
	sortedNodeRelationPairs = sorted(nodeRelationPairs, key=byValue)
	queryList = [ label ]

	primListString = ""
	for primitiveId in sorted(list(segPrimMap[ segId ][0])):
		primListString += primitiveId + ':'
		
	for (childId, relation) in sortedNodeRelationPairs:
		queryList += [ relation ]

	#print(primListString)
	#print(queryList)

	# Obtain the replacement, provided as an ordered sequence of
	# regions, giving the order in which to map subregions.
	key = tuple(queryList)
	anyKey = tuple(['ANY'] + queryList[1:])

	#print("key: " + str(key))
	#print(structureMap.keys())
	if key in structureMap.keys():
		replacementTuple = structureMap[ key ]
		#print("replacement: " + str(replacementTuple))

		# Find the node that matches each relation in the passed list,
		# and generate the appropriate string.
		for i in range(0,len(replacementTuple)):
			nextRelation = replacementTuple[ i ]

			match = False
			for j in range(0,len(nodeRelationPairs)):
				(childId, relation) = nodeRelationPairs[j]
				if relation == nextRelation:
					strString += translate(lg, childId, segPrimMap,\
							edgeMap, symbolMap, structureMap) 
					match = True
					break
			# RZ, Jan 2013: allow other tags to be inserted (e.g. at end);
			# add primitive ids as identifier for symbols with multiple
			# subregions (e.g. fractions, roots)
			if not match:
				strString += replacementTuple[i].replace('_I_','\"' + \
						primListString + '\"')
	
	# HACK!!! Copying and modifying above conditional branch.
	elif anyKey in structureMap.keys():
		replacementTuple = structureMap[ anyKey ]
		#print("replacement: " + str(replacementTuple))

		# Find the node that matches each relation in the passed list,
		# and generate the appropriate string.
		for i in range(0,len(replacementTuple)):
			nextRelation = replacementTuple[ i ]

			match = False
			for j in range(0,len(nodeRelationPairs)):
				(childId, relation) = nodeRelationPairs[j]
				if relation == nextRelation:
					strString += translate(lg, childId, segPrimMap,\
							edgeMap, symbolMap, structureMap) 
					match = True
					break
				elif nextRelation == 'PARENT':
					strString += nodeString
					match = True
					break

			# RZ, Jan 2013: allow other tags to be inserted (e.g. at end);
			# add primitive ids as identifier for symbols with multiple
			# subregions (e.g. fractions, roots)
			if not match:
				strString += replacementTuple[i].replace('_I_','\"' + \
						primListString + '\"')


	return strString

def translateRelation(lg, (relation, nextChildId), structureMap, \
		segPrimMap, edgeMap, symbolMap, nodeString):
	"""Translate an individual spatial relation."""
	relString = ""
	replacementTuple = ()
	
	if relation in structureMap.keys():
		replacementTuple = structureMap[ relation ]
	
	else:
		sys.stderr.write("  !! Error: Unknown relationship label " + relation + "\n")
		sys.stderr.write("  !!        Using relationship mapping: " + str(structureMap[ 'REL_DEFAULT' ]) + "\n")
		# Use default mapping if label is unknown.
		replacementList = list( structureMap[ 'REL_DEFAULT' ] )
		for i in range(0,len(replacementList)):
			replacementList[i] = replacementList[i].replace('_L_', \
					relation)
		replacementTuple = tuple( replacementList )
	
	for i in range(0,len(replacementTuple)):
		nextEntry = replacementTuple[ i ]
		if nextEntry == "PARENT":
			# Add current symbol at this location
			relString += nodeString
		elif nextEntry == "CHILD":
			relString += translate(lg, nextChildId, segPrimMap, edgeMap, symbolMap, structureMap)
		else:
			relString += replacementTuple[i]
	
	return relString


def translate(lg, segId,  segPrimMap, edgeMap,  symbolMap, structureMap):
	"""Recursively create output for an expression at the object level."""
	byValue = lambda pair: pair[1]  
	byRel = lambda pair: pair[0]

	oneSegPrimitive = list(segPrimMap[ segId ][0])[0]
	labelValuePairs = sorted(lg.nlabels[ oneSegPrimitive ].items(), key=byValue)
	(label, value) = labelValuePairs[0]

	nodeString = label  
	
	# Create label identifying primitives in the object.
	primListString = ""
	for primitiveId in sorted(list(segPrimMap[ segId ][0])):
		primListString += primitiveId + ':'
	
	if label in symbolMap:
		nodeString = symbolMap[ label ].replace('_I_','\"' + \
				primListString + '\"')
	else:
		# Treat all unknowns uniformly.
		nodeString = symbolMap[ 'OBJ_DEFAULT' ].replace('_I_','\"' + \
				primListString + '\"').replace('_L_',label)
		sys.stderr.write("  !! Error: Unknown object label " + label + "\n")

	if segId in edgeMap:
		# This node has children - lookup replacement based on sorted labels
		# for edges to child nodes.
		childSegIds = edgeMap[ segId ]
		nodeRelationPairs = []
		horRelation = []
		noSubSupPairs = []
		subSupPairs = []
		for nextChildId in childSegIds:
			# Obtain the highest-valued label for the edge.
			childPrimitive =list( segPrimMap[ nextChildId ][0])[0]
			edgeLabels = lg.elabels[ (oneSegPrimitive, childPrimitive) ]
			labelValuePairs = sorted(edgeLabels.items(), key=byValue)
			(relation, value) = labelValuePairs[0]

			# DEBUG: remove HOR/R relations, separate SUB/SUP relations.
			# Add missing "Sub" "Sup" labels for CROHME 2013.
			# DEBUG: Separate undefined labels into the 'noSubSupPairs' note
			#   that this binds these undefined relationships before any hor.
			#   adjacency relationship.
			if not (relation == 'HOR' or relation == 'R' or relation == "Right"):
				nodeRelationPairs += [ (nextChildId, relation) ]
				if not (relation == 'SUB' or relation == 'SUP' or \
						relation == 'Sub' or relation == 'Sup' or
						not relation in structureMap.keys() and not relation == 'I' and not relation == 'Inside' ):
					noSubSupPairs += [ (nextChildId, relation) ]
				else:
					subSupPairs += [ (nextChildId, relation) ]
			
			else:
				horRelation += [ (nextChildId, relation) ]


		# CASE 1: all relations other than HOR/R are in a structure.
		strString = translateStructure(lg, label, nodeRelationPairs, structureMap,\
				segPrimMap, edgeMap, symbolMap, segId, nodeString)
		if not strString == "":
			nodeString = strString 
		else:
			# CASE 2: only non-SUP/SUB relations are in a structure.
			strString = translateStructure(lg, label, noSubSupPairs, structureMap,\
					segPrimMap, edgeMap, symbolMap, segId, nodeString)
			if not strString == "":
				nodeString = strString
				for (nextChildId, relation) in sorted(subSupPairs, key=byValue):
					nodeString = translateRelation(lg, (relation, nextChildId),\
							structureMap, segPrimMap, edgeMap, symbolMap, nodeString)

					#nodeString += translateRelation(lg, (relation, nextChildId),\
					#		structureMap, segPrimMap, edgeMap, symbolMap)
			else:
				# DEFAULT: map relations independently.
				for (nextChildId, relation) in sorted(nodeRelationPairs, key=byValue):
					nodeString = translateRelation(lg, (relation, nextChildId),\
							structureMap, segPrimMap, edgeMap, symbolMap, nodeString)

		# Lastly, generate string for adjacent symbols on the baseline.
		# **if there are multiple 'HOR' symbols all will be mapped.
		for (child, relation) in horRelation:
			nodeString = translateRelation(lg, (relation, child),\
					structureMap, segPrimMap, edgeMap, symbolMap, nodeString)

	return nodeString

def main():
	if len(sys.argv) < 2:
		print("Usage: [[python]] lg2txt.py <infile.lg> [mapfile.csv]")
		print("")
		print("   Produces a text file for label graph file")
		print("   <infile.lg>. A symbol and structure map file (mapfile.csv)")
		print("   may be provided to override default (latex) mappings.")
		return

	lg = Lg(sys.argv[1])

	# Hide the unlabeled edges.
	lg.hideUnlabeledEdges()

	(segmentPrimitiveMap, primitiveSegmentMap, noparentSegments, segmentEdges) = \
				lg.segmentGraph()
	(rootNodes, treeEdges, otherEdges) = lg.separateTreeEdges()

	# Default symbol and structure mappings.
	symbolMap = { }
	structureMap = { }

	# A bit dirty; redefining the global maps.
	if len(sys.argv) > 2:
		(symbolMap, structureMap) = readMapFile(sys.argv[2])

	# Create a map from nodes to child nodes, in order to be able to
	# detect structures such as fractions, etc.
	treeEdgeMap = {}
	for (parent, child) in treeEdges:
		if parent in treeEdgeMap:
			treeEdgeMap[ parent ] += [ child ]
		else:
			treeEdgeMap[ parent ] = [ child ]

	# NOTE: currently this will print out more than one expression on 
	# separate lines if a graph has multiple root nodes.

	# Exit if there is no root node, generate a list of TeX expressions if there are
	# multiple root nodes.
	if len(rootNodes) < 1:
		sys.stderr.write("  !! Error: graph contains no root node; cannot generate output.\n")
		sys.exit(1)
	elif len(rootNodes) > 1:
		sys.stderr.write("  !! Graph contains " + str(len(rootNodes)) + " root nodes.\n")

	for root in rootNodes:
		print(translate(lg, root, segmentPrimitiveMap, treeEdgeMap,\
				symbolMap, structureMap))

main()
