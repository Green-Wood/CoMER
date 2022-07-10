################################################################
# lg.py - Label Graph Class
#
# Authors: R. Zanibbi and H. Mouchere, 2012
# Copyright (c) 2012-2014 Richard Zanibbi and Harold Mouchere
################################################################
import csv
import sys
import math
import copy
import smallGraph
import compareTools
import os

class Lg(object):
	"""Class for bipartite graphs where the two node sets are identical, and
	multiple node and edge labels are permited. The graph and individual nodes
	and edges have associated values (e.g. weights/probabilities)."""

	# Define graph data elements ('data members' for an object in the class)
	__slots__ = ('file','gweight','nlabels','elabels','error','absentNodes',\
			'absentEdges','hiddenEdges', 'cmpNodes', 'cmpEdges')

	##################################
	# Constructors (in __init__)
	##################################
	def __init__(self,*args): 
		"""Graph data is read from a CSV file or provided node and edge label
		dictionaries.  If invalid entries are found, the error flag is set to
		true, and graph input continues.  In .lg files, blank lines are
		ignored, and # may be used for comment lines in CSV graph files."""
		self.error = False
		self.gweight = 1.0
		self.nlabels = {}
		self.elabels = {}
		self.absentNodes = set([])
		self.absentEdges = set([])
		self.hiddenEdges = {}
		self.cmpNodes = compareTools.cmpNodes
		self.cmpEdges = compareTools.cmpEdges
	
		
		fileName = None
		nodeLabels = {}
		edgeLabels = {}
		
		validAsteriskEdges = set()
		invalidAsteriskNodes = set()

		if len(args) == 1:
			fileName = args[0]
			self.file = fileName # DEBUG: add filename for debugging purposes.
		elif len(args) == 2:
			nodeLabels = args[0]
			edgeLabels = args[1]

		if fileName == None:
			# CONSTRUCTOR 1: try to read in node and edge labels.
			self.file = None
			# Automatically convert identifiers and labels to strings if needed.
			for nid in list(nodeLabels):
				if not isinstance(nid, str):
					nid = str(nid)

				newdict = {}
				for label in list(nodeLabels[nid]):
					if not isinstance(nid, str):
						label = str(label)
				
					# Weights need to be floats.
					if not isinstance( nodeLabels[nid][label], float ):
						self.error = True
						sys.stderr.write('  !! Invalid weight for node ' + nid + ', label \"' \
								+ label +"\": " + str(nodeLabels[nid][label]) + "\n")
					newdict[ label ] = nodeLabels[nid][label]
				self.nlabels[nid] = newdict

			# WARNING: self-edges are not detected if edge labels used
			# for initialization.
			for eid in list(edgeLabels):
				if not isinstance(eid[0], str) or not isinstance(eid[1],str):
					eid[0] = str(eid[0])
					eid[1] = str(eid[1])

				newdict = {}
				for label in list(edgeLabels[eid]):
					if not isinstance(label, str):
						label = str(label)
					if not isinstance( edgeLabels[eid][label], float ):
						self.error = True
						sys.stderr.write('  !! Invalid weight for edge ' + str(eid) + ', label \"' \
								+ label +"\": " + str(edgeLabels[eid][label]) + "\n")
					newdict[ label ] = edgeLabels[eid][label]

				self.elabels[eid] = newdict
		else:
			# CONSTRUCTOR 2: Read graph data from CSV file.
			MIN_NODE_ENTRY_LENGTH = 3
			MIN_EDGE_ENTRY_LENGTH = 4
			MIN_OBJECT_ENTRY_LENGTH = 5
			MIN_OBJECT_EDGE_ENTRY_LENGTH = 5
			try:
				fileReader = csv.reader(open(fileName))
			except:
				# Create an empty graph if a file cannot be found.
				# Set the error flag.
				sys.stderr.write('  !! IO Error (cannot open): ' + fileName + '\n')
				self.error = True
				return
			objectDict = dict([])
			for row in fileReader:
				# Skip blank lines.
				if len(row) == 0 or len(row) == 1 and row[0].strip() == '':
					continue

				entryType = row[0].strip()
				if entryType == 'N':
					if len(row) < MIN_NODE_ENTRY_LENGTH:
						sys.stderr.write(' !! Invalid node entry length: ' +str(len(row))+\
								'\n\t' + str(row) + '\n')
						self.error = True
					else:
						nid = row[1].strip() # remove leading/trailing whitespace
						if nid in list(self.nlabels):
							nlabelDict = self.nlabels[ nid ]
							nlabel = row[2].strip()
							# if nlabel in nlabelDict:
								# # Note possible error.
								# sys.stderr.write(' !! Repeated node label entry ('\
										# + self.file + '): ' \
										# + '\n\t' + str(row) + '\n')
								# self.error = True
							# Add (or replace) entry for the label.
							nlabelDict[ nlabel ] = float(row[3])
						else:
							# New primitive; create new dictionary for 
							# provided label (row[2]) and value (row[3])
							nid = row[1].strip()
							nlabel = row[2].strip()

							# Feb. 2013 - allow no weight to be provided.
							if len(row) > MIN_NODE_ENTRY_LENGTH:
								self.nlabels[ nid ] = { nlabel : float(row[3]) }
							else:
								self.nlabels[ nid ] = { nlabel : 1.0 }
	
				elif entryType == 'E':
					if len(row) < MIN_EDGE_ENTRY_LENGTH:
						sys.stderr.write(' !! Invalid edge entry length: ' +str(len(row))+\
								'\n\t' + str(row) + '\n')
						self.error = True
					else:
						primPair = ( row[1].strip(), row[2].strip() )
						#self to self edge = error
						if primPair[0] == primPair[1]:
							sys.stderr.write('  !! Invalid self-edge (' +
									self.file + '):\n\t' + str(row) + '\n')
							self.error = True
							nid = primPair[0]
							if nid in list(self.nlabels):
								nlabelDict = self.nlabels[ nid ]
								nlabel = row[3].strip()
								# if nlabel in nlabelDict:
									# # Note possible error.
									# sys.stderr.write(' !! Repeated node label entry ('\
										# + self.file + '): ' \
										# + '\n\t' + str(row) + '\n')
							# Add (or replace) entry for the label.
							nlabelDict[ nlabel ] = float(row[4])

						#an edge already existing, add a new label
						elif primPair in list(self.elabels):
							elabelDict = self.elabels[ primPair ]
							elabel = row[3].strip()
							# if elabel in elabelDict:
								# # Note possible error.
								# sys.stderr.write(' !! Repeated edge label entry (' \
										# + self.file + '):\n\t' + str(row) + '\n')
								# self.error = True
							if elabel == '*':
								# if using old fashion segmentation label, convert it by finding the (only) node label
								if primPair[0] in self.nlabels and primPair[1] in self.nlabels and \
								self.nlabels[ primPair[0]] == self.nlabels[ primPair[1]]:
									elabel =  list(self.nlabels[ primPair[0]])[0]
									
									validAsteriskEdges.add( primPair )

								else:
									sys.stderr.write(' !! * edge used with ambiguous node labels (' \
										+ str(self.nlabels[ primPair[0]]) + ' vs. ' \
										+ str(self.nlabels[ primtPair[1]]) + ') in ' \
										+ self.file + '):\n\t' + ", ".join(row) + '\n')
									
									# RZ: Oct. 14 - cheap and dirty correction.
									elabel = 'MergeError'
									self.nlabels[ primPair[0] ] = { elabel : 1.0 }
									self.nlabels[ primPair[1] ] = { elabel : 1.0 }
									self.error = True

									invalidAsteriskNodes.add( primPair[0] )
									invalidAsteriskNodes.add( primPair[1] )
			
							# Add (or replace) entry for the label.
							# Feb. 2013 - allow no weight.
							if len(row) > MIN_EDGE_ENTRY_LENGTH:
								elabelDict[ elabel ] = float(row[4])
							else:
								elabelDict[ elabel ] = 1.0
						else:
							# Add new edge label entry for the new edge label
							# as a dictionary.
							primPair = ( row[1].strip(), row[2].strip() )
							elabel = row[3].strip()
							if elabel == '*':
								# if using old fashion segmentation label, convert it by finding the (only) node label
								if primPair[0] in self.nlabels and primPair[1] in self.nlabels and \
								self.nlabels[ primPair[0]] == self.nlabels[ primPair[1]]:
									elabel = list(self.nlabels[ primPair[0]])[0]
									validAsteriskEdges.add( primPair )

								else:
									sys.stderr.write(' !! * edge used with ambiguous node labels (' \
										+ str(self.nlabels[ primPair[0]]) + ' vs. ' \
										+ str(self.nlabels[ primPair[1]]) + ') in ' \
										+ self.file + '):\n\t' + ", ".join(row) + '\n')
									
									elabel = 'MergeError'
									self.nlabels[ primPair[0] ] = { elabel : 1.0 }
									self.nlabels[ primPair[1] ] = { elabel : 1.0 }
									self.error = True

									invalidAsteriskNodes.add( primPair[0] )
									invalidAsteriskNodes.add( primPair[1] )

							self.elabels[ primPair ] = { elabel : float(row[4]) }
				elif entryType == 'O':
					if len(row) < MIN_OBJECT_ENTRY_LENGTH:
						sys.stderr.write(' !! Invalid object entry length: '+str(len(row))+\
								'\n\t' + str(row) + '\n')
						self.error = True
					else:
						rawnodeList = row[4:] # get all other item as node id
						oid =  row[1].strip()
						nlabel =  row[2].strip()
						nValue =  float(row[3].strip())
						nodeList = []
						# add all nodes
						for n in rawnodeList:
							nid = n.strip()
							nodeList.append(nid)
							if nid in list(self.nlabels):
								nlabelDict = self.nlabels[ nid ]
								
								# Add (or replace) entry for the label.
								nlabelDict[ nlabel ] = nValue
							else:
								# New primitive; create new dictionary for 
								# provided label and value 	
								# Feb. 2013 - allow no weight to be provided.
								self.nlabels[ nid ] = { nlabel : nValue }
						#save the nodes of this object
						objectDict[oid] = nodeList
						#add all edges
						for nid1 in nodeList:
							#nid1 = n1.strip()
							for nid2 in nodeList:
								#nid2 = n2.strip()
								if nid1 != nid2:
									primPair = ( nid1, nid2 )
									elabel = nlabel 
									if primPair in list(self.elabels):
										elabelDict = self.elabels[ primPair ]
										
										# Add (or replace) entry for the label.
										elabelDict[ elabel ] = nValue
									else:
										# Add new edge label entry for the new edge label
										# as a dictionary.
										self.elabels[ primPair ] = { elabel : nValue }

				elif entryType == 'R' or entryType == 'EO':
					if len(row) < MIN_OBJECT_EDGE_ENTRY_LENGTH:
						sys.stderr.write(' !! Invalid object entry length: ' +str(len(row))+\
								'\n\t' + str(row) + '\n')
						self.error = True
					else:
						oid1 = row[1].strip()
						oid2 = row[2].strip()
						elabel = row[3].strip()
						eValue = float(row[4].strip())
						validRelationship = True

						if not oid1 in objectDict:
							sys.stderr.write(' !! Invalid object id: "' + oid1+\
									'" - IGNORING relationship:\n\t' + str(row) + '\n')
							self.error = True
							validRelationship = False
						if not oid2 in objectDict:
							sys.stderr.write(' !! Invalid object id: "' + oid2+\
									'" - IGNORING relationship:\n\t' + str(row) + '\n')
							self.error = True
							validRelationship = False
						if validRelationship:
							nodeList1 = objectDict[oid1] # get all other item as node id
							nodeList2 = objectDict[oid2] # get all other item as node id

							for nid1 in nodeList1:
								for nid2 in nodeList2:
									if nid1 != nid2:
										primPair = ( nid1, nid2 )
										if primPair in list(self.elabels):
											elabelDict = self.elabels[ primPair ]
											
											# Add (or replace) entry for the label.
											elabelDict[ elabel ] = eValue
										else:
											# Add new edge label entry for the new edge label
											# as dictionary.
											self.elabels[ primPair ] = { elabel : eValue }
									else:			
										sys.stderr.write('  !! Invalid self-edge (' +
										self.file + '):\n\t' + str(row) + '\n')
										self.error = True

				# DEBUG: complaints about empty lines here...
				elif len(entryType.strip()) > 0 and entryType.strip()[0] == '#':
					# Ignore lines with comments.
					pass
				else:
					sys.stderr.write('  !! Invalid graph entry type (expected N, E, O, R or EO): ' \
							+ str(row) + '\n')
					self.error = True
	
		# Add any implicit nodes in edges explicitly to the hash table
		# containing nodes. The 'nolabel' label is '_'.
		anonNode = False
		anodeList = []
		for elabel in list(self.elabels):
			nid1 = elabel[0]
			nid2 = elabel[1]

			if not nid1 in list(self.nlabels):
				self.nlabels[ nid1 ] = { '_' : 1.0 }
				anodeList = anodeList + [ nid1 ]
				anonNode = True
			if not nid2 in list(self.nlabels):
				self.nlabels[ nid2 ] = { '_' : 1.0 }
				anodeList = anodeList + [ nid2 ]
				anonNode = True
		if anonNode:
			sys.stderr.write('  ** Anonymous labels created for:\n\t' \
				+ str(anodeList) + '\n')


		# RZ Oct. 2014: add invalid merge edges and node labels where missing.
		#    This catches when a valid * edge is connected to an invalid one,
		#    relabeling the edge.
		invalidAsteriskNodeList = sorted( list(invalidAsteriskNodes) )
		while len(invalidAsteriskNodeList) > 0:
			# Remove last element from the list.
			nextPrimId = invalidAsteriskNodeList.pop()
			
			# Linear traversal for matches (a 'region growing' algorithm)
			# Add a traversal each time a new connected edge is found.
			# NOTE: this will not add edges missing in the input (e.g.
			#  if '*' is defined in one direction but not the other.
			for (parent, child) in validAsteriskEdges:
				otherId = None
				if parent == nextPrimId:
					otherId = child
				if child == nextPrimId:
					otherId = parent

				if otherId != None:
					if not otherId in invalidAsteriskNodes:
						invalidAsteriskNodes.add( otherId )
						invalidAsteriskNodeList.append( otherId )

					self.nlabels[ otherId ] = { 'MergeError' : 1.0 }
					self.elabels[ (parent, child) ] = { 'MergeError' : 1.0 }

	##################################
	# String, CSV output
	##################################
	def __str__(self):
		nlabelcount = 0
		elabelcount = 0
		for nid in list(self.nlabels):
			nlabelcount = nlabelcount + len(list(self.nlabels[nid]))
		for eid in list(self.elabels):
			elabelcount = elabelcount + len(list(self.elabels[eid]))

		return 'Nodes: ' + str(len(list(self.nlabels))) \
				+ ' (labels: ' + str(nlabelcount) \
				+ ')   Edges: ' + str(len(list(self.elabels))) \
				+ ' (labels: ' + str(elabelcount) \
				+ ')   Error: ' + str(self.error)


	def csvObject(self):
		"""Construct CSV data file using object-relationship format. Currently 
		weight values are only placeholders (i.e. 1.0 is always used)."""
		outputString = ""

		(segmentPrimitiveMap, primitiveSegmentMap, rootSegments, \
				segmentEdges) = self.segmentGraph()

		# Write the file name.
		outputString += "# " + os.path.split(self.file)[1]
		outputString += "\n\n"

		# Write number of objects and format information.
		# Output object information.
		outputString += "# " + str(len(list(segmentPrimitiveMap))) + " Objects"
		outputString += "\n"
		outputString += "# FORMAT: O, Object ID, Label, Weight, [ Primitive ID List ]"
		outputString += "\n"

		for objectId in sorted( list(segmentPrimitiveMap) ):
			for label in sorted(segmentPrimitiveMap[objectId][1]):
				outputString += "O, " + objectId + ", " + label + ", 1.0"
				for primitiveId in sorted( segmentPrimitiveMap[ objectId ][ 0 ] ):
					outputString += ", " + primitiveId 
				outputString += "\n"

		# Write number of relationships and format information.
		# Write relationship information.
		outputString += "\n"
		outputString += "# " + str( len(list(segmentEdges)) ) + " Relationships (Pairs of Objects)"
		outputString += "\n"
		outputString += "# FORMAT: R, Object ID (parent), Object ID (child), Label, Weight" 
		outputString += "\n"

		for (parentObj, childObj) in sorted( list(segmentEdges) ):
			for relationship in sorted( list(segmentEdges[ (parentObj, childObj) ]) ):
				outputString += "R, " + parentObj + ", " + childObj + ", " 
				outputString += relationship + ", 1.0"
				outputString += "\n"

		return outputString


	def csv(self):
		"""Construct CSV data file representation as a string."""
		# NOTE: currently the graph value is not being stored...
		sstring = ''
		nlist = []
		elist = []
		for nkey in list(self.nlabels):
			nodeLabels = self.nlabels[nkey]
			for nlabel in list(nodeLabels):
				nstring = 'N,' + nkey + ',' + nlabel + ',' + \
						str(nodeLabels[nlabel]) + '\n'
				nlist = nlist + [ nstring ]

		for npair in list(self.elabels):
			edgeLabels = self.elabels[npair]
			for elabel in list(edgeLabels):
				estring = 'E,' + npair[0] + ',' + npair[1] + ',' + elabel + ',' + \
						str(edgeLabels[ elabel ]) + '\n'
				elist = elist + [ estring ]

		# Sort the node and edge strings lexicographically.
		# NOTE: this means that '10' precedes '2' in the sorted ordering
		nlist.sort()
		elist.sort() 
		sstring += '# ' + os.path.split(self.file)[1] + '\n\n' 
		sstring += '# ' + str(len(nlist)) + ' Nodes\n'
		sstring += "# FORMAT: N, Primitive ID, Label, Weight\n"
		for nstring in nlist:
			sstring = sstring + nstring
		sstring += "\n"

		sstring += '# ' + str(len(elist)) + ' Edges\n'
		sstring += '# FORMAT: E, Primitive ID (parent), Primitive ID (child), Label, Weight\n'
		for estring in elist:
			sstring = sstring + estring
		
		return sstring

	##################################
	# Construct segment-based graph
	# for current graph state
	##################################
	def segmentGraph(self):
		"""Return dictionaries from segments to strokes, strokes to segments,
		segments without parents, and edges labeled as segment (w. symbol label)."""
		primitiveSegmentMap = {}
		segmentPrimitiveMap = {}
		#noparentSegments = []
		segmentEdges = {}  # Edges between detected objects (segments)

		self.hideUnlabeledEdges()

		# Note: a segmentation edge in either direction merges a primitive pair.
		primSets = {}
		for node,labs in self.nlabels.items():
			primSets[node] = {}
			for l in labs:
				(cost,_)=self.cmpNodes([l],[])
				if(cost > 0):
					primSets[node][l] = set([node])
			#if len(primSets[node]) == 0:
			#	primSets[node]['_'] = set([node]) #at least one empty label
		for (n1, n2) in list(self.elabels):
			commonLabels = set(list(self.nlabels[n1])).intersection(list(self.nlabels[n2]),list(self.elabels[(n1,n2)]))
			for l in commonLabels:
				#check if this label is interesting or not => compare to 'nothing', if there is not error, it means it is not interesting
				(cost,_)=self.cmpNodes([l],[])
				if(cost > 0):
					primSets[n1][l].add(n2)
					primSets[n2][l].add(n1)

		# NOTE: Segments can have multiple labels
		# A primitive can belong to several different
		# segments with different sets of primitives with different labels.
		# but there is only one segment with the same label attached to each primitive.
		i = 0
		segmentList = []
		rootSegments = set([])
		
		# For each label associated with each primitive, there is a possible object/segment
		for primitive,segments in primSets.items():
			if not primitive in primitiveSegmentMap:
				primitiveSegmentMap[ primitive ] = {}
			for lab in list(segments):
				alreadySegmented = False
				for j in range(len(segmentList)):
					if segments[lab] == segmentList[j]["prim"]:
						if not primitive in primitiveSegmentMap:
							primitiveSegmentMap[ primitive ] = {}
						primitiveSegmentMap[ primitive ][lab] = 'Obj' + str(j)
						alreadySegmented = True
						if lab not in segmentList[j]["label"]:
							segmentPrimitiveMap[  'Obj' + str(j) ][1].append(lab)
							segmentList[j]["label"].add(lab)
						break

				if not alreadySegmented:
					# Add the new segment.
					newSegment = 'Obj' + str(i)
					segmentList = segmentList + [ {"label":{lab},"prim":primSets[primitive][lab]} ]
					segmentPrimitiveMap[ newSegment ] = (segments[lab],[lab])
					primitiveSegmentMap[ primitive ][lab] = newSegment
					rootSegments.add(newSegment)
					i += 1

		# Identify 'root' objects/segments (i.e. with no incoming edges),
		# and edges between objects. **We skip segmentation edges.
		for (n1, n2), elabs in self.elabels.items():
			segment1 = primitiveSegmentMap[n1]
			segment2 = primitiveSegmentMap[n2]
			
			#for all possible pair of segments with these two primitives, look for the effective relation labels
			possibleRelationLabels = set(list(elabs)).difference(list(self.nlabels[n1]),list(self.nlabels[n2]))
			if len(possibleRelationLabels) != 0:
				#for all pair of labels
				for l1,pset1 in segment1.items():
					for l2, pset2 in segment2.items():
						#if not in the same seg
						if pset1 != pset2:
							#look for the label which is common for all primitive pair in the two segments
							theRelationLab = possibleRelationLabels
							for p1 in primSets[n1][l1]:
								for p2 in primSets[n2][l2]:
									if(p1,p2) in self.elabels:
										theRelationLab &= set(list(self.elabels[(p1,p2)]))
									else:
										theRelationLab = set([]) # it should be a clique !
									if len(theRelationLab) == 0:
										break
								if len(theRelationLab) == 0:
									break
							# there is a common relation if theRelationLab is not empty
							if len(theRelationLab) != 0:
								#we can remove seg2 from the roots
								if pset2 in rootSegments:
									rootSegments.remove(pset2)
								#print (str((n1, n2))+ " => " + str(( pset1,  pset2)) + "  = " + str(theRelationLab))
								for label in theRelationLab:
									#check if this label is interesting or not => compare to 'nothing', if there is not error, it means it is not interesting
									(cost,_)=self.cmpNodes([label],[])
									if(cost > 0):
										if ( pset1,  pset2) in segmentEdges:
											if label in segmentEdges[ ( pset1,  pset2) ]:
												# Sum weights for repeated labels
												segmentEdges[ ( pset1,  pset2)][label] += \
														self.elabels[(n1,n2)][label]
											else:
												# Add unaltered weights for new edge labels
												segmentEdges[ ( pset1,  pset2) ][label] = \
														self.elabels[(n1,n2)][label]
										else:
											segmentEdges[ ( pset1, pset2) ] = {}
											segmentEdges[ ( pset1, pset2) ][label] = \
													self.elabels[(n1,n2)][label]

		self.restoreUnlabeledEdges()

		return (segmentPrimitiveMap, primitiveSegmentMap, list(rootSegments), \
				segmentEdges)


	##################################
	# Metrics and Graph Differences
	##################################
	def compareSegments(self, lg2):
		"""Compute the number of differing segments, and record disagreements.
		The primitives in each graph should be of the same number and names
		(identifiers). Nodes are merged that have identical (label,value)
		pairs on nodes and all incoming and outgoing edges."""
		(sp1, ps1, _, sre1) = self.segmentGraph()
		(sp2, ps2, _, sre2) = lg2.segmentGraph()

		allNodes = set(list(ps1))
		assert allNodes == set(list(ps2))
	
		edgeDiffCount = 0
		edgeDiffClassCount = 0
		segDiffs = {}
		correctSegments = set([])
		correctSegmentsAndClass = set([])
		undirDiffClassSet = set([])
		
		# List and count errors due to segmentation.
		# Use cmpNodes to compare the labels of symbols.
		# Idea : build the sub graph with the current primitive as center and only 
		for primitive in list(ps1):
			edgeFromP1 = {}
			edgeFromP2 = {}
			for (lab1,seg1) in ps1[primitive].items():
				for p in sp1[seg1][0]:
					# DEBUG (RZ): this is producing a primitive edge-level count:
					# do not count segment edges that are undefined (e.g. in one direction,
					# but not the other)
					if p != primitive and (p,primitive) in list(self.elabels) and \
							lab1 in list(self.elabels[ (p,primitive) ]):
						if p in edgeFromP1:
							edgeFromP1[p].append(lab1)
						else:  
							edgeFromP1[p] = [lab1]
	
			for (lab2,seg2) in ps2[primitive].items():
				for p in sp2[seg2][0]:
					# DEBUG (RZ) - see DEBUG comment above.
					if p != primitive and (p,primitive) in list(lg2.elabels) and \
							lab2 in list(lg2.elabels[ (p, primitive) ]):
						if p in edgeFromP2:
							edgeFromP2[p].append(lab2)
						else:
							edgeFromP2[p] = [lab2]

			# Compute differences in edge labels with cmpNodes (as they are symbol labels)
			diff1 = set([])
			diff2 = set([])
			
			# first add differences for shared primitives
			commonPrim = set(list(edgeFromP1)).intersection(list(edgeFromP2))
			for p in commonPrim:
				(cost,diff) = self.cmpNodes(edgeFromP1[p], edgeFromP2[p])
				edgeDiffCount = edgeDiffCount + cost

				# RZ June 2015: Record edges that are specifically valid merges with disagreeing labels.
				#     Also record sets of undirected edges that disagree.
				for (l1,l2) in diff:
					if l1 in list(self.nlabels[p]) and l2 in list(lg2.nlabels[p]):
						edgeDiffClassCount += 1
					
					# RZ: we do not have a *segmentation* difference if corresponding segm.
					#     edges have a label.
					elif cost > 0:
						diff1.add(p)
						diff2.add(p)

					if not (p, primitive) in undirDiffClassSet and not (primitive, p) in undirDiffClassSet:
						undirDiffClassSet.add( (primitive, p) )

			#then add differences for primitives which are not in the other set
			for p in (set(list(edgeFromP1)) - commonPrim):
				(cost,diff) = self.cmpNodes(edgeFromP1[p], [])
				edgeDiffCount = edgeDiffCount + cost
				diff1.add(p)
					
			for p in (set(list(edgeFromP2)) - commonPrim):
				(cost,diff) = self.cmpNodes(edgeFromP2[p], [])
				edgeDiffCount = edgeDiffCount + cost
				diff2.add(p)
					

			# Only create an entry where there are disagreements.
			if len(diff1) + len(diff2) > 0:
				segDiffs[primitive] = ( diff1, diff2 )
			
		# RZ: Oct. 2014 - replacing method used to evaluate segmentation. Also
		#     add checks for segments in the target being disjoint.
		#
		# Objects are defined by a set of primitives, plus a label. 
		# NOTE: This currently will support mutliple labels, but will lead to invalid
		#   "Class/Det" values in 00_Summary.txt if there are multiple labels.
		targets = {}

		# RZ: Add mapping from primitive list to object ids for direct lookup.
		targetObjIds = {}
		matchedTargets = set()
		for ObjID in list(sp2):
			# Skip absent nodes - they are not valid targets.
			if 'ABSENT' not in sp2[ ObjID ][ 1 ]:
				# Convert primitive set to a sorted tuple list.
				primitiveTupleList = tuple( sorted( list( sp2[ ObjID ][ 0 ] ) ) )
			
				# Store target label in targets dict, matches in matchedTargets dict (false init.)
				targets[ primitiveTupleList ] = sp2[ ObjID][1]
				targetObjIds[ primitiveTupleList ] = ObjID
		
		# Look for matches.
		# Do *not* allow a primitive set to be matched more than once.
		for ObjID in list(sp1):
			# HACK (RZ): DEBUG - was not checking whether matched objects were
			#               missing before absent nodes were added.
			if 'ABSENT' in sp1[ ObjID ][ 1 ]:
				continue

			primitiveTupleList = tuple( sorted( list(sp1[ObjID][ 0 ] )))
			if primitiveTupleList in list(targets) \
					and not primitiveTupleList in matchedTargets:
				matchedTargets.add( primitiveTupleList )
				correctSegments.add( ObjID )
				
				# Obtain matching labels. Create list of correct (segmentId, label) pairs
				# for *all* matching labels.
				# DEBUG: empty lists were being matched! Added test for empty matches.
				# WARNING: Only guaranteed to work for single labels.
				outputLabels = set(sp1[ ObjID ][ 1 ])
				matchingLabels = list( outputLabels.intersection( targets[ primitiveTupleList ] ) )
				if len(matchingLabels) > 0:
					ObjIDRepeats = [ObjID] * len(matchingLabels)
					correctSegmentsAndClass.add( tuple( zip(ObjIDRepeats, list(matchingLabels))))

		# Compute total number of object classifications (recognition targets)
		nbSegmClass = 0
		for (_,labs) in sp2.items():
			nbSegmClass += len(labs[1])

		# Compute the specific 'object-level' graph edges that disagree, at the
		# level of primitive-pairs. 
		segRelErrors = 0
		correctSegRels = 0
		correctSegRelLocations = 0
		primRelEdgeDiffs = {}
		
		# Iterate over object relationships in the output graph.
		for thisPair in list(sre1):
			misLabeled = False
			falsePositive = False

			thisParentIds = set(sp1[ thisPair[0] ][0])
			thisChildIds = set(sp1[thisPair[1] ][0])
			
			# RZ (June 2015): Obtain names for correct segments in target graph (lg2)
			primitiveTupleListParent = tuple( sorted( list( thisParentIds )))
			primitiveTupleListChild =  tuple( sorted( list ( thisChildIds )))
			targetObjNameParent = None
			targetObjNameChild = None

			if primitiveTupleListParent in list(targetObjIds):
				targetObjNameParent = targetObjIds[ primitiveTupleListParent ]
			if primitiveTupleListChild in list(targetObjIds):
				targetObjNameChild = targetObjIds[ primitiveTupleListChild ]
			
			# Check whether the objects are correctly segmented by their object identifiers
			if not ( thisPair[0] in correctSegments and  thisPair[1] in correctSegments):
				# Avoid counting mis-segmented objects as having valid relationships
				falsePositive = True
			elif not ( targetObjNameParent, targetObjNameChild ) in list(sre2):
				# Check that there is an edge between these objects in the target graph.
				falsePositive = True
			else:
				# RZ (June, 2015): Compare labels directly on relation edges.
				# WARNING: This checks that *all* labels are identical. Fine for single labels.
				if not sorted( list(sre1[ thisPair ]) ) == \
						sorted( list(sre2[ ( targetObjNameParent, targetObjNameChild )]) ):
					misLabeled = True
					
			# NOTE: assumes single labels on primitives.
			# primRelEdgeDiffs records which object pairs have incorrect labels.
			if falsePositive or misLabeled:
				self.error = True
				segRelErrors += 1
				primRelEdgeDiffs[ thisPair ] = [ ('Error',1.0) ]
			else:
				correctSegRels += 1
			
			# Count correct relationship structures/locations.
			if not falsePositive:
				correctSegRelLocations += 1

		# Compute object counts *without* inserted absent nodes.
		lg2.removeAbsent()
		self.removeAbsent()

		(sp2orig, ps2orig, _, sre2orig) = lg2.segmentGraph()
		(sp1orig, ps1orig, _, sre1orig) = self.segmentGraph()
		
		nLg2Objs = len(list(sp2orig)) 
		nLg1Objs = len(list(sp1orig)) 

		# For input file, need to compare against all objects after including
		# missing/additional absent nodes and edges.
		nLg1ObjsWithAbsent = len(list(sp1))

		lg2.addAbsent(self)
		self.addAbsent(lg2)
		
		# RZ (Oct. 2014) Adding indicator variables for different correctness scenarios.
		hasCorrectSegments = 1 if len(correctSegments) == nLg2Objs and \
				len(correctSegments) == nLg1ObjsWithAbsent else 0
		hasCorrectSegmentsAndLabels = 1 if len(correctSegmentsAndClass) == nLg2Objs and \
				len(correctSegmentsAndClass) == nLg1ObjsWithAbsent else 0
		
		hasCorrectRelationLocations = 1 if correctSegRelLocations == len(list(sre1)) and \
				correctSegRelLocations == len(list(sre2)) else 0
		hasCorrectRelationsAndLabels =  1 if correctSegRels == len(list(sre1)) and \
				correctSegRels == len(list(sre2)) else 0
		
		hasCorrectStructure = hasCorrectRelationLocations and hasCorrectSegments
		
		# Compile vector of (name, value) metric pairs.
		metrics = [
			("edgeDiffClassCount", edgeDiffClassCount),
			("undirDiffClassCount", len(undirDiffClassSet)),
			
			("nSeg", nLg2Objs),
			("detectedSeg", nLg1Objs),
			("dSegRelEdges", len(list(sre1))),
			("CorrectSegments", len(correctSegments)),
		    ("CorrectSegmentsAndClass", len(correctSegmentsAndClass)),
			("ClassError", nbSegmClass - len(correctSegmentsAndClass)), 
			("CorrectSegRels",correctSegRels),
			("CorrectSegRelLocations",correctSegRelLocations),
			("SegRelErrors", segRelErrors),
			
			("hasCorrectSegments", hasCorrectSegments),
			("hasCorrectSegLab", hasCorrectSegmentsAndLabels), 
			("hasCorrectRelationLocations", hasCorrectRelationLocations),
			("hasCorrectRelLab", hasCorrectRelationsAndLabels),
			("hasCorrectStructure", hasCorrectStructure) ]

		# RZ: June 2015 - need to subtract misclassified edges from non-matching edges
		# to obtain correct "Delta S" (D_S) Hamming distance for mismatched
		# segmentation edges.
		segEdgeMismatch = edgeDiffCount - edgeDiffClassCount

		return (segEdgeMismatch, segDiffs, correctSegments, metrics, primRelEdgeDiffs)

	def compare(self, lg2):
		"""Returns: 1. a list of (metric,value) pairs,
		2. a list of (n1,n2) node disagreements, 3. (e1,e2) pairs
		for edge disagreements, 4. dictionary from primitives to
		disagreeing segment graph edges for (self, lg2). Node and 
		edge labels are compared using label sets without values, and
		*not* labels sorted by value."""
		metrics  = []
		nodeconflicts = []
		edgeconflicts = []

		# HM: use the union of all node labels instead of only lg2 ones
		#     it changes the nlabelMismatch, nodeClassError and so D_C and all rates values
		allNodes = set(list(lg2.nlabels)).union(list(self.nlabels))
		numNodes = len(allNodes)
		(sp2, ps2, _, sre2) = lg2.segmentGraph()
		nSegRelEdges = len(sre2)

		# Handle case of empty graphs, and missing primitives.
		# SIDE EFFECT: 'ABSENT' nodes added to each graph.
		self.matchAbsent(lg2)

		# METRICS
		# Node and edge labels are considered as sets.
		nlabelMismatch = 0
		numEdges = numNodes * (numNodes - 1)  # No self-edges.
		numLabels = numNodes + numEdges
		elabelMismatch = 0

		# Mismatched nodes.
		nodeClassError = set()
		for nid in allNodes: #list(self.nlabels):
			(cost,errL) = self.cmpNodes(list(self.nlabels[nid]),list(lg2.nlabels[nid]))
			#if there is some error
			if cost > 0:
				# add mismatch
				nlabelMismatch = nlabelMismatch + cost
				# add errors in error list
				for (l1,l2) in errL:
					nodeconflicts = nodeconflicts + [ (nid, [ (l1, 1.0) ], [(l2, 1.0)] ) ]
				# add node in error list
				nodeClassError = nodeClassError.union([nid])

		# Two-sided comparison of *label sets* (look from absent edges in both
		# graphs!) Must check whether edge exists; '_' represents a "NONE"
		# label (no edge).

		# Identify the set of nodes with disagreeing edges.
		nodeEdgeError = set()
		for (graph,oGraph) in [ (self,lg2), (lg2,self) ]:
			for npair in list(graph.elabels):
				if not npair in oGraph.elabels \
						and (not graph.elabels[ npair ] == ['_']):
					(cost,errL) = self.cmpEdges(list(graph.elabels[ npair ]),['_'])
					elabelMismatch = elabelMismatch + cost

					(a,b) = npair
					
					# Record nodes in invalid edge
					nodeEdgeError.update([a,b])

					# DEBUG: Need to indicate correctly *which* graph has the
					# missing edge; this graph (1st) or the other (listed 2nd).
					if graph == self:
						for (l1,l2) in errL:
							edgeconflicts.append((npair, [ (l1, 1.0) ], [(l2, 1.0)] ) )
						
					else:
						for (l1,l2) in errL:
							edgeconflicts.append((npair, [ (l2, 1.0) ], [(l1, 1.0)] ) )
	
		# Obtain number of primitives with an error of any sort.
		nodeError = nodeClassError.union(nodeEdgeError)

		# One-sided comparison for common edges. Compared by cmpEdges
		for npair in list(self.elabels):
			if npair in list(lg2.elabels):
				(cost,errL) = self.cmpEdges(list(self.elabels[npair]),list(lg2.elabels[npair]))
				if cost > 0:
					elabelMismatch = elabelMismatch + cost
					(a,b) = npair
					
					# Record nodes in invalid edge
					nodeEdgeError.update([a,b])
					for (l1,l2) in errL:
						edgeconflicts.append((npair, [ (l1, 1.0) ], [(l2, 1.0)] ) )

		# Now compute segmentation differences.
		(segEdgeMismatch, segDiffs, correctSegs, segmentMetrics, segRelDiffs) \
				= self.compareSegments(lg2)

		# UNDIRECTED/NODE PAIR METRICS
		# Compute number of invalid nodePairs
		badPairs = {}
		for ((n1, n2), _, _) in edgeconflicts:
			if not (n2, n1) in badPairs:
				badPairs[(n1, n2)] = True
		incorrectPairs = len(badPairs)

		# Compute number of mis-segmented node pairs.
		badSegPairs = set([])
		for node in list(segDiffs):
			for other in segDiffs[node][0]:
				if node != other and (other, node) not in badSegPairs:
					badSegPairs.add((node, other))
			for other in segDiffs[node][1]:
				if  node != other and (other, node)not in badSegPairs:
					badSegPairs.add((node, other))
		segPairErrors = len(badSegPairs)

		# Compute performance metrics; avoid divisions by 0.
		cerror = ("D_C", nlabelMismatch) 
		lerror = ("D_L", elabelMismatch) 
		serror = ("D_S", segEdgeMismatch) 
		rerror = ("D_R", elabelMismatch - segEdgeMismatch)
		aerror = ("D_B", nlabelMismatch + elabelMismatch) 

		# DEBUG:
		# Delta E BASE CASE: for a single node, which is absent in the other
		# file, set label and segment edge mismatches to 1 (in order
		# to obtain 1.0 as the error metric, i.e. total error).
		if len(list(self.nlabels)) == 1 and \
				(len(self.absentNodes) > 0 or \
				len(lg2.absentNodes) > 0):
			elabelMismatch = 1
			segEdgeMismatch = 1
		
		errorVal = 0.0
		if numEdges > 0:
			errorVal +=  math.sqrt(float(segEdgeMismatch) / numEdges) + \
					 math.sqrt(float(elabelMismatch) / numEdges)
		if numNodes > 0:
			errorVal += float(nlabelMismatch) / numNodes
		errorVal = errorVal / 3.0
		eerror  = ("D_E(%)", errorVal)
	
		# Compile metrics
		metrics = metrics + [ aerror, cerror, lerror, rerror, serror,  \
				eerror, \
				("nNodes",numNodes), ("nEdges", numEdges), \
				("nSegRelEdges", nSegRelEdges), \
				("dPairs",incorrectPairs),("segPairErrors",segPairErrors),
				("nodeCorrect", numNodes - len(nodeError)) ]
				
		metrics = metrics + segmentMetrics

		return (metrics, nodeconflicts, edgeconflicts, segDiffs, correctSegs,\
				segRelDiffs)
		
	##################################
	# Manipulation/'Mutation'
	##################################
	def separateTreeEdges(self):
		"""Return a list of root nodes, and two lists of edges corresponding to 
		tree/forest edges, and the remaining edges."""

		# First, obtain segments; perform extraction on edges over segments.
		(segmentPrimitiveMap, primitiveSegmentMap, noparentSegments, \
				segmentEdges) = self.segmentGraph()

		# Collect parents and children for each node; identify root nodes.
		# (NOTE: root nodes provided already as noparentSegments)
		nodeParentMap = {}
		nodeChildMap = {}
		rootNodes = set(list(segmentPrimitiveMap))
		for (parent, child) in segmentEdges:
			if not child in list(nodeParentMap):
				nodeParentMap[ child ] = [ parent ]
				rootNodes.remove( child )
			else:
				nodeParentMap[ child ] += [ parent ]

			if not parent in list(nodeChildMap):
				nodeChildMap[ parent ] = [ child ]
			else:
				nodeChildMap[ parent ] += [ child ]

		# Separate non-tree edges, traversing from the root.
		fringe = list(rootNodes)

		# Filter non-tree edges.
		nonTreeEdges = set([])
		while len(fringe) > 0:
			nextNode = fringe.pop(0)

			# Skip leaf nodes.
			if nextNode in list(nodeChildMap):
				children = copy.deepcopy(nodeChildMap[ nextNode ])
				
				for child in children:
					numChildParents = len( nodeParentMap[ child ] )

					# Filter edges to children that have more than
					# one parent (i.e. other than nextNode)
					if numChildParents == 1:
						# Child in the tree found, put on fringe.
						fringe += [ child ]
					else:
						# Shift edge to non-tree status.
						nonTreeEdges.add((nextNode, child))

						nodeChildMap[ nextNode ].remove(child)
						nodeParentMap[ child ].remove(nextNode)

		# Generate the tree edges from remaining child relationships.
		treeEdges = []
		for node in nodeChildMap:
			for child in nodeChildMap[ node ]:
				treeEdges += [ (node, child) ]

		return (list(rootNodes), treeEdges, list(nonTreeEdges))
					
	def removeAbsent(self):
		"""Remove any absent edges from both graphs, and empty the fields
		recording empty objects."""
		for absEdge in self.absentEdges:
			del self.elabels[ absEdge ]

		for absNode in self.absentNodes:
			del self.nlabels[ absNode ]
		
		self.absentNodes = set([])
		self.absentEdges = set([])

	def addAbsent(self, lg2):
		"""Identify edges in other graph but not the current one."""
		selfNodes = set(list(self.nlabels))
		lg2Nodes = set(list(lg2.nlabels))
		self.absentNodes = lg2Nodes.difference(selfNodes)

		# WARN about absent nodes/edges; indicate that there is an error.
		if len(self.absentNodes) > 0:
			sys.stderr.write('  !! Inserting ABSENT nodes for:\n      ' \
					+ self.file + ' vs.\n      ' + lg2.file + '\n      ' \
				+ str(sorted(list(self.absentNodes))) + '\n')
			self.error = True

		# Add "absent" nodes.
		# NOTE: all edges to/from "absent" nodes are unlabeled.
		for missingNode in self.absentNodes:
			self.nlabels[ missingNode ] = { 'ABSENT': 1.0 }

	def matchAbsent(self, lg2):
		"""Add all missing primitives and edges between this graph and
		the passed graph. **Modifies both the object and argument graph lg2."""
		self.removeAbsent()
		self.addAbsent(lg2)

		lg2.removeAbsent()
		lg2.addAbsent(self)


	##################################
	# Routines for missing/unlabeled 
	# edges.
	##################################
	# Returns NONE: modifies in-place.
	def labelMissingEdges(self):
		for node1 in list(self.nlabels):
			for node2 in list(self.nlabels):
				if not node1 == node2:
					if not (node1, node2) in list(self.elabels):
						self.elabels[(node1, node2)] = {'_' : 1.0 }

	# Returns NONE: modifies in-place.
	def hideUnlabeledEdges(self):
		"""Move all missing/unlabeled edges to the hiddenEdges field."""
		# Move all edges labeled '_' to the hiddenEdges field.
		for edge in list(self.elabels):
			if set( list(self.elabels[ edge ]) ) == \
					set( [ '_' ] ):
				self.hiddenEdges[ edge ] = self.elabels[ edge ]
				del self.elabels[ edge ]

	def restoreUnlabeledEdges(self):
		"""Move all edges in the hiddenEdges field back to the set of
		edges for the graph."""
		for edge in list(self.hiddenEdges):
			self.elabels[ edge ] = self.hiddenEdges[ edge ]
			del self.hiddenEdges[ edge ]

	##################################
	# Merging graphs
	##################################
	# RETURNS None (modifies 'self' in-place.)
	def merge(self, lg2, ncombfn, ecombfn):
		"""New node/edge labels are added from lg2 with common primitives. The
	   value for common node/edge labels updated using ncombfn and
	   ecombfn respectiveley: each function is applied to current values to
	   obtain the new value (i.e. v1' = fn(v1,v2))."""

		# Deal with non-common primitives/nodes.
		# DEBUG: make sure that all absent edges are treated as
		# 'hard' decisions (i.e. label ('_',1.0))
		self.matchAbsent(lg2)
		#self.labelMissingEdges()

		# Merge node and edgelabels.
		mergeMaps(self.nlabels, self.gweight, lg2.nlabels, lg2.gweight, \
				ncombfn)
		mergeMaps(self.elabels, self.gweight, lg2.elabels, lg2.gweight,\
				ecombfn)

				
	# RETURNS None: modifies in-place.
	def addWeightedLabelValues(self,lg2):
		"""Merge two graphs, adding the values for each node/edge label."""
		def addValues( v1, w1, v2, w2 ):
			return w1 * v1 + w2 * v2
		self.merge(lg2, addValues, addValues)
	
	# RETURNS None: modifies in-place.
	# HM: Added for IJDAR CROHME draft; invoke to filter a graph.
	# (currenly not used by default).
	def keepOnlyCorrectLab(self, gt):
		"""Keep only correct labels compared with the gt. Use the
		label ERROR_N and ERROR_E for node and edges errors. Use the 
		compareTools to compare the labels with ground truth."""
		
		allNodes = set(list(gt.nlabels)).union(list(self.nlabels))
		self.matchAbsent(gt)

		for nid in allNodes:
			(cost,_) = self.cmpNodes(list(self.nlabels[nid]),list(gt.nlabels[nid]))
			#if there is some error
			if cost > 0:
				self.nlabels[ nid ] = {'ERROR_N' : 1.0}
			else:
				self.nlabels[ nid ] = gt.nlabels[nid]

		for (graph,oGraph) in [ (self,gt), (gt,self) ]:
			for npair in list(graph.elabels):
				cost = 0;
				if not npair in oGraph.elabels:
					(cost,errL) = self.cmpEdges(list(graph.elabels[npair]),['_'])
				else:
					(cost,errL) = self.cmpEdges(list(graph.elabels[npair]),list(oGraph.elabels[npair]))
				if cost > 0:
					self.elabels[ npair ] = {'ERROR_E' : 1.0}
				else:
					if npair in gt.elabels:
						self.elabels[ npair ] = gt.elabels[npair]
					else:
						self.elabels[ npair ] =  {'_' : 1.0}

	# RETURNS None: modifies in-place.
	def selectMaxLabels(self):
		"""Filter for labels with maximum confidence. NOTE: this will
		keep all maximum value labels found in each map, e.g. if two
		classifications have the same likelihood for a node."""
		for object in list(self.nlabels):
			max = -1.0
			maxPairs = {}
			for (label, value) in self.nlabels[object].items():
				if value > max:
					max = value
					maxPairs = { label : value }
				elif value == max:
					maxPairs[label] = value

			self.nlabels[ object ] = maxPairs

		for edge in list(self.elabels):
			max = -1.0
			maxPairs = {}
			for (label, value) in self.elabels[edge].items():
				if value > max:
					max = value
					maxPairs = { label : value }
				elif value == max:
					maxPairs[label] = value

			self.elabels[ edge ] = maxPairs
	
	# RETURNS NONE: modifies in-place.
	def invertValues(self):
		"""Substract all node and edge label values from 1.0, to 
		invert the values. Attempting to invert a value outside [0,1] will
		set the error flag on the object."""
		for node in list(self.nlabels):
			for label in self.nlabels[ node ]:
				currentValue = self.nlabels[ node ][ label ] 
				if currentValue < 0.0 or currentValue > 1.0:
					sys.stderr.write('\n  !! Attempted to invert node: ' \
							+ node + ' label \"' \
							+ label + '\" with value ' + str(currentValue) + '\n')
					self.error = True
				else:
					self.nlabels[ node ][ label ] = 1.0 - currentValue

		for edge in list(self.elabels):
			for label in self.elabels[ edge ]:
				currentValue = self.elabels[ edge ][ label ]
				if currentValue < 0.0 or currentValue > 1.0:
					sys.stderr.write('\n  !! Attempted to invert edge: ' + \
							str(edge) + ' label \"' \
							+ label + '\" with value ' + str(currentValue) + '\n')
					self.error = True
				else:
					self.elabels[ edge ][ label ] = 1.0 - currentValue

	def subStructIterator(self, nodeNumbers):
		""" Return an iterator which gives all substructures with n nodes
		n belonging to the list depths"""
		if(isinstance(nodeNumbers, int)):
			nodeNumbers = [nodeNumbers]
		subStruct = []
		
		# Init the substruct with isolated nodes
		for n in list(self.nlabels):
			subStruct.append(set([n]))
			if 1 in nodeNumbers:
				yield smallGraph.SmallGraph([(n, "".join(list(self.nlabels[n])))], [])
		
		for d in range(2,max(nodeNumbers)+1):
			#add one node to each substructure
			newSubsS = set([])
			newSubsL = []
			for sub in subStruct:
				le = getEdgesToNeighbours(sub,list(self.elabels))
				for (f,to) in le:
					new = sub.union([to])
					lnew = list(new)
					lnew.sort()
					snew = ",".join(lnew)
					
					if(not snew in newSubsS):
						newSubsS.add(snew)
						newSubsL.append(new)
						if d in nodeNumbers:
							yield self.getSubSmallGraph(new)
			
			# ??? BUG ???
			subStruct = newSubsL
			
	def getSubSmallGraph(self, nodelist):
		"""Return the small graph with the primitives in nodelist and all edges 
		between them. The used label is the merged list of labels from nodes/edges"""
		sg = smallGraph.SmallGraph()
		for n in nodelist:
			sg.nodes[n] = list(self.nlabels[n])
		for e in getEdgesBetweenThem(nodelist,list(self.elabels)):
			sg.edges[e] = list(self.elabels[e])
		return sg
		
	# Compare the substructure
	def compareSubStruct(self, olg, depths):
		"""Return the list of couple of substructure which disagree
		the substructure from self are used as references"""
		allerrors = []
		for struc in olg.subStructIterator(depths):
				sg1 = self.getSubSmallGraph(list(struc.nodes))
				if(not (struc == sg1)):		
					allerrors.append((struc,sg1))
		return allerrors
	
	def compareSegmentsStruct(self, lgGT,depths):
		"""Compute the number of differing segments, and record disagreements
		in a list. 
		The primitives in each subgraph should be of the same number and names
		(identifiers). Nodes are merged that have identical (label,value) pairs
		on nodes and all identical incoming and outgoing edges.  If used for
		classification evaluation, the ground-truth should be lgGT.  The first
		key value of the matrix is the lgGT obj structure, which gives the
		structure of the corresponding primitives which is the key to get the
		error structure in self.""" 
		(sp1, ps1, _, sre1) = self.segmentGraph()
		(spGT, psGT, _, sreGT) = lgGT.segmentGraph()

		segDiffs = set()
		correctSegments = set()
		for primitive in list(psGT):
			# Make sure to skip primitives that were missing ('ABSENT'),
			# as in that case the graphs disagree on all non-identical node
			# pairs for this primitive, and captured in self.absentEdges.

			# RZ: Assuming one level of structure here; modifying for
			#     new data structures accomodating multiple structural levels.
			obj1Id = ps1[primitive][ list(ps1[primitive])[0] ]
			obj2Id = psGT[primitive][ list(psGT[primitive])[0] ]

			if not 'ABSENT' in self.nlabels[primitive] and \
					not 'ABSENT' in lgGT.nlabels[primitive]:
				# Obtain sets of primitives sharing a segment for the current
				# primitive for both graphs.
				# Each of sp1/spGT are a map of ( {prim_set}, label ) pairs.

				segPrimSet1 = sp1[ obj1Id ][0]
				segPrimSet2 = spGT[ obj2Id ][0]
				
				# Only create an entry where there are disagreements.
				if segPrimSet1 != segPrimSet2:
					segDiffs.add( ( obj2Id, obj1Id) )
				else:
					correctSegments.add( obj2Id )
			
			# DEBUG: don't record differences for a single node.
			elif len(list(self.nlabels)) > 1:
				# If node was missing in this graph or the other, treat 
				# this graph as having a missing segment
				# do not count the segment in graph with 1 primitive
				segDiffs.add(( obj2Id, obj1Id ) )

		# now check if the labels are identical
		for seg in correctSegments:
			# Get label for the first primtives (all primitives have identical
			# labels in a segment).
			# DEBUG: use only the set of labels, not confidence values.
			firstPrim = list(spGT[seg][0])[0]
			(cost, diff) = self.cmpNodes(list(self.nlabels[ firstPrim ]),list(lgGT.nlabels[ firstPrim ]))

			segId1 = ps1[firstPrim][ list(ps1[ firstPrim ])[0] ]
			segId2 = psGT[firstPrim][ list(psGT[ firstPrim ])[0] ]
			
			if (0,[]) != (cost, diff):
				segDiffs.add(( segId2, segId1) )
		allSegWithErr = set([p for (p,_) in segDiffs])
		
		# start to build the LG at the object level
		# add nodes for object with the labels from the first prim
		lgObj = Lg()
		for (sid,lprim) in spGT.iteritems():
			lgObj.nlabels[sid] = lgGT.nlabels[list(lprim[0])[0]]

		# Compute the specific 'segment-level' graph edges that disagree, at the
		# level of primitive-pairs. This means that invalid segmentations may
		# still have valid layouts in some cases.
		# Add also the edges in the smallGraph
		segEdgeErr = set()
		for thisPair in list(sreGT):
			# TODO : check if it is sp1[thisPair[0]] instead of sp1[thisPair[0]][0]
			thisParentIds = set(spGT[ thisPair[0] ][0])
			thisChildIds = set(spGT[thisPair[1] ][0])
			lgObj.elabels[thisPair] = lgGT.elabels[ (list(thisParentIds)[0], list(thisChildIds)[0])]
			
			# A 'correct' edge has the same label between all primitives
			# in the two segments.
			# NOTE: we are not checking the consitency of label in each graph
			#  ie if all labels from thisParentIds to thisChildIds in self are 
			# the same 
			for parentId in thisParentIds:
				for childId in thisChildIds:
					# DEBUG: compare only label sets, not values.
					if not (parentId, childId) in list(self.elabels) or \
					   (0,[]) != self.cmpEdges(list(self.elabels[ (parentId, childId) ]), list(lgGT.elabels[ (parentId, childId) ])):
						segEdgeErr.add(thisPair)
						continue
		
		listOfAllError = []
		for smg in lgObj.subStructIterator(depths):
			#if one segment is in the segment error set
			showIt = False
			if len(set(list(smg.nodes)).intersection(allSegWithErr)) > 0:
				showIt = True
			for pair in list(smg.edges):
				if pair in segEdgeErr:
					showIt = True
					continue
			if showIt:
				#build the smg for the prim from lgGT
				allPrim = []
				for s in list(smg.nodes):
					allPrim.extend(spGT[s][0])
				
				smgPrim1 = self.getSubSmallGraph(allPrim)
				smgPrimGT = lgGT.getSubSmallGraph(allPrim)
				listOfAllError.append((smg,smgPrimGT,smgPrim1))
		
		return listOfAllError 

################################################################
# Utility functions
################################################################
def mergeLabelLists(llist1, weight1, llist2, weight2, combfn):
	"""Combine values in two label lists according to the passed combfn
	function, and passed weights for each label list."""
	# Combine values for each label in lg2 already in self.
	allLabels = set(llist1.items())\
			.union(set(llist2.items()))
	# have to test whether labels exist
	# in one or both list.
	for (label, value) in allLabels:
		if label in list(llist1) and \
				label in list(llist2):
			llist1[ label ] = \
				combfn( llist1[label], weight1,\
						llist2[label], weight2 )
		elif label in list(llist2):
			llist1[ label ] = \
				weight2 * llist2[label]
		else:
			llist1[ label ] = \
				weight1 * llist1[label]


def mergeMaps(map1, weight1, map2, weight2, combfn):
	"""Combine values in two maps according to the passed combfn
	function, and passed weights for each map."""
	# Odds are good that there are built-in function for this
	# operation.
	objects1 = list(map1)
	objects2 = list(map2)
	allObjects = set(objects1).union(set(objects2))
	for object in allObjects:
		if object in objects1 and object in objects2:
			# Combine values for each label in lg2 already in self.
			mergeLabelLists(map1[object],weight1, map2[object], weight2, combfn )			
		# DEBUG: no relationship ('missing') edges should
		# be taken as certain (value 1.0 * weight) where not explicit.
		elif object in objects2:
			# Use copy to avoid aliasing problems.
			# Use appropriate weight to update value.
			map1[ object ] = copy.deepcopy( map2[ object ] )
			for (label, value) in map1[object].items():
				map1[object][label] = weight2 * value
			map1[object]['_'] = weight1 
		else:
			# Only in current map: weight value appropriately.
			for (label, value) in map1[object].items():
				map1[object][label] = weight1 * value
			map1[object]['_'] = weight2 


def getEdgesToNeighbours(nodes,edges):
	"""return all edges which are coming from one of the nodes to out of these nodes"""
	neigb = set([])
	for (n1,n2) in edges:
		if (n1 in nodes and not n2 in nodes):
			neigb.add((n1,n2))
	return neigb

def getEdgesBetweenThem(nodes,edges):
	"""return all edges which are coming from one of the nodes to out of these nodes"""
	edg = set([])
	for (n1,n2) in edges:
		if (n1 in nodes and n2 in nodes):
			edg.add((n1,n2))
	return edg
