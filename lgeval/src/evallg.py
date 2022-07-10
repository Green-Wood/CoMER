################################################################
# evallg.py
#
# Program that reads in two .lg (CSV) files, computes metrics,
# and returns the result as a (CSV) entry, along with a
# CSV entry (row) for each specific error on standard output.
#
# *If run in 'batch' mode, a CSV file for errors and a separate
# file containing all errors observed will be produced.
#
# Author: R. Zanibbi, June 2012
# Copyright (c) 2012-2014 Richard Zanibbi and Harold Mouchere
################################################################
import sys
import csv
from lg import *
from lgio import *
import SmGrConfMatrix
import compareTools

# for RIT web service :
#INKMLVIEWER = "inkml_viewer/index.xhtml?path=../testdata/&files="
#local :
INKMLVIEWER = "http://www.cs.rit.edu/~rlaz/inkml_viewer/index.xhtml?path=http://www.cs.rit.edu/~rlaz/testdata/&files="
MINERRTOSHOW = 3

def runBatch(fileName, defaultFileOrder, confMat, confMatObj):
	"""Compile metrics for pairs of files provided in a CSV
	file. Store metrics and errors in separate files."""
	fileReader = csv.reader(open(fileName))
	metricStream = open(fileName + '.m','w')
	diffStream = open(fileName + '.diff','w')

	htmlStream = None
	matrix = None
	matrixObj = None
	if confMat:
		matrix = SmGrConfMatrix.ConfMatrix()
		if confMatObj:
			matrixObj = SmGrConfMatrix.ConfMatrixObject()

	for row in fileReader:
		# Skip comments and empty lines.
		if not row == [] and not row[0].strip()[0] == "#":
			lgfile1 = row[0].strip() # remove leading/trailing whitespace
			lgfile2 = row[1].strip()
			if not defaultFileOrder:
				temp = lgfile2
				lgfile2 = lgfile1
				lgfile1 = temp
			print ("Test: "+lgfile1+" vs. "+lgfile2);
			toShow = lgfile1
			if len(row)> 2:
				toShow = row[2].strip()
			# Here lg1 is the output, and lg2 the ground truth.
			lg1 = Lg(lgfile1)
			lg2 = Lg(lgfile2)
			out = lg1.compare(lg2)

			metricStream.write('*M,' + lgfile1 + ',' + lgfile2 + '\n')
			writeMetrics(out, metricStream)
			diffStream.write('DIFF,' + lgfile1 + ',' + lgfile2 + '\n')
			writeDiff(out[1], out[3], out[2], diffStream)
			
			nodeClassErr = set()
			edgeErr = set()
			if confMat or confMatObj:
				for (n,_,_) in out[1] :
					nodeClassErr.add(n)
				for (e,_,_) in out[2] :
					edgeErr.add(e)
			
			if confMat:
				for (gt,er) in lg1.compareSubStruct(lg2,[2,3]):
					er.rednodes = set(list(er.nodes)) & nodeClassErr
					er.rededges = set(list(er.edges)) & edgeErr
					matrix.incr(gt,er,toShow)
			if confMatObj:
				for (obj,gt,er) in lg1.compareSegmentsStruct(lg2,[2]):
					er.rednodes = set(list(er.nodes)) & nodeClassErr
					er.rededges = set(list(er.edges)) & edgeErr
					matrixObj.incr(obj,gt,er,toShow)
                        
		htmlStream = None
	if confMat or confMatObj:
		htmlStream = open(fileName + '.html','w')
		htmlStream.write('<html xmlns="http://www.w3.org/1999/xhtml">')
		htmlStream.write('<h1> File :'+fileName+'</h1>')
		htmlStream.write('<p>Only errors with at least '+str(MINERRTOSHOW)+' occurrences appear</p>')
	if confMat:
		htmlStream.write('<h2> Substructure Confusion Matrix </h2>')
		matrix.toHTML(htmlStream,MINERRTOSHOW,INKMLVIEWER)
	if confMatObj:
		htmlStream.write('<h2> Substructure Confusion Matrix at Object level </h2>')
		matrixObj.toHTML(htmlStream,MINERRTOSHOW,INKMLVIEWER)
	if confMat or confMatObj:
		htmlStream.write('</html>')
		htmlStream.close()
		
	metricStream.close()
	diffStream.close()
		
def main():
	if len(sys.argv) < 3:
		print("Usage: [[python]] evallg.py <file1.lg> <file2.lg> [diff/*]  [INTER]")
		print("   OR  [[python]] evallg.py <file1.lg> <file2.lg> MATRIX fileout")
		print("   OR  [[python]] evallg.py [batch] <filepair_list> [GT-FIRST] [MAT] [MATOBJ] [INTER]")
		print("")
		print("    For the first usage, return error metrics and differences")
		print("    for  label graphs in file1.lg and file2.lg.")
		print("    A third argument will return just differences ('diff')")
		print("    or just metrics (any other string). ")
		print("    If MATRIX option is used, 4 evaluations are done with the ")
		print("    different matrix label filters and output in the fileout[ABCD].m]")
		print("")
		print("    For the second usage, a file is provided containing pairs of")
		print("    label graph files, one per line (e.g. 'file1, GTruth').")
		print("    A third optional column contains the file name which should be")
		print("    linked to the InkML viewer.")
		print("")
		print("    A CSV file containing metrics for all comparisons is written")
		print("    to \"filepair_list.m\", and differences are written to a file")
		print("    \"filepair_list.diff\". By default ground truth is listed")
		print("    second on each line of the batch file; GT-FIRST as third argument")
		print("    will result in the first element of each line being treated")
		print("    as ground truth - this does not affect metrics (.m), but does")
		print("    affect difference (.diff) output.")
		print("")
		print("    The MAT or MATOBJ option will create a HTML file with confusion Matrix")
		print("    between substructures.")
		print("    MAT will produce the subtructure at stroke level.")
		print("    MATOBJ will produce the subtructure at object level.")
		print("     (in both cases, the size of substructure is 2 or 3 nodes,")
		print("      in both cases, only errors with at least 3 occurrences appear)")
		sys.exit(0)

	showErrors = True
	showMetrics = True
	
	if "INTER" in sys.argv:
		compareTools.cmpNodes = compareTools.intersectMetric;
		compareTools.cmpEdges = compareTools.intersectMetric;
	
	if sys.argv[1] == "batch":
		# If requested, swap arguments.
		defaultFileOrder = True
		confMat = False
		confMatObj = False
		if len(sys.argv) > 3 and "GT-FIRST" in sys.argv:
			print(">> Treating 1st column as ground truth.")
			defaultFileOrder = False
		if len(sys.argv) > 3 and "MAT" in sys.argv:
			print(">> Compute the confusion matrix at primitive level.")
			confMat = True
		if len(sys.argv) > 3 and "MATOBJ" in sys.argv:
			print(">> Compute the confusion matrix at object level.")
			confMatObj = True
		runBatch(sys.argv[2], defaultFileOrder, confMat, confMatObj)

	else:
		# Running for a pair of files: require default order of arguments.
		fileName1 = sys.argv[1]
		fileName2 = sys.argv[2]
		if len(sys.argv) > 4 and  sys.argv[3] == 'MATRIX':
			fileOut = sys.argv[4]
			#print ("MODE MATRIX : " + fileOut)
			todo = {'Mat':set(['*M']),'Col':set(['*C']),'Row':set(['*R']),'Cell':set(['*Cell'])}
			compareTools.cmpNodes = compareTools.filteredMetric
			compareTools.cmpEdges = compareTools.filteredMetric
			for (n,s) in todo.items():
				compareTools.selectedLabelSet = s
				n1 = Lg(fileName1)
				n2 = Lg(fileName2)
				out	= n1.compare(n2)
				outStream = open(fileOut+n+".m", 'w')
				writeMetrics(out, outStream)
				outStream.close()
			compareTools.selectedLabelSet = set([])
			compareTools.ignoredLabelSet = set(['*M','*C','*R','*Cell'])			
			n1 = Lg(fileName1)
			n2 = Lg(fileName2)
			out	= n1.compare(n2)
			outStream = open(fileOut+"Symb.m", 'w')
			writeMetrics(out, outStream)
			
		else:
			
			if 'diff' in sys.argv:
				showMetrics = False
			elif 'm' in sys.argv:
				showErrors = False
			n1 = Lg(fileName1)
			n2 = Lg(fileName2)
			
			if "INTER" in sys.argv:
				n1.labelMissingEdges()
				n2.labelMissingEdges()
			# print n1.csv()
			# print n2.csv()
				
			out = n1.compare(n2)

			if showMetrics:
				writeMetrics(out, sys.stdout)
			if showErrors:
				writeDiff(out[1],out[3],out[2], sys.stdout)

main()

