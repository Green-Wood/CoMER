################################################################
# metricDist.py
#
# Filter to collect the distribution for a metric in a given 
# .m (metrics) file.
#
# Author: R. Zanibbi, June 2012
# Copyright (c) 2012-2014 Richard Zanibbi and Harold Mouchere
################################################################
import sys
import csv
import math

def main():
	if len(sys.argv) < 3:
		print("Usage : [[python]] metricDist.py <metric_name> <file1.m> [sort]\n")
		print("    Print all values for the passed metric name/field in")
		print("    metric file file1.m to the standard output. By default")
		print("    results are returned as (file,value) pairs in order of")
		print("    appearance.")
		print("")
		print("    !NOTE! For metrics with special characters, e.g. 'DB(%)',")
		print("    the metric name *must* be passed in double quotes.")
		print("")
		print("    Any third argument (e.g. 'sort') will result in sorting")
		print("    the values before they are output.")
		sys.exit(0)

	# Read metric data from CSV file.
	fileName = sys.argv[2]
	fileOut = open("listStrokeN.txt","w")
	try:
		fileReader = csv.reader(open(fileName))
	except:
		sys.stderr.write('  !! IO Error (cannot open): ' + fileName)
		sys.exit(0)

	# Collect all values for the given metric; associate these with files.
	values = []
	for row in fileReader:
		# Skip blank lines.
		if len(row) == 0:
			continue

		entryType = row[0].strip()
		if entryType == "*M":
			file = row[1]
			continue

		for i in range(0,len(row),2):
			metricName = row[i].strip()
			if metricName == sys.argv[1]:
				values = values + [ (file, float(row[i+1].strip()) ) ]

	# Sort if user requested this.
	byValue = lambda pair: pair[1]  # define key for sort comparisons.
	if len(sys.argv) > 3:
		values = sorted(values, key=byValue)

	# Print the values for the metric.
	for val in values:
		print(val[0] + ', ' + str(val[1]))

main()
