#################################################################
# statlgdb.py
#
# Program to generate structure confusion histograms as .html
#
# Author: H. Mouchere, June 2013
# Copyright (c) 2013-2014 Richard Zanibbi and Harold Mouchere
################################################################


import sys
import csv
from lg import *
from lgio import *
import time
import SmGrConfMatrix

INKMLVIEWER="file://www.cs.rit.edu/~rlaz/inkml_viewer/index.xhtml?path=http://www.cs.rit.edu/~rlaz/testdata/&files="
MINERRTOSHOW = 1

def getObjStruct(strkLG):
	(sp, _, _, sre) = strkLG.segmentGraph()
	lgObj = Lg()
	for (sid,lprim) in sp.iteritems():
		lgObj.nlabels[sid] = strkLG.nlabels[list(lprim[0])[0]]

	for thisPair in list(sre):
		# TODO : check if it is sp1[thisPair[0]] instead of sp1[thisPair[0]][0]
		thisParentIds = set(sp[ thisPair[0] ][0])
		thisChildIds = set(sp[thisPair[1] ][0])
		lgObj.elabels[thisPair] = strkLG.elabels[ (list(thisParentIds)[0], list(thisChildIds)[0])]
	return lgObj	

def main():
	stat = SmGrConfMatrix.SmDict()
	statObj = SmGrConfMatrix.SmDict()
	listName = sys.argv[1]

	processStrokes = False;
	if len(sys.argv) > 2:
		processStrokes = True;
		print("Computing stroke and object confusion histograms.")

	print ("Computing histograms for files in: " + str(listName))
	fileReader = csv.reader(open(listName), delimiter=' ')
	for row in fileReader:
		# Skip comments and empty lines.
		if not row == [] and not row[0].strip()[0] == "#":
			lgfile = row[0].strip() # remove leading/trailing whitespace
			print (lgfile)
			lg = Lg(lgfile)

			# NOTE: list of integers is object neighborhood sizes
			for s in getObjStruct(lg).subStructIterator([2,3]):
				#print s
				statObj.get(s,SmGrConfMatrix.Counter).incr()

			#NOTE: List of integers are stroke neighborhood sizes
			# Only process strokes if explicitly asked to do so.
			if processStrokes:
				for s in lg.subStructIterator([2,3]):
					stat.get(s,SmGrConfMatrix.Counter).incr()
			
	out=open('CH_' + listName + '.html', 'w')
	out.write('<html xmlns="http://www.w3.org/1999/xhtml">')
	
	# Style
	out.write('<head><style type="text/css">\n')
	out.write('</style></head>\n\n')
	out.write("<font face=\"helvetica,arial,sans-serif\">")
	
	out.write("<h1>LgEval Structure Confusion Histograms</h1>")
	out.write("\n<b>" + str(listName) + "</b><br>")
	out.write(time.strftime("%c"))
	out.write('')
	out.write('<UL><LI><A HREF="#Object">Object confusion histograms</A></LI><LI><A HREF=\"#Stroke\"></UL>')
	
	out.write('<h2><A NAME=\"#Object\">Object Subgraph Confusion Histograms</A></h2>')
	out.write(statObj.toHTML(MINERRTOSHOW))
	
	if (processStrokes):
		out.write('<h2><A NAME=\"#Stroke\">Stroke Subgraph Confusion Histograms</A></h2>')
		out.write(stat.toHTML(MINERRTOSHOW))
	
	out.write('</font>')
	out.write('</html>')
	out.close()
	
main()
