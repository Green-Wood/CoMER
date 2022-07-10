#################################################################
# SmGrConfMatrix.py
#
# Structure confusion histograms. 
#
# Author: H. Mouchere, June 2013
# Copyright (c) 2013-2014 Richard Zanibbi and Harold Mouchere
################################################################

from operator import itemgetter

# Set graph size.
GRAPH_SIZE=100

class SmDict(object):
	"""This is not a real dictionnary but it is like a dictionnary using only 
	the == operator (without hash) 
	A value can be associate to a smallGraph. 
	For efficiency, use an object as a value to avoid call to set()
	It uses the isomorphism to know if 2 smallGraphs are the same."""
	
	def __init__(self,*args):
		self.myitems = []
	
	def set(self, sg, value):
		for i in range(len(self.myitems)):
			if(sg == self.myitems[i][0]):
				self.myitems[i][1] = value
				return
		self.myitems.append((sg,value))
		
	def get(self, sg, defaultType = object):
		"""find the corresponding key and if not found add it with the default value"""
		for i in range(len(self.myitems)):
			if(sg == self.myitems[i][0]):
				return self.myitems[i][1]
		self.myitems.append((sg, defaultType()))
		return self.myitems[-1][1]
		
	def __contains__(self,sg):
		for i in range(len(self.myitems)):
			if(sg == self.myitems[i][0]):
				return True
		return False

	def getIter(self):
		for p in self.myitems:
			yield p
	def __str__(self):
		res = "{"
		for (k,v) in self.myitems:
			res = res + "(" + str(k) + ":" + str(v) + "),"
		return res[:-1] + "}"
	def toHTML(self, limit = 0):
		html = '<table border="1">\n'
		sortedList = sorted(self.myitems, key=lambda t:t[1].get(), reverse=True)
		for (g,v) in sortedList:
			if (v.get() >  limit):
					html = html + '<tr><td>\n' + g.toSVG(100) + '</td>\n'
					html = html + '<td>'+str(v)+'</td></tr>\n'
		return html + '</table>\n'
		

class Counter(object):
	""" just a small counter but embedded in an object
	Designed to be used in smDict
	It can save a list of object by adding it as param in the 
	incr() function"""
	
	def __init__(self,*args):
		self.value = 0
		self.list = []
		if(len(args)> 0):
			self.value = int(args[0])
			if (len(args) == 2):
				self.list = args[1]
	def incr(self,elem=None):
		self.value = self.value +1
		if elem != None:
			self.list.append(elem)
		else:
			self.list = [ elem ]
	def get(self):
		return self.value
	def set(self,v):
		self.value = int(v)
	def getList(self,unique = True):
		if unique:
			return list(set(self.list))
		else:
			return self.list
	def add(self,c2):
		return Counter(self.value + c2.value, self.list + c2.list)

	def __add__(self,c2):
		return Counter(self.value + c2.value, self.list + c2.list)

	def __str__(self):
		return str(self.value)
	def __int__(self):
		return self.value
	
	
	
class ConfMatrix(object):
	
	def __init__(self,*args):
		self.mat = SmDict()
	
	def size(self):
		return len(self.mat.myitems)

	def incr(self, row, column, elem=None):
		""" add 1 (one) to the counter indexed by row and column
		an object can be added in the attached list"""
		self.mat.get(row, SmDict).get(column,Counter).incr(elem)
	def __str__(self):
		return str(self.mat)

	def errorCount(self):
		count = 0
		for (obj,smDict) in self.mat.getIter():
			count += sum([v.get() for (_,v) in smDict.getIter()])
			#nbE = Counter()
			#for (_,c) in errmat.getIter():
			#	nbE = nbE + sum([v for (_,v) in c.getIter()], Counter())
			#count += nbE.get()
		return count

	def toHTMLfull(self, outputStream):
		i = 0
		allErr = SmDict()
		outputStream.write(' <table border="1"><tr>')
		outputStream.write('<td></td>')
		for (rowG,col) in self.mat.getIter():
			for (g,_) in col.getIter():
				c = allErr.get(g,Counter)
				if c.get() == 0:
					c.set(i)
					i = i+1
					outputStream.write( '<th>' + g.toSVG(100) + '</th>')
		outputStream.write('</tr>')
		nbE = len(allErr.myitems)
		for (rowG,col) in self.mat.getIter():
			i = 0
			outputStream.write('<tr><th>\n' + rowG.toSVG(100) + '</th>')
			for (g,v) in col.getIter():
				c = allErr.get(g)
				for empty in range(i,c.get()):
					outputStream.write('   <td>0</td>')
				outputStream.write('   <td>' + str(v) + '</td>')
				i = c.get()
			for empty in range(i,nbE-1):
				outputStream.write('   <td>0</td>')
			outputStream.write('</tr>\n')
		outputStream.write('</table>\n<p>')

	def toHTML(self, outputStream, limit = 0, targetLimit = 1, viewerURL="", redn = [], rede = [], parentObject=0):
		""" write in the output stream the HTML code for this matrix and
		return a Counter object with
		the number of unshown errors and the list of hidden elements
		The list of files with errors is prefixed with the param viewerURL
		in the href attribute."""
		
		arrow = True
		hiddenErr = Counter()
		sortedList = []
	# first count all error for each sub structure
		for (rowG,col) in self.mat.getIter():
			nbE = sum([v for (_,v) in col.getIter()],Counter())
			sortedList.append((rowG,col,nbE))
		
		# Show each confused stroke-level graph target in decreasing order of frequency.
		sortedList = sorted(sortedList, key=lambda t:t[2].get(), reverse=True)
		tindex = 1
		graphSize=int(GRAPH_SIZE * 1.0)
		outputStream.write('<table valign="top">')
		outputStream.write('<tr><th>' \
		+ '<input type="checkbox" id="Obj' + str(parentObject) + '"></th><th>Targets</th></tr>\n')
		for (rowG,col,nbE) in sortedList:
			if int(nbE) >= limit:
				
				outputStream.write('<tr><th text-align="center" valign="top"><input type="checkbox" id="Obj' + str(parentObject) + 'Target' + str(tindex) + '" name="fileList">' + str(tindex) + '</th><th>' \
						+ str(nbE) + ' errors<br><br>\n')
				outputStream.write(rowG.toSVG(graphSize,arrow))
				outputStream.write('\n</th>')
				
				# ** Now show specific stroke-level confusions for target graph.
				locHiddenErr = Counter()
				arrow = False

				# Critical: sort by frequency for specific confusion instances.
				pairs = sorted(col.getIter(), key=lambda p:p[1].get(), reverse=True)
				findex = 1
				for (g,v) in pairs:
					if v.get() >= limit:
						value = (" ").join(v.getList())
						outputStream.write('<td><input type="checkbox" name="fileList" id="Obj' + str(parentObject) + 'Target' + str(tindex) + 'Files' + str(findex) + '" class="fileCheck" value="' \
								+ value + '">')
						outputStream.write('\n'+str(v) + ' errors<br><br>')
						outputStream.write(g.toSVG(graphSize,arrow))
						outputStream.write('</td>\n')
					else:
						# Tricky; this counter object __str__ gives its list
						# size, but '+' concatenates entries.
						locHiddenErr = locHiddenErr + v
					
					findex += 1
				
				# Write only one entry for 'other' errors. Do this
				# Whenever a target/row is shown for completeness.
				if len(locHiddenErr.getList()) > 0:
					value = (" ").join(locHiddenErr.getList())
					outputStream.write('<td valign="top">' \
							+ '<input type="checkbox" id="Obj' + str(parentObject) + 'Target' + str(tindex) + 'Files' + str(findex) + '" name="fileList" class="fileCheck" value="' \
							+ value + '">' + str(locHiddenErr) + ' errors<br><br>')
					outputStream.write('<center><font size=2>Other<br>Errors</font></center></td>')

				outputStream.write('</tr>')
			
			elif int(str(nbE)) >= targetLimit:
				
				# This is for errors less frequent than the threshold
				# for different target stroke-level graphs.
				locHiddenErr = Counter()
				for (g,v) in col.getIter():
					locHiddenErr = locHiddenErr + v

				# Show all ground truth target errors with counts, so that
				# object-level count is sum of confused stroke-level graphs.
				value = (" ").join(locHiddenErr.getList())
				outputStream.write('<tr><th valign="top"><input type="checkbox" id="Obj' + str(parentObject) + 'Target' + str(tindex) + '"> ' + str(nbE) + ' errors<br><br>\n')
				outputStream.write(rowG.toSVG(graphSize,arrow))
				outputStream.write('</th><td valign=\"top\"><input type="checkbox" class="fileCheck" id="Obj' + str(parentObject) + 'Target' + str(tindex) + 'Files1" value="' + value + '">' +
					str(locHiddenErr) + ' errors<br><br>')
				outputStream.write('<center><font size=2>Other<br>Errors</font></center></td></tr>')
				
			else:
				hiddenErr = hiddenErr + nbE

			# Increment counter for stroke-level targets.
			tindex += 1
		
		# End this entry.
		outputStream.write('</table>\n')
			
		return hiddenErr
		

class ConfMatrixObject(object):
	
	def __init__(self,*args):
		self.mat = SmDict()
	
	def size(self):
		return len(self.mat.myitems)

	def incr(self, obj, row, column,elem=None):
		self.mat.get(obj, ConfMatrix).incr(row, column,elem)

	def __str__(self):
		return str(self.mat)

	def errorCount(self):
		count = 0
		for (obj,errmat) in self.mat.getIter():
			nbE = Counter()
			for (_,c) in errmat.mat.getIter():
				nbE = nbE + sum([v for (_,v) in c.getIter()], Counter())
			count += nbE.get()
		return count

	def toHTML(self, outputStream, limit = 0, viewerURL="", redn = {}):
		""" write in the output stream the HTML code for this matrix and
		use the ConfMatrix.toHTML to write the submatrices.
		The list of files with error is prefixed with the param viewerURL
		in the href attribute. """
		outputStream.write(' <table><tr>')
		outputStream.write('<th><input type="checkbox" id="Obj"></th><th>Object Targets</th><th>Primitive Targets and Errors</th>')
		outputStream.write('</tr>')
		arrow = True
		hiddenErr = Counter()
		sortedList = []
		# first count all errors for each object (over the full sub matrix)
		for (obj,errmat) in self.mat.getIter():
			nbE = Counter()
			for (_,c) in errmat.mat.getIter():
				nbE = nbE + sum([v for (_,v) in c.getIter()], Counter())
			sortedList.append((obj,errmat,nbE))
		sortedList = sorted(sortedList, key=lambda t:t[2].get(), reverse=True)

		# Entries for object graphs ('main' rows)
		oindex = 1
		graphSize=GRAPH_SIZE
		for (obj,errmat,nbE) in sortedList:
			if int(nbE) >= limit:
				outputStream.write('<tr><th valign="top">' \
						+ str(oindex) + '</th>')
				outputStream.write('<th valign="top">\n')
				outputStream.write(str(nbE) + " errors<br><br>")
				outputStream.write(obj.toSVG(graphSize,arrow,'box'))
				outputStream.write('</th><td>')
				arrow = False
				# Treat 'object-level' matrix different: show all missed targets.
				hiddenErr = hiddenErr + errmat.toHTML(outputStream,limit,viewerURL,parentObject=oindex)
				outputStream.write('</td></tr>\n')
			else:
				hiddenErr = hiddenErr + nbE
			
			# Increment count for object targets
			oindex += 1
		
		outputStream.write('</table><p><b>Additional errors:</b> ')
		viewStr = ""
		if(len(hiddenErr.getList())> 0):
			viewStr = '<a href="' + viewerURL+ (",").join(hiddenErr.getList())+'"> View </a>'
		outputStream.write(str(hiddenErr) + viewStr + '</p>')
		
	
