################################################################
# sumDiff.py
#
# Program that reads in a .diff (CSV) file containing differences between
# to BG, and outputs confusion matrix for symbols and spatial relations.
# Output is in CSV or HTML formats.
# 
# Author: H. Mouchere, June 2012
# Copyright (c) 2012-2014, Richard Zanibbi and Harold Mouchere
################################################################
import sys
import csv
import collections
import time
import os

def addOneError(confM, id1, id2):
        #thanks to "defaultdict" there is nothing to do !
        confM[id1][id2] += 1

def affMat(output, allID, confM):
        # Header
        output.write("Output:")
        for k in sorted(allID):
               output.write(",'"+str(k)+"'")
        output.write("\n")
        
        # Data
        for k1 in sorted(allID):
                output.write("'"+str(k1)+"'")
                for k2 in sorted(allID):
                        if not confM[k1][k2] == 0:
                                output.write(","+str(confM[k1][k2]))
                        else:
                                output.write(",")
                output.write("\n")

def affMatHTML(output, allID, confM):
        output.write("<table>\n<tr><th><i>(Out:Rows)</i></th>")
        for k in sorted(allID):
                output.write("<th>"+str(k)+"</th>")
        output.write("</tr>\n")
        for k1 in sorted(allID):
                output.write("<tr><th>"+str(k1)+"</th>")
                i = 0
                for k2 in sorted(allID):
                        val = str(confM[k1][k2])
                        if val == "0":
                                val = ""
                        output.write('<td class="col_'+str(i)+'">'+val+"</td>")
                        i = i+1
                output.write("<th>"+str(k1)+"</th></tr>\n")
        output.write("<tr><th></th>")
        for k in sorted(allID):
                output.write("<th>"+str(k)+"</th>")
        output.write("</tr>\n")                
        output.write("</table>\n")

def writeCSS(output, allID):
        output.write('<head><style type="text/css">\n')
        output.write('table { border-collapse:collapse;}\n')
        output.write('p { line-height: 125%;}\n')
        output.write('ul { line-height: 125%;}\n')
        output.write('th{ text-align: right; padding: 4px;}\n')
        output.write('td { text-align: right; border: 1px solid lightgray; padding: 4px; }\n')
        
        #output.write('h2 {        color: red;}\n')
        output.write('tr:hover{background-color:rgb(180,200,235);}\n ')
        #i = 0
        #for k1 in sorted(allID):
        #        output.write('td.col_'+str(i)+':hover {\nbackground-color:rgb(100,100,255);\n}\n')
        #        i = i+1
        output.write('td:hover{background-color:yellow;} \n')
        output.write('</style></head>\n')

def main():
        if len(sys.argv) < 3:
                print("Usage : [[python]] sumDiff.py <file1.diff> <labelsGT.txt> [HTML]\n")
                print("        Merge results for each line in file1.diff into confusion Matrices.")
                print("        By default output is sent to stdout in CSV format.")
                print(" requires list of GT labels from labelsGT.txt.")
                print("        [HTML] option changes output format to HTML.")
                sys.exit(0)
        # Read data from CSV file.
        fileName = sys.argv[1]
        labelFile = sys.argv[2]
        try:
                fileReader = csv.reader(open(fileName))
        except:
                sys.stderr.write('  !! IO Error (cannot open): ' + fileName)
                sys.exit(1)

        try:
                labelfileReader = csv.reader(open(labelFile))
        except:
                sys.stderr.write('  !! IO Error (cannot open): ' + fileName)
                sys.exit(1)

        # Read for node and edge label sets.
        readEdges = False
        gtNodeLabels = set()
        gtEdgeLabels = set()
        for row in labelfileReader:
                if len(row) == 0:
                        continue
                
                nextEntry = row[0].strip()
                if nextEntry == 'NODE LABELS:':
                        continue
                elif nextEntry == 'EDGE LABELS:':
                        readEdges = True
                else:
                        if readEdges:
                                gtEdgeLabels.add(nextEntry)
                        else:
                                gtNodeLabels.add(nextEntry)

        withHTML = False
        if len(sys.argv) > 3:
                withHTML = True
        #confusion matrix = dict->dict->int
        labelM = collections.defaultdict(collections.defaultdict(int).copy)
        spatRelM = collections.defaultdict(collections.defaultdict(int).copy)
        #segRelM = collections.defaultdict(collections.defaultdict(int).copy)
        
        allLabel = set()
        allSR = set()
        rowCount = -1

        # Idenfity all confused symbol labels. We will use this to
        # present relationship and segmentation confusions separately.
        symbolLabels = set([])

        nodeErrors = 0
        allSegErrors = 0
        allRelErrors = 0
        fposMerge = 0
        fnegMerge = 0

        for row in fileReader:
                rowCount += 1

                # Skip blank lines.
                if len(row) == 0:
                        continue

                entryType = row[0].strip()
                #skip file names
                if entryType == "DIFF":
                        continue
                #process node label errors
                elif entryType == "*N":
                        # Capture all confused symbol (node) labels.
                        symbolLabels.add(row[2].strip())
                        symbolLabels.add(row[5].strip())

                        addOneError(labelM,row[2].strip(),row[5].strip())
                        allLabel.add(row[2].strip())
                        allLabel.add(row[5].strip())

                        nodeErrors += 1

                #process link errors
                elif entryType == "*E":
                        # DEBUG
                        if row[3].strip() == "1.0" or row[6].strip() == "1.0":
                                print("ERROR at row: " + str(rowCount) + " for file: " + fileName)
                                print(row)
                        elif not len(row) == 8:
                                print("INVALID LENGTH at row: " + str(rowCount) + " for file: " + fileName)
                                print(row)
                        
                        outputLabel = row[3].strip()
                        otherLabel = row[6].strip()
                        addOneError(spatRelM, outputLabel, otherLabel)

                        allSR.add(outputLabel)
                        allSR.add(otherLabel)

                elif entryType == "*S":
                        # Currently ignore segmentation errors (i.e. object-level errors)
                        continue
                
        # Obtain the list of edge labels that do not appear on nodes.
        # DEBUG: need to consult all GT labels in general case (handling '*' input).
        mergeEdgeLabel = '*'
        relOnlyLabels = allSR.difference(symbolLabels).difference(gtNodeLabels)
        relMergeLabels = relOnlyLabels.union(mergeEdgeLabel)

        # Create a modified confusion histogram where all symbol/segmentation
        # edge confusions are treated as being of the same type.
        ShortEdgeMatrix = collections.defaultdict(collections.defaultdict(int).copy)
        for output in list(spatRelM):
                olabel = output
                if not output in relOnlyLabels:
                        olabel = mergeEdgeLabel

                for target in list(spatRelM[output]):
                        tlabel = target
                        if not target in relOnlyLabels:
                                tlabel = mergeEdgeLabel

                        # Increment the entry for the appropriate matrix.
                        ShortEdgeMatrix[olabel][tlabel] += spatRelM[output][target]

                        if not olabel == output or not tlabel == target:
                                allSegErrors += spatRelM[output][target]
                                if not olabel == output and tlabel == target:
                                        fposMerge += spatRelM[output][target]
                                elif not tlabel == target and olabel == output:
                                        fnegMerge += spatRelM[output][target]
                        else:
                                allRelErrors += spatRelM[output][target]

        if withHTML:
                sys.stdout.write('<html>')
                writeCSS(sys.stdout, allLabel.union(allSR))
                print("<font face=\"helvetica,arial,sans-serif\">")
                print("<h2>LgEval Error Summary</h2>")
                print(time.strftime("%c"))
                print("<br>\n")
                print("<b>File:</b> " + os.path.splitext( os.path.split(fileName)[1] )[0] + "<br>")
                print("<p>All confusion matrices show only errors. In each matrix, output labels appear in the left column, and target labels in the top row.</p>")
                print("<UL><LI><A href=\"#nodes\">Node Label Confusion Matrix</A> <LI> <A HREF=\"#ShortEdges\">Edge Label Confusion Matrix (short - ignoring object class confusions)<A> <LI> <A HREF=\"#Edges\">Edge Label Matrix (all labels)</A> </UL>")
                print ("<hr>")
                print ("<h2><A NAME=\"nodes\">Node Label Confusion Matrix</A></h2>")
                print ("<p>"+str(len(allLabel)) + " unique node labels. " + str(nodeErrors) + " errors. ABSENT: a node missing in the output or target graph</p>")
                affMatHTML(sys.stdout, allLabel, labelM)
                print("<br><hr><br>")
                print ("<h2><A NAME=\"ShortEdges\">Edge Label Confusion Matrix (Short)</A></h2>")
                print ("<p>" + str(len(relOnlyLabels)) + " unique relationship labels + * representing grouping two nodes into an object (any type). " + str(allSegErrors + allRelErrors) + " errors <UL><LI>" + str(allSegErrors) + " Directed segmentation and node pair classification errors (entries in '*'-labeled row and column) <UL><LI><b>" + str(allSegErrors - fposMerge - fnegMerge) + " edges between correctly grouped nodes, but with conflicting classification (* vs. *)</b> <LI>" + str(fposMerge) + " false positive merge edges (* vs. other)<LI>" + str(fnegMerge) + " false negative merge edges (other vs. *) </UL>  <LI>" + str(allRelErrors) + " Directed relationship errors (remaining matrix entries) </UL></p></p>")
                affMatHTML(sys.stdout, relMergeLabels, ShortEdgeMatrix)
                #affMatHTML(sys.stdout, relOnlyLabels, spatRelM)
                
                print("<br><hr><br>")
                print("<h2><A NAME=\"Edges\">Edge Label Confusion Matrix (All Errors)</A></h2>")
                print("<p>"+str(len(allSR)) + " unique edge labels representing relationships and node groupings for specific symbol types. " + str(allSegErrors + allRelErrors) + " errors</p>")
                affMatHTML(sys.stdout, allSR, spatRelM)
                
                print("</font>")
                sys.stdout.write('</html>')
        else:
                print("LgEval Error Summary for: "+fileName)
                print(time.strftime("%c"))
                print("")
                print("NOTE: This file contains 3 confusion matrices.")
                print("")
                print("I. Node Label Confusion Matrix: " + str(len(allLabel)) + " unique labels. ABSENT: a node missing in the output or target graph")
                affMat(sys.stdout, allLabel, labelM)
                
                print("")
                print("")
                print("II. Edge Label Confusion Matrix (Short): " + str(len(relOnlyLabels)) + " unique relationship labels + * (merge)")
                affMat(sys.stdout, relMergeLabels, ShortEdgeMatrix)
                
                print("")
                print("")
                print("III. Edge Label Confusion Matrix (Full): " + str(len(allSR)) + " unique labels for relationships and node groupings for specific symbol types")
                affMat(sys.stdout, allSR, spatRelM)

main()
