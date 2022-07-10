################################################################
# sumMetric.py
#
# Program that reads in a .m (CSV) file containing metrics,
# and outputs summary statistics and global performance metrics.
# 
# Author: H. Mouchere and R. Zanibbi, June 2012
# Copyright (c) 2012-2014, Richard Zanibbi and Harold Mouchere
################################################################
import sys
import csv
import math
import time
import os

def fmeasure(R,P):
        """Harmonic mean of recall and precision."""
        value = 0
        if R > 0 or P > 0:
                value = (2 * R * P)/(R+P)
        return value

def meanStdDev( valueList, scale ):
        """Compute the mean and standard deviation of a *non-empty* list of numbers."""
        numElements = len(valueList)
        if numElements == 0:
                return(None, 0.0)
        
        mean = float(sum(valueList)) / numElements
        variance = 0
        for value in valueList:
                variance += math.pow( value - mean, 2 )
        variance = variance / float(numElements)
        return (scale * mean, scale * math.sqrt(variance))
        
def weightedMeanStdDev( valueList, weights, scale ):
        """Compute the weighted mean and standard deviation of a *non-empty* list of numbers."""

        numElements = sum(weights)
        if len(valueList) < 1 or numElements == 0:
                return(None, 0.0)

        mean = 0
        for i in range(len(valueList)):
                mean += float(valueList[i]*weights[i])
        mean = mean / numElements
        variance = 0
        for  i in range(len(valueList)):
                variance += math.pow( valueList[i] - mean, 2 )*weights[i]
        variance = variance / float(numElements)
        
        return (scale * mean, scale * math.sqrt(variance))

def reportMeanStdDev(formatWidth, label, valueList, scale ):
        (m,s) = meanStdDev(valueList,scale)
        printTable(formatWidth,[label,m,s])

def reportWMeanStdDev(formatWidth, label, valueList, weights, scale ):
        (m,s) =  weightedMeanStdDev(valueList,weights,scale)
        printTable(formatWidth,[label,m,s])
        #print(label + " (mean, stdev) = " + str(weightedMeanStdDev(valueList,weights,scale)))
        
def reportCoupleCSV(sep,c ):
        (mean,stdev) = c
        sys.stdout.write(sep + str(mean) + "," + str(stdev))

def intMetric( dictionary, label ):
        return str(int(dictionary[label]))

def floatMetric( dictionary, label ):
        return str(dictionary[label])

def printTable( field_width, entries):
        """Makes it easier to format output for evaluation metrics."""
        cols = len(entries) 
        labelFormat = ''
        for i in range(0,cols):
                extra = ''
                if type(entries[i]) is float:
                        labelFormat += '{0[' + str(i) + ']:>{width}.2f' + '}'
                else:
                        labelFormat += '{0[' + str(i) + ']:>{width}}'
        print (labelFormat.format( entries, width=field_width))
def histogramm(values):
        """Compute the histogramm of all values: a dictionnary dict[v]=count"""
        hist = {}
        for v in values:
                if v in hist:
                        hist[v]+=1
                else:
                        hist[v]=1
        return hist

def printHist(hist,N,field_width):
        vals = []
        cumulVals = []
        cum = 0
        for i in range(0,N):
                if i in hist:
                        vals.append(hist[i])
                else:
                        vals.append(0)
                cum += vals[-1]
                cumulVals.append(cum)
                
                # RZ: Inefficient but simple - sum all values, substracted accumulated ones.
                total = 0
                for key in list(hist):
                        total += hist[key]

                remaining = total - cum

        printTable(field_width, [ '' ] +  list(range(0,N)) + ['>' + str(N-1)])
        print('----------------------------------------------------------------------------------')
        printTable(field_width, [ 'Num. Files' ] + vals + [ remaining ])
        printTable(field_width, [ 'Cum. Files' ] + cumulVals + [ total ])



def main():
        if len(sys.argv) < 2:
                print("Usage : [[python]] sumMetric.py <label> <file1.m> [CSV] \n")
                print("    [CSV] : print all results in one line \n")
                print("")
                print("'label' is a string used to identify data used for comparison.")
                sys.exit(0)

        showCSV = False
        if len(sys.argv) > 3:
                showCSV = True
        # Read data from CSV file.
        dataSourceLabel = sys.argv[1]
        fileName = sys.argv[2]
        try:
                fileReader = csv.reader(open(fileName))
        except:
                sys.stderr.write('  !! IO Error (cannot open): ' + fileName)
                sys.exit(0)

        # Compile distributions for all metrics.
        allValues = {}
        nbEM = 0;
        fileList = []
        for row in fileReader:
                # Skip blank lines.
                if len(row) == 0:
                        continue

                entryType = row[0].strip()
                if entryType == "*M":
                        fileList = fileList + [row[1]]
                        continue
                for i in range(0,len(row),2):
                        vName =  row[i].strip()
                        if vName not in allValues:
                                allValues[vName] = []
                        allValues[vName] = allValues[vName] \
                                        + [float(row[i+1].strip())]
                nbEM+=1
        
        # Compile and display the sum for each metric.
        allSum = {}
        allZeroCount = {}
        zeroFileList = {}
        allHist = {}
        for v in list(allValues):
                allSum[v] = sum(allValues[v])
                #print(str(v) + " = " + str(allSum[v]))
                allHist[v] = histogramm(allValues[v])
                allZeroCount[v] = 0
                for s in range(len(allValues[v])):
                        if allValues[v][s] == 0:
                                allZeroCount[v] += 1
                                if v in list(zeroFileList):
                                        zeroFileList[v] += '\n' + str(s)
                                else:
                                        zeroFileList[v] = str(s)
                                #print fileList[s]
                #print ('    Correct expressions: ' + str(nbZ))

        # Report input counts.
        correctExps = int(allZeroCount["D_B"])
        #sys.stderr.write( str( zeroFileList[ "D_B" ] ) )
        correctExps2 = int(allZeroCount["D_E(%)"])
        #sys.stdout.write( str( zeroFileList[ "D_E" ] ) )
        if(not correctExps == correctExps2):
                sys.stderr.write( "Warning : correctExps != correctExps2 (" + str(correctExps) + " vs " + str(correctExps2)+")")

        nodes = int(allSum["nNodes"])
        dcTotal = int(allSum["D_C"])
        edges = int(allSum["nEdges"])
        dlTotal = int(allSum["D_L"])
        dbTotal = int(allSum["D_B"])
        duTotal = int(allSum["dPairs"])
        dsTotal = int(allSum["D_S"])  
        dEdgeClassConflicts = int(allSum["edgeDiffClassCount"])

        if showCSV:
                print("D_C,D_L,D_S,D_B,D_B(%),var,D_E(%),var,wD_E(%),var")
                sys.stdout.write(intMetric(allSum,"D_C") + "," +intMetric(allSum, "D_L") \
                         + "," + str(dsTotal) + "," \
                         + intMetric(allSum, "D_B"))
                reportCoupleCSV(',',meanStdDev(allValues["D_B(%)"],100))
                reportCoupleCSV(',',meanStdDev(allValues["D_E"],100))
                reportCoupleCSV(',',weightedMeanStdDev(allValues["D_E"],allValues["nNodes"],100))
                print("")
        else:
                fieldWidth = 10
                
                # Add file name and date.
                print("LgEval Evaluation Summary")
                print(time.strftime("%c"))
                print("")
                print(dataSourceLabel)
                #print(os.path.splitext( os.path.split(fileName)[1]) )[0]
                print('')

                print("****  PRIMITIVES   **************************************************************")
                print('')
                printTable(fieldWidth,['Directed','Rate(%)','Total','Correct','Errors','SegErr','ClErr','RelErr'])
                print("---------------------------------------------------------------------------------")
                nodeRate = 100.0
                if nodes > 0:
                        nodeRate = 100 * float(nodes-dcTotal)/nodes
                printTable(fieldWidth,['Nodes', nodeRate, int(allSum["nNodes"]), nodes - dcTotal, dcTotal ])

        
                edgeRate = 100.0
                if edges > 0:
                        edgeRate = 100 * float(edges - dlTotal) / edges

                # RZ DEBUG: For relation conflicts, need to subtract segmentation and class label
                #           edges from total errors.
                printTable(fieldWidth,['Edges', edgeRate, edges, edges - dlTotal, dlTotal,\
                                dsTotal, dEdgeClassConflicts, dlTotal -dsTotal -dEdgeClassConflicts])

                labelRate = 100.0
                if nodes + edges > 0:
                        labelRate =  100 *(nodes + edges - dbTotal)/float(nodes + edges)
                print('')
                printTable(fieldWidth,['Total', labelRate, nodes + edges, nodes + edges - dbTotal, dbTotal])

        
                print('\n')
                printTable(fieldWidth,['Undirected','Rate(%)','Total','Correct','Errors','SegErr','ClErr','RelErr'])
                print("---------------------------------------------------------------------------------")
                printTable(fieldWidth,['Nodes', nodeRate, int(allSum["nNodes"]), nodes - dcTotal, dcTotal ])

                undirNodeRel = 100.0
                if edges > 0:
                        undirNodeRel = 100 * (float(edges)/2 - duTotal)/(edges/2)
                mergeClassErrors = int(allSum["undirDiffClassCount"])
                segPairErrors = int(allSum["segPairErrors"])

                # RZ DEBUG: As above for directed edges, reporting of segmentation and relationship count
                #           errors was wrong, despite being correct in the .csv and .diff output.
                printTable(fieldWidth,['Node Pairs', undirNodeRel, edges/2, int(edges)/2 - duTotal, duTotal, \
                                segPairErrors, mergeClassErrors, duTotal - segPairErrors - mergeClassErrors ])

                nodeAllRate = 100.0
                nodeAllCorrect = 100.0
                nodePairCorrect = 100.0

                correctNodesAndPairs = nodes - dcTotal + float(edges)/2 - duTotal
                pairCount = edges/2 
                if nodes > 0:
                        nodeAllCorrect = int(allSum["nodeCorrect"])
                        nodeAllRate = 100 * float(nodeAllCorrect)/nodes
                        nodePairCorrect = 100 * float(correctNodesAndPairs)/(nodes + pairCount)
                
                print('')
                printTable(fieldWidth,['Total', nodePairCorrect, nodes + pairCount, int(correctNodesAndPairs), int(dcTotal + duTotal) ])

                print('')
                print('     SegErr: merge/split   ClErr: valid merge class error   RelErr: relation error')
                
                print("\n")

                print("****  OBJECTS   **************************************************************************") 
                print('')
                printTable(fieldWidth,['','Recall(%)','Prec(%)','2RP/(R+P)','Targets','Correct','FalseNeg','*Detected','*FalsePos'])
                print("------------------------------------------------------------------------------------------")
                
                # Compute segmentation and classification errors.
                numSegments = int(allSum["nSeg"])
                detectedSegs = int(allSum["detectedSeg"])
                correctSegments = int(allSum["CorrectSegments"]) 
                classErrors = int(allSum["ClassError"])
                correctClass = int(allSum["CorrectSegmentsAndClass"]) 

                # DEBUG: now explicitly record the number of correct segment rel. edges.
                numSegRelEdges = int(allSum["nSegRelEdges"])
                detectedSegRelEdges = int(allSum["dSegRelEdges"])
                segRelErrors = int(allSum["SegRelErrors"])
                correctSegRelEdges = int(allSum["CorrectSegRels"])
                correctSegRelLocations = int(allSum["CorrectSegRelLocations"])

                segRelRecall = 100.0
                if numSegRelEdges > 0:
                        segRelRecall = 100*float(correctSegRelEdges)/numSegRelEdges
                segRelPrecision = 100.0
                if detectedSegRelEdges > 0:
                        segRelPrecision = float(100*float(correctSegRelEdges)/detectedSegRelEdges)
                relFalsePositive = 0
                if detectedSegRelEdges > 0:
                        relFalsePositive = segRelErrors


                segRate = 100.0
                segClassRate = 100.0
                if numSegments > 0:
                        segRate = 100 * float(correctSegments)/numSegments
                        segClassRate = 100*float(correctClass)/numSegments
                segPrec = 100.0
                segClassPrec = 100.0
                if detectedSegs > 0:
                        segPrec = 100 * float(correctSegments)/detectedSegs
                        segClassPrec = 100*float(correctClass)/detectedSegs


                segRelLocRecall = 100.0
                if numSegRelEdges > 0:
                        segRelLocRecall = 100 * float (correctSegRelLocations) / numSegRelEdges
                segRelLocPrecision = 100.0
                if detectedSegRelEdges > 0:
                        segRelLocPrecision = 100 * float(correctSegRelLocations) / detectedSegRelEdges
                segRelLocFalsePositive = 0
                if detectedSegRelEdges > 0:
                        segRelLocFalsePositive = detectedSegRelEdges - correctSegRelLocations 

                segRelativeRecall = '(Empty)'
                if correctSegments > 0:
                        segRelativeRecall = 100 * float(correctClass)/correctSegments


                segRelativeRelRecall = '(Empty)' 
                if correctSegRelLocations > 0:
                        segRelativeRelRecall = 100 * float(correctSegRelEdges)/correctSegRelLocations

                printTable(fieldWidth,['Objects', segRate, \
                                segPrec, fmeasure(segRate,segPrec),
                                numSegments, correctSegments, numSegments - correctSegments,\
                                                detectedSegs, detectedSegs - correctSegments ])

                
                printTable(fieldWidth,['+ Classes', segClassRate, \
                                segClassPrec, fmeasure(segClassRate, segClassPrec), \
                                numSegments, correctClass, numSegments - correctClass,\
                                detectedSegs, detectedSegs - correctClass])

                printTable(fieldWidth,['Class/Det', segRelativeRecall,'','', \
                                correctSegments, correctClass])

                print('')
                printTable(fieldWidth,['Relations',\
                                segRelLocRecall, \
                                segRelLocPrecision, \
                                fmeasure(segRelLocRecall, segRelLocPrecision), \
                                numSegRelEdges,\
                                correctSegRelLocations,\
                                numSegRelEdges - correctSegRelLocations, \
                                intMetric(allSum, "dSegRelEdges"),\
                                segRelLocFalsePositive])


                printTable(fieldWidth,['+ Classes',\
                                segRelRecall, \
                                segRelPrecision, \
                                fmeasure(segRelRecall, segRelPrecision), \
                                numSegRelEdges,\
                                correctSegRelEdges,\
                                numSegRelEdges - correctSegRelEdges, \
                                intMetric(allSum, "dSegRelEdges"),\
                                relFalsePositive])

                printTable(fieldWidth,['Class/Det', segRelativeRelRecall, '', '', \
                                correctSegRelLocations, correctSegRelEdges])

                print("\n     2RP/(R+P): harmonic mean (f-measure) for (R)ecall and (P)recision")
                print("     Class/Det: (correct detection and classification) / correct detection") 
                print("\n")

                print("****  FILES  ***************************************")
                print('')
                printTable(fieldWidth,['','Rate(%)','Total','Correct','Errors'])
                print('---------------------------------------------------')
                correctSegments = 0
                if 1 in allHist['hasCorrectSegments']:
                        correctSegments = allHist['hasCorrectSegments'][1]
                correctRelLocs = 0
                if 1 in allHist['hasCorrectRelationLocations']:
                        correctRelLocs = allHist['hasCorrectRelationLocations'][1]
                correctSegAndClass = 0
                if 1 in allHist['hasCorrectSegLab']:
                        correctSegAndClass = allHist['hasCorrectSegLab'][1]
                correctRelAndClass = 0
                if 1 in allHist['hasCorrectRelLab']:
                        correctRelAndClass = allHist['hasCorrectRelLab'][1]
                correctStructure = 0
                if 1 in allHist['hasCorrectStructure']:
                        correctStructure = allHist['hasCorrectStructure'][1]
                

                objRelative = '(Empty)' if correctSegments <  1 else 100 * float(correctSegAndClass)/correctSegments 
                printTable(fieldWidth,['Objects',100 * float(correctSegments)/nbEM,nbEM,correctSegments,nbEM-correctSegments])
                printTable(fieldWidth,['+ Classes',100 * float(correctSegAndClass)/nbEM, nbEM, correctSegAndClass, nbEM - correctSegAndClass])
                printTable(fieldWidth,['Class/Det',objRelative,correctSegments,correctSegAndClass,'']) #correctSegments-correctSegAndClass])

                print('')
                relRelative = '(Empty)' if correctRelLocs < 1 else 100 * float(correctRelAndClass)/correctRelLocs
                printTable(fieldWidth,['Relations',100 * float(correctRelLocs)/nbEM,nbEM,correctRelLocs,nbEM-correctRelLocs])
                printTable(fieldWidth,['+ Classes',100 * float(correctRelAndClass)/nbEM, nbEM, correctRelAndClass, nbEM - correctRelAndClass])
                printTable(fieldWidth,['Class/Det',relRelative, correctRelLocs,correctRelAndClass,'']) #correctRelLocs - correctRelAndClass])

                print('')
                expRelative = '(Empty)' if correctStructure < 1 else 100 * float(correctExps)/correctStructure
                printTable(fieldWidth,['Structure',100 * float(correctStructure)/nbEM, nbEM, correctStructure, nbEM - correctStructure])

                printTable(fieldWidth,['+ Classes',100 * float(correctExps)/nbEM,nbEM,correctExps,nbEM-correctExps,'*Final'])
                printTable(fieldWidth,['Class/Det',expRelative,correctStructure,correctExps,'']) #correctStructure-correctExps])
                print('')
                
                print('')
                print("****  LABEL ERROR HISTOGRAM (Dir. Edges, D_B)  ****")
                print('')
                printHist(allHist['D_B'],6,fieldWidth)
                print('')


main()
