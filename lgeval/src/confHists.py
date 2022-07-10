################################################################
# confHists.py
#
# Create confusion histograms.
#
# Author: R. Zanibbi, Oct. 2014
# Copyright (c) 2014 Richard Zanibbi and Harold Mouchere
################################################################

import sys
import csv
import time
import os

from lg import *
from lgio import *
import SmGrConfMatrix
import compareTools

def main(fileList, minCount, confMat, confMatObj, subgraphSize):
	fileReader = csv.reader(open(fileList), delimiter=' ')
	htmlStream = None
	
	matrix = SmGrConfMatrix.ConfMatrix()
	matrixObj = SmGrConfMatrix.ConfMatrixObject()

	for row in fileReader:
		# Skip comments and empty lines.
		if not row == [] and not row[0].strip()[0] == "#":
			#print(row)
			lgfile1 = row[0].strip() # remove leading/trailing whitespace
			lgfile2 = row[1].strip()
			
			# Here lg1 is input; lg2 is ground truth/comparison
			lg1 = Lg(lgfile1)
			lg2 = Lg(lgfile2)
			out = lg1.compare(lg2)
			
			nodeClassErr = set()
			edgeErr = set()
			if confMat or confMatObj:
				for (n,_,_) in out[1] :
					nodeClassErr.add(n)
				for (e,_,_) in out[2] :
					edgeErr.add(e)
			
			(head, tail) = os.path.split(lgfile1)
			(base, _) = os.path.splitext(tail)
			fileName = base + ".lg"
			if confMat:
				# Subgraphs of 2 or 3 primitives.
				for (gt,er) in lg1.compareSubStruct(lg2,[subgraphSize]):
					er.rednodes = set(list(er.nodes)) & nodeClassErr
					er.rededges = set(list(er.edges)) & edgeErr
					matrix.incr(gt,er,fileName)
			if confMatObj:
				# Object subgraphs of 2 objects.
				for (obj,gt,er) in lg1.compareSegmentsStruct(lg2,[subgraphSize]):
					er.rednodes = set(list(er.nodes)) & nodeClassErr
					er.rededges = set(list(er.edges)) & edgeErr
					matrixObj.incr(obj,gt,er,fileName)
                        
        htmlStream = None
	
	objTargets = matrixObj.size()
	primTargets = matrix.size()

	# HTML header output
	htmlStream = open('CH_' + fileList + '.html','w')
	htmlStream.write('<meta charset="UTF-8">\n<html xmlns="http://www.w3.org/1999/xhtml">')
	htmlStream.write('<head>')

        # Code to support 'select all' checkboxes
        # Essentially registering callback functions to checkbox click events.
        # Make sure to include JQuery (using version 2.1.1 for now)
        htmlStream.write('<script src="http://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>')
        htmlStream.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/1.0.0/FileSaver.min.js"></script>')
        
        # (Excuse the messs..) create callbacks for checkbox events, save button 
        # which saves the unique list of selected files in sorted order.
        # This was a slow, painful way to do this - perhaps an 'include' would be better.
        htmlStream.write(
        '<SCRIPT language="javascript">\
            $(function(){ \
            $("#savebutton").click(function () { \
               var output = ""; \
               var selections = $(".fileCheck:checked"); \
               var fileString = ""; \
               for (i=0; i < selections.length; i++) { \
                    fileString = selections[i].value.concat(" ").concat(fileString); \
					console.log(fileString); \
                } \
			   fileList = fileString.split(" "); \
               fileList.sort(); \
               var uniqueSels = []; \
               var last = ""; \
               for (i=0; i < fileList.length; i++) { \
                 if (fileList[i] != last) { \
                    uniqueSels.push( fileList[i]); \
                    last = fileList[i]; \
                 } \
                } \
               output = uniqueSels.join("\\n"); \
               var blob = new Blob([ output ], {type: "text/plain;charset=utf-8"}); \
               saveAs(blob, "selectedFiles.txt"); \
            }); \
            $(":checkbox").click(function () { \
				var current = this.id; \
				var re = new RegExp(this.id + "[0-9]","i"); \
				var elementsCommonIdPrefix = $("[id^=" + this.id + "]").filter(function() { \
				        return current == "Obj" || ! this.id.match(re); }); \
				console.log(this.id + " Matched: " + elementsCommonIdPrefix.length); \
				var parentId = this.id.match(/[a-zA-Z]+[0-9]+[a-zA-Z]+[0-9]+/); \
				var grandparentId = this.id.match(/[a-zA-Z]+[0-9]+/); \
				if ( ! this.checked ) { \
				    elementsCommonIdPrefix.prop("checked",false); \
				    if (parentId != null ) \
				        $("[id=" + parentId + "]").prop("checked", false); \
				    if (grandparentId != null) \
					    $("[id=" + grandparentId + "]").prop("checked", false); \
				    if ($("[id=Obj]") != null) \
					    $("[id=Obj]").prop("checked", false); \
	            } else { \
				    elementsCommonIdPrefix.prop("checked", true); \
				    var pDescendents = $("[id^=" + parentId + "]"); \
		    		var pDescChecked = $("[id^=" + parentId + "]:checked"); \
				    if (parentId != null && pDescendents.length == pDescChecked.length + 1 ) \
					    $("[id=" + parentId + "]").prop("checked", true); \
				    var gDescendents = $("[id^=" + grandparentId + "]"); \
					var gDescChecked = $("[id^=" + grandparentId + "]:checked"); \
					if (grandparentId != null && gDescendents.length == gDescChecked.length + 1 ) \
					    $("[id=" + grandparentId + "]").prop("checked", true); \
					var aDescendents = $("[id^=Obj]"); \
					var aDescChecked = $("[id^=Obj]:checked"); \
					if ($("[id=Obj]") != null && aDescendents.length == aDescChecked.length + 1 ) \
					    $("[id=Obj]").prop("checked", true); \
				} \
			}); \
        }); \
        </SCRIPT>\n')	
        
	# Style
	htmlStream.write('<style type="text/css">\n')
        htmlStream.write('svg { overflow: visible; }\n')
	htmlStream.write('p { line-height: 125%; }\n')
	htmlStream.write('li { line-height: 125%; }\n')
        htmlStream.write('button { font-size: 12pt; }\n')
	htmlStream.write('td { font-size: 10pt; align: left; text-align: left; border: 1px solid lightgray; padding: 5px; }\n')
	htmlStream.write('th { font-size: 10pt; font-weight: normal; border: 1px solid lightgray; padding: 10px; background-color: lavender; text-align: left }\n')
	htmlStream.write('tr { padding: 4px; }\n')
	htmlStream.write('table { border-collapse:collapse;}\n')
	htmlStream.write('</style></head>\n\n')
	htmlStream.write("<font face=\"helvetica,arial,sans-serif\">")
	
	htmlStream.write("<h2>LgEval Structure Confusion Histograms</h2>")
	htmlStream.write(time.strftime("%c"))
	htmlStream.write('<p><b>'+ fileList + '</b><br>')
	htmlStream.write('<b>Subgraphs:</b> ' + str(subgraphSize) + ' node(s)<br>')
	htmlStream.write('<br>')
	htmlStream.write('<p><b>Note:</b> Only primitive-level graph confusions occurring at least '+str(minCount)+' times appear below.<br><Note:</b><b>Note:</b> Individual primitive errors may appear in multiple error graphs (e.g. due to segmentation errors).</p>')
	htmlStream.write('<UL>')

	if (confMatObj):
		htmlStream.write('<LI><A HREF=\"#Obj\">Object histograms</A> (' + str(objTargets) + ' incorrect targets; ' + str(matrixObj.errorCount()) + ' errors)')
	if (confMat):
		htmlStream.write('<LI><A HREF=\"#Prim\">Primitive histograms</A> (' + str(primTargets) + ' incorrect targets; ' + str(matrix.errorCount()) + ' errors)')
	htmlStream.write('</UL>')
	
	htmlStream.write('<button type="button" font-size="12pt" id="savebutton">&nbsp;&nbsp;Save Selected Files&nbsp;&nbsp;</button>')
	htmlStream.write('\n<hr>\n')
        
	if confMatObj:
		htmlStream.write('<h2><A NAME=\"#Obj\">Object Confusion Histograms</A></h2>')
		htmlStream.write('<p>\n')
		htmlStream.write('Object structures recognized incorrectly are shown at left, sorted by decreasing frequency. ' + str(objTargets) + ' incorrect targets, ' + str(matrixObj.errorCount()) + ' errors.')
		htmlStream.write('</p>\n')
		matrixObj.toHTML(htmlStream,minCount,"")
	
	if confMat:
		htmlStream.write("<hr>\n")
		htmlStream.write('<h2><A NAME=\"Prim\">Primitive Confusion Histograms</A></h2>')
		htmlStream.write('<p>Primitive structure recognizes incorrectly are shown at left, sorted by decreasing frequency. ' + str(primTargets) + ' incorrect targets, ' + str(matrix.errorCount()) + ' errors.</p>')

		# Enforce the given limit for all reported errors for primitives.
                matrix.toHTML(htmlStream,minCount,minCount,"")
	
		
	htmlStream.write('</html>')
	htmlStream.close()
		
# (RZ) Lazy - not checking arguments on assumption this is called from the
# strConfHist script.
minCount = 1
fileList = sys.argv[1]
subgraphSize = int(sys.argv[2])
if len(sys.argv) > 3:
	minCount = int(sys.argv[3])

confMatObj = True
confMat = True if len(sys.argv) > 4 else False 

main(fileList, minCount, confMat, confMatObj, subgraphSize)
