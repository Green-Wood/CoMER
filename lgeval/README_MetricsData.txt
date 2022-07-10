-------------------------------------------------------------------
  README: Summary of Metrics and Key Data Structures
  LgEval 0.3.2

  First Version: Oct. 10, 2014 (R. Zanibbi)
  Copyright (c) 2014 Richard Zanibbi and Harold Mouchere
-------------------------------------------------------------------

LgEval uses a simple file-based approach to evaluating individual files and
collections of files.

The program src/evallg.py provides the main functions from which metrics are
computed for each input file, producing a metrics file (<infile>.csv) and a
file specific differences between the input and its target (<infile>.diff,
another .csv file).

When using the 'evaluate' script, metrics and differences for individual files
are written to a <Results_Dir>/Metrics directory. These individual results are
concatenated and then used to produce the raw results spreadsheet and summary
files output by the 'evaluate' script.

:: Adding Metrics ::

Metrics may be added by modifying the lists of named metrics in the functions
lg.compare() and lg.compareSegments() in src/lg.py. Once added to one of these
lists, they will automatically be computed and compiled when using the
'evaluate' script.


DIFF FILE FORMAT (.diff)
---------------------------

.diff files are in CSV format, representing one pair of disagreeing labels per 
line.

Node label errors:

	*N, Primitive ID, OutputLabel, OutputWeight, :vs:, TargetLabel, TargetWeight

Edge label errors (single line in .diff file):

	*E, Primitive ID (parent), Primitive ID (child), OutputLabel, OutputWeight, :vs:,
		TargetLabel, TargetWeight

Segmentation errors showing primitive pair where output and target disagree on 
whether the two primitives belong to the same object:

	*S, PrimitiveID (parent), PrimitiveID (child)

NOTE: because primitive merges are represented by bidirectional edges, normally
if *S,1,2 appears in a .diff file, *S,2,1 will also appear in the file.


METRIC DESCRIPTIONS
--------------------------------------------------

Metrics have been organized into groups below. Please note that they currently
do not appear in this order in 00_RawResults.csv.

Targets
---------
nNodes                  Number nodes in ground truth (comparison) file
nEdges                  Number edges in ground truth (comparison) file
nSeg                    Number objects (segments) in ground truth (comparison)
nSegRelEdges            Number object relationships in ground truth (comparison) 

Detections
-----------
detectedSeg             Number objects detected in input file
dSegRelEdges            Number object relationships in input file

Primitive Metrics
-------------------
D_B                     Number of incorrect node and edge labels
D_C                     Number of incorrect node/primitive labels
D_L                     Number of incorrect edge labels
D_R                     Number of incorrect relationship edges
D_S                     Number of incorrect 'merge/object' edges 
D_E(%)                  Weighted accuracy over node and edge labels 
                        (see DRR 2013 paper)   
nodeCorrect             Number primitives (nodes) correctly labeled

segPairErrors           Number incorrectly merged/split primitive pairs 
edgeDiffClassCount      Number valid directed merge edges with incorrect object type  
undirDiffClassCount     Number valid undirected merge edges with incorrect object type
dPairs                  Number incorrect *undirected* node pairs


Object Metrics
------------------
CorrectSegRelLocations      Number correct relationship locations
CorrectSegRels              Number correctly located and labeled relationships 
CorrectSegments             Number correctly segmented objects
CorrectSegmentsAndClass     Number correctly segmented and labeled objects
ClassError                  Number incorrectly classified objects
SegRelErrors                Number incorrectly detected segment relationships

Flags (1/0)
-------------
hasCorrectSegments          Object locations are correct
hasCorrectSegLab            Object locations and labels correct
hasCorrectRelationLocations Object relationship locations correct
hasCorrectRelLab            Object relationship locations correct
hasCorrectStructure         Object *and* relationship locations correct




LGEVAL KEY DATA STRUCTURES
------------------------------------

Label Graph Attributes (see lg.py)
-----------------------------------
lg.error            Error flag
lg.cmpNodes         Function used to compare node labelings 
                    (default: Hamming distance, #disagreeing labels)
lg.cmpEdges         Function used to compare edges labelings
                    (default: Hamming distance)

lg.nlabels          Dictionary from node (primitive) identifiers to
                    another dictionary mapping labels to confidence values
                    (floating point values)
lg.elabels          Dictionary from primitive pairs (edges) to
                    another dictionary mapping labels to confidence values
                    (floating point values)
lg.absentNodes      Set of identifiers not present in the lg relative
                    to another lg (e.g. relative to ground truth)


Graph Segment Output (output of lg.segmentGraph())
----------------------------------------------------
segmentPrimitiveMap    Dictionary from object identifier to a pair (a,b)
                       a: set of primitives in the object, b: list of labels
primitiveSegmentMap    Dictionary from primitive identifier to 
                       another dictionary mapping a label to the object id
                       associated with the primitive for this relationship type
rootSegments           Set of objects with no incoming edges
segmentEdges           Dictionary from pairs of object identifiers to
                       another dictionary mapping relationship labels to 
                       confidence values

'compareSegments' output (lg.compareSegments())
------------------------------------------------
edgeDiffCount       Number of disagreeing 'merge/object' edges        
segDiffs            Dictionary mapping primitives to pairs of
                    primitives belonging to objects ( diff1, diff2 )
correctSegments     Set of (Obj id, label) pairs for correct segments
metrics             List of metric (name, value) pairs - these are a
                    subset of the metrics described above
primRelEdgeDiffs    Dictionary mapping primitive pairs (edges) to an
                    error entry (should probably be simplified)

'compare' output (lg.compare())
---------------------------------
metrics             All metrics described above
nodeconflicts       List of pairs (node id, [ (l1, 1.0), (l2, 1.0) ])
                    where l1 and l2 are disagreeing labels
edgeconflicts       List of pairs ( (nid_1, nid_2, [ (l1, 1.0), (l2, 1.0) ])
                    where l1 and l2 are disagreeing labels
segDiffs            Produced by compareSegments() (see above)
correctSegs         Produced by compareSegments() (see above)
segRelDiffs         Same as primRelEdgeDiffs from compareSegments() 
                    (see above)

