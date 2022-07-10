################################################################
# compareTools.py
#
# Defines how nodes and edges are compared.
# Usable by other packages such as smallGraph
#
# Author: H. Mouchere, Oct. 2013
# Copyright (c) 2013-2014 Richard Zanibbi and Harold Mouchere
################################################################

def generateListErr(ab,ba):
	listErr = []
	if len(ab) == 0:
		ab = ['_']
	if len(ba) == 0:
		ba = ['_']
	for c1 in ab:
		for c2 in ba:
			listErr.append((c1,c2))
	return listErr

def defaultMetric(labelList1, labelList2):
	#new way but with 1 label per node
	diff =  set(labelList1) ^ (set(labelList2)) # symetric diff
	if len(diff) == 0:
		return (0,[])
	else:
		ab = diff&set(labelList1)
		ba = diff&set(labelList2)
		cost = max(len(ab),len(ba) )
		return (cost,generateListErr(ab,ba))


synonym = {'X':'x','\\times':'x', 'P':'p', 'O':'o','C':'c', '\\prime':'COMMA'}
def synonymMetric(labelList1, labelList2):
	def replace(x):
		if x in list(synonym):
			return synonym[x]
		else:
			return x
	a = map(replace, labelList1)
	b = map(replace, labelList2)
	diff =  set(a) ^ (set(b)) # symetric diff
	if len(diff) == 0:
		return (0,[])
	else:
		ab = diff&set(a)
		ba = diff&set(b)
		cost = max(len(ab),len(ba) )
		return (cost,generateListErr(ab,ba))

ignoredLabelSet = set([])
selectedLabelSet = set([])
def filteredMetric(labelList1, labelList2):
	labelS1 = set(labelList1) - ignoredLabelSet # removing the ignored labels
	labelS2 = set(labelList2) - ignoredLabelSet # removing the ignored labels
	if len(selectedLabelSet) > 0:
		labelS1 &= selectedLabelSet # keep only the selected labels
		labelS2 &= selectedLabelSet # keep only the selected labels
	return defaultMetric(labelS1,labelS2)

# no error if at least one symbol is OK
def intersectMetric(labelList1, labelList2):
#new way but with 1 label per node
	inter =  set(labelList1) & (set(labelList2)) # symetric diff
	if len(inter) > 0:
		return (0,[])
	else:
		ab = set(labelList1)-inter
		ba = set(labelList2)-inter
		return (1,generateListErr(ab,ba))
	
	
cmpNodes = defaultMetric
cmpEdges = defaultMetric
