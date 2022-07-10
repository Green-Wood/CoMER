################################################################
# lg2dot.py
#
# Create different .dot files from .lg files.
#
# Author: Richard Zanibbi, June 2012
# Copyright (c) 2012-2014, Richard Zanibbi and Harold Mouchere
################################################################
import sys
from lg import *

# Default separator for label lists.
DELIM=" "

def createLabelList(labelList, delimiter=DELIM):
	"""Convenience - create a delimited list of labels."""
	Labels = sorted(list(set(labelList)))
	outString = ""
	i=0
	for label in Labels:
		if i > 0:
			outString += delimiter
		outString += (str(label)).replace('\\','\\\\')
		i += 1

	# Make sure to use underscore to represent empty label lists.
	if len(Labels) < 1:
		outString = '_'
	return(outString)

def createSegPrimitivesLabel( segmentId, lg, segPrimMap, delimiter=DELIM):
	"""Given a label graph and segment tuple (with nodeIds and
	segment label), return a delimited list for all labels
	associated with nodes in the segment."""
	(primIds, _) = segPrimMap[ segmentId ]

	#  Compile the label set for all primitives.
	primLabelSet = set()
	for idName in primIds:
		if idName in list(lg.nlabels):
			for nextLabel in list(lg.nlabels[ idName ]):
				primLabelSet.add( nextLabel )
		else:
			primLabelSet.add('_')

	return( createLabelList( sorted(list(primLabelSet)), delimiter) )

def createRelPrimitivesLabel( edge, lg, segPrimMap, delimiter=DELIM):
	"""Create label list from set of all primitive labels associated
	with a relationship between objects."""
	(parentPrimIds, _) = segPrimMap[ edge[0] ]
	(childPrimIds, _) = segPrimMap[ edge[1] ]

	edgePrimLabelSet = set()
	for pid in parentPrimIds:
		for cid in childPrimIds:
			if (pid, cid) in list(lg.elabels):
				for label in list(lg.elabels[ (pid, cid) ]):
					edgePrimLabelSet.add(label)
			else:
				edgePrimLabelSet.add('_')
		
	return( createLabelList( sorted(list(edgePrimLabelSet)), delimiter) )

def getFirstElements(list):
	"""Return first element for each tuple in a list."""
	def first(x):
		return(x[0])
	return(map(first,list))

def primitiveNodeString(lg, nodeDiffList):
	dotString = "digraph lg {\n\trankdir=LR; ranksep=1.0;\n\tedge[fontsize=11,weight=1]; node[fontsize=13]; graph[concentrate=true,ordering=out];\n"
	dotString = dotString + "\n\t/*  NODES (PRIMITIVES) */\n\t"
	for primitive in sorted(list(list(lg.nlabels))):
		Rlabel = createLabelList(list(lg.nlabels[primitive]))
		color = 'blue'

		# Find id's with disagreeing node labels.
		Elabel = [] 
		for (id,_,RlabelList) in nodeDiffList:
			if id == primitive:
				Elabel += getFirstElements(RlabelList)
				color = 'red,penwidth=2.0,fontcolor=red' #,peripheries=2'

		Estring = ""
		if len(Elabel) > 0:
			Estring = "\n( " + createLabelList(Elabel) + " )"
		
		dotString = dotString + primitive + " [label=\"" \
				+  Rlabel + Estring + "\\n" + primitive \
				+  "\", color=" + color + "];\n\t"

	return dotString

def bipartiteNodeString(lg, nodeDiffList, lg2=None):
	dotString = "digraph lg {\n\trankdir=LR; ranksep=1.0;\n\tedge[fontsize=11,weight=1]; node[fontsize=13]; graph[ordering=out];\n"
	i = 0
	dotString = dotString + "\n\t/*  NODES (PRIMITIVES) */"
	for primitive in sorted(list(list(lg.nlabels))):
		dotString = dotString + \
				"\n\tsubgraph cluster" + str(i) + "{" \
				+ "\n\t\trank=" + str(i+1) + "; color=white;\n\t\t"
		Llabel = createLabelList(list(lg.nlabels[primitive]))
		Rlabel = Llabel

		if not lg2 == None:
			Rlabel = createLabelList(list(lg2.nlabels[primitive]))
		color = 'blue'
		if not Llabel == Rlabel:
			color = "red,penwidth=2.0,fontsize=14,fontcolor=red"
		dotString = dotString + 'L' + primitive + " [label=\"" \
				+  Llabel + "\\n" + primitive \
				+  "\", color = " + color + "];\n\t\t"
		dotString = dotString + 'R' + primitive + " [label=\"" \
				+  Rlabel + "\\n" + primitive \
				+  "\", color = blue" + "];\n\t\t"
		dotString = dotString + "L" + primitive + " -> " \
				+ "R" + primitive + " [style=invis, weight=1000]}\n"
		i = i + 1
	return dotString

def lgsegdot(lg, nodeDiffList, sdiffs, lg2=None):
	"""Produce a .dot string representation of the segmentation graph
	corresponding to a bipartite graph."""
	
	dotString = bipartiteNodeString(lg, nodeDiffList, lg2)
	
	# Compute segment information. We only need the maps (and diffs,
	# if provided)
	(segmentPrimitiveMap, primitiveSegmentMap, _, _) \
			= lg.segmentGraph()

	dotString = dotString + "\n\t/* EDGES (FOR COMMON OBJECTS) */\n"
	for cid in sorted(list(list(primitiveSegmentMap))):
		# HACK - this map has changed somehow.
		csegment = primitiveSegmentMap[cid].values()[0]
		commonIds = segmentPrimitiveMap[csegment][0] 
		for neighbor in commonIds: 
			# Prevent self-edges.
			if not neighbor == cid:
				color = ""
				if cid in list(sdiffs):
					errorEdges = sdiffs[cid]
					# Color false positives red.
					if neighbor in errorEdges[0] and neighbor not in errorEdges[1]:
						color = ",color=red,penwidth=2.0"
				dotString = dotString + "\tL" + cid + " -> " + "R" + neighbor \
					+ " [dir=none" + color + "];\n"

		# Show false negative as red dashed lines.
		if cid in list(sdiffs):
			errorEdges = sdiffs[cid]
			for primitive in errorEdges[1]:
				if not primitive == cid and primitive not in commonIds:
					dotString = dotString + "\tL" + cid + " -> " + "R" + primitive \
						+ " [dir=none,color=red,penwidth=2.0,style=dashed];\n"

	dotString = dotString + "}"
	return dotString

def lgPrimitiveDot(lg, nodeDiffList, edgeDiffList):
	"""Produce a .dot string representation of a primitive graph."""
	dotString = ""
	dotString += primitiveNodeString(lg,nodeDiffList)
	dotString += "\n\t/* EDGES (PRIMITIVE RELATIONSHIPS) */\n"
	edges = list(lg.elabels)
	
	# Edges/Mislabeled edges from graph lg, as appropriate.
	# Check for opportunities to create bidirectional edges.
	seen = set()
	for (parent, child) in sorted(list(edges)):
		errorString = ""
		labelString = createLabelList(lg.elabels[(parent,child)])

		# Skip edges that have already been created.
		if (parent, child) in seen:
			continue
	
		bidirectional=""
		# Check label in opposite direction.
		if (child, parent) in list(edges):
			oppositeLabelString = createLabelList(lg.elabels[(child,parent)])
			if labelString == oppositeLabelString:
				bidirectional="dir=both,"
				seen.add((child,parent))

		Elabel = []
		for (pair,_,oelabel) in edgeDiffList:
			# NOTE: specific to current implementation for missing edge repr.
			if pair == (parent,child):
				Elabel += getFirstElements(oelabel)
				errorString = ",color=red,penwidth=2.0,fontsize=14,fontcolor=red"
		
		Estring = ""
		if len(Elabel) > 0:
			Estring = "\\n( " + createLabelList(Elabel) + " )"

		dotString = dotString + "\t" + parent + " -> " + child \
			+ " [" + bidirectional + "label=\"" + labelString + Estring + "\"" \
			+ errorString + "];\n"


	# Check for missing edges.
	for ((parent,child), labels, oelabel) in edgeDiffList:
		if labels == [('_',1.0)]:
			errorString = ",color=red,penwidth=2.0,fontcolor=red"
			otherLabel = createLabelList(getFirstElements(oelabel))
			dotString = dotString + "\t" + parent + " -> " + child \
					+ " [fontsize=14,label=\"_\\n( " + otherLabel + " )\"" + errorString + "];\n"

	dotString = dotString + "}"
	return(dotString)


def lgdot(lg, nodeDiffList, edgeDiffList, lg2=None):
	"""Produce a .dot string representation for a bipartite graph."""
	dotString = ""

	dotString = dotString + bipartiteNodeString(lg,nodeDiffList,lg2)
	dotString = dotString + "\n\t/*  EDGES (PRIMITIVE RELATIONSHIPS) */\n"
	edges = list(lg.elabels)

	# Edges/Mislabeled edges from graph lg, as appropriate.
	for (parent, child) in sorted(list(edges)):
		errorString = ""
		otherLabel = []
		for (pair,_,oelabel) in edgeDiffList:
			# NOTE: specific to current implementation for missing edge repr.
			if pair == (parent,child):
				errorString = ",color=red,penwidth=2.0,fontsize=14,fontcolor=red"
				otherLabel += getFirstElements(oelabel)  
		otherString = ""
		if len(otherLabel) > 0:
			otherString = "\n( " + createLabelList(otherLabel) + " )"

		labelString = createLabelList(lg.elabels[(parent,child)])
		dotString = dotString + "\tL" + parent + " -> " + "R" + child \
			+ " [label=\"" + labelString + otherString + "\"" \
			+ errorString + "];\n"

	# Check for missing edges.
	for ((parent,child), labels, oelabel) in edgeDiffList:
		if labels == [('_',1.0)]:
			errorString = ",color=red,penwidth=2.0,fontcolor=red"
			otherLabel = "\\n( " + createLabelList(getFirstElements(oelabel)) + " )"
			dotString = dotString + "\tL" + parent + " -> " + "R" + child \
				+ " [fontsize=14,label=\"_" + otherLabel + "\"" + errorString + "];\n"

	dotString = dotString + "}"
	return(dotString)

def dagSegmentString(lg, lg2, segPrimMap, primSegMap, correctSegs):
	dotString = "digraph dag {\n\trankdir=LR; ranksep=1.0;\n\tedge[fontsize=13,weight=1]; node[fontsize=13,shape=box]; graph[ordering=out];\n"

	dotString = dotString + "\n\t/* NODES (OBJECTS) */\n\t"
	for segmentId in sorted(list(list(segPrimMap))):
		BadSegmentation = True
		
		# Search for this segment in the list of correct segments.
		if segmentId in correctSegs:
			BadSegmentation = False

		# Get segment label,  all labels for primitives in the segment.
		(segIds, slabel) = segPrimMap[ segmentId ]
		otherLabel = createSegPrimitivesLabel(segmentId, lg2, segPrimMap) 

		classError = ""
		slabelString = createLabelList(slabel)
		if not slabelString == otherLabel:
			classError = '\\n(' + otherLabel + ')'

		# Format segmentation errors differently than mislabelings,
		# than correct segments.
		if BadSegmentation:
			color = 'red,peripheries=2,fontcolor=red'
		elif len(classError) > 0:
			color = 'red,fontcolor=red'
		else:
			color = 'blue'

		dotString = dotString + segmentId + " [label=\"" \
				+  slabelString + classError + "\\n" \
				+  segmentId + "\\n"\
				+  createLabelList(segIds," ") + "\", color = " + color + "];\n\t"
	return dotString

def dagSegmentRelString(lg, lg2, segPrimMap, treeEdges, otherEdges, segmentEdges,\
		treeOnly, segRelDiffs ):
	dotString = "\n\t/* EDGES (OBJECT RELATIONSHIPS)    */\n\t"

	for edge in list(segRelDiffs):
		formatting =",color=red,fontcolor=red,penwidth=3"
	
		if treeOnly and edge not in treeEdges:
			continue 

		# Produce edge labels.
		parentPrim = list(segPrimMap[ edge[0] ][0])[0]
		childPrim = list(segPrimMap[ edge[1] ][0])[0]
		elabel = createLabelList(list(lg.elabels[ (parentPrim, childPrim) ]))

		otherLabel = createRelPrimitivesLabel( edge, lg2, segPrimMap)

		dotString += str(edge[0]) + ' -> ' + str(edge[1])
		dotString += " [label=\"" + elabel  \
				+ "\\n(" + otherLabel + ")\\n\""+ formatting + "]" + ';\n\t'

	for edge in segmentEdges:
		formatting = ""

		# Skip incorrect edges; skip non-tree edges if instructed.
		if edge in list(segRelDiffs) or \
			(treeOnly and edge not in treeEdges):
			continue

		# Produce edge labels.
		parentPrim = list(segPrimMap[ edge[0] ][0])[0]
		childPrim = list(segPrimMap[ edge[1] ][0])[0]
		elabel = createLabelList(list(lg.elabels[ (parentPrim, childPrim) ]))

		dotString += str(edge[0]) + ' -> ' + str(edge[1])
		dotString += " [label=\"" + str(elabel) + "\""+ formatting + "]" + ';\n\t'

	dotString += '\n}'
	return dotString
	

def lgDag(lg, lg2, treeOnly, correctSegs, segRelDiffs):
	"""Directed graph over segments."""
	(segmentPrimitiveMap, primitiveSegmentMap, noparentSegments, segmentEdges) = \
				lg.segmentGraph()
	(rootNodes, treeEdges, otherEdges) = lg.separateTreeEdges()
	head = dagSegmentString(lg,lg2, segmentPrimitiveMap, primitiveSegmentMap,\
			correctSegs)
	rest = dagSegmentRelString(lg, lg2, segmentPrimitiveMap, treeEdges, otherEdges,\
			segmentEdges, treeOnly, segRelDiffs)
	return head + rest


def main():
	if len(sys.argv) < 2:
		print("Usage: [[python]] lg2dot.py <lg.csv> [lg2.csv] [ b | s | p | t ]")
		print("")
		print("    Produce a dot file containing either a:")
		print("       1. (default) directed graph of relationships over objects, or a")
		print("       2. (p) directed graph over primitives,")
		print("       3. (b) bipartite graph over primitives,")
		print("       4. (s) segmentation graph over primitives,")
		print("       5. (t) tree of relationships over objects (assumes hierarchical structure).")
		print("              (NOTE: all inherited relationships are removed from the graph)")
		
		print("")
		print("    The object graphs (options d and t) only show objects and edges defined in")
		print("    the first graph. To see all milabelings at the primitive level, use")
		print("    the default or (s) options.")

		print("\n    VISUALIZING DIFFERENCES BETWEEN GRAPHS\n")
		print("    If two files are provided, both should use the same ")
		print("    node (primitive) identifiers.")
		print("")
		print("    For two files, disagreements between the first and second graphs are shown")
		print("    in red.")
		print("\n    REPRESENTATION\n")
		print("    Ovals are used for primitives, squares for objects, and squares with")
		print("    doubled edges for objects appearing in lg.csv but not lg2.csv")
		print("    (for segmentation errors). Labeling disagreements show lg1.csv")
		print("    labels above labels from lg2.csv (shown in parentheses).")
		print("    In the default and 'b' primitive graphs, objects are shown using")
		print("    bidirectional edges between primitives in the same object, which")
		print("    have the same label as the object.")
		print("")
		print("    NOTE: object-level plots ('d' and 't' options) assume one level of structure")
		print("    for objects (i.e. each primitive belongs to one object).")
		sys.exit(0)

	fileName = sys.argv[1]
	lg = Lg(fileName)

	# Hide unlabeled edges.
	lg.hideUnlabeledEdges()

	if len(sys.argv) == 2:
		# RZ: Modification: show the object graph.
		# HACK: to get correct segments, compare graph with itself.
		(_, nodeconflicts, edgeconflicts, segDiffs, correctSegs, \
				segRelDiffs) = lg.compare(lg)
		print( lgDag(lg, lg, False, correctSegs, segRelDiffs) )

	elif len(sys.argv) == 3:
		# Graph types for single graph - check second argument passed (sys.argv[2])
		# - Bipartite graph (b)
		# - DAG graph over segments (default)
		# - Tree(s) over segments (t)
		# - Segmentation graph over primitives (s)
		# - Directed graph over primitives (p)

		# HACK: to get correct segments, compare graph with itself.
		(_, nodeconflicts, edgeconflicts, segDiffs, correctSegs, \
				segRelDiffs) = lg.compare(lg)

		if sys.argv[2] == 't':
			print(lgDag(lg, lg, True, correctSegs, segRelDiffs))
		elif sys.argv[2] == 's':
			print( lgsegdot(lg, {}, {}) )
		elif sys.argv[2] == 'b':
			print(lgdot(lg, [], []))
		elif sys.argv[2] == 'p':
			print( lgPrimitiveDot(lg, nodeconflicts, edgeconflicts) )
		else: 
			# Difference DAG over objects.
			comparisonFileName = sys.argv[2]
			lg2 = Lg(comparisonFileName)
			(_, nodeconflicts, edgeconflicts, segDiffs, correctSegs, \
				segRelDiffs) = lg.compare(lg2)
			print(lgDag(lg, lg2,  False, correctSegs, segRelDiffs))
	

	elif len(sys.argv) > 3:
		# Compute graph difference.
		comparisonFileName = sys.argv[2]
		lg2 = Lg(comparisonFileName)
		(_, nodeconflicts, edgeconflicts, segDiffs, correctSegs, \
			segRelDiffs) = lg.compare(lg2)

		# Produce the appropriate graph type.
		if sys.argv[3] == 's':
			print( lgsegdot(lg, nodeconflicts, segDiffs, lg2) )
		elif (sys.argv[3] == 'd'):
			print( lgDag(lg, lg2, False, correctSegs, segRelDiffs) )
		elif (sys.argv[3] == 't'):
			print( lgDag(lg, lg2, True, correctSegs, segRelDiffs) )
		elif (sys.argv[3] == 'b'):
			print( lgdot(lg, nodeconflicts, edgeconflicts, lg2) )
		else:
			print( lgPrimitiveDot(lg, nodeconflicts, edgeconflicts) )

main()

