# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 15:25:04 2019
Preprocess MathMl files to be rendered to LG
@author: mahshad

"""
from bs4 import BeautifulSoup
import numpy as np
import sys
import os

def check_tags(tagList):
    for tag in tagList:
        if tag not in ['mrow','mi','mo','mn','msup','msub','mfrac','msqrt',
                       'mroot','msubsup','munder', 'mover', 'munderover',
                       'mtd', 'mtable', 'mtr']: 
                       
            print ('**** WARNING: unkown tag is detected:', tag)

 
def remove_unknown_tags(mml):
    valid=['mrow','mi','mo','mn','msup','msub','mfrac','msqrt',
                       'mroot','msubsup','munder', 'mover', 'munderover',
                       'mtd', 'mtable', 'mtr','semantics']   
    invalid=[]
    for subtree in mml.findChildren(): 
        tag=subtree.name
        if tag not in valid:
            invalid.append(tag)
    #print('invalid tags found', invalid)

    #check if semantics exist
    #new_mml=mml.findChildren()[1] if 'semantics' in invalid else mml
    new_mml=mml
    for tag in invalid:
        for item in new_mml.select(tag):
            item.decompose()
            
    return new_mml

# normalize symbols and add ID
def add_ID(mml):
    
    for count, subtree in enumerate(mml.findAll()):
        norm_label=normalizeSymbol(subtree.text)
        #print(subtree.name)
        #Add tags
        if subtree.name in ['mi','mo','mn']:
            subtree['xml:id']=str(norm_label)+'_'+str(count)
 
        elif subtree.name in ['mfrac','mroot','msqrt','mtr','mtable','mtd']:
            subtree['xml:id']='_'+str(count)
    return mml

#return mathml unicodes into latex labels
def normalizeSymbol(label):
    if label in ['rightarrow', 'sum', 'int', 'pi', 'leq', 'sin','cos','tan', 'lim',
                 'geq', 'infty', 'prime', 'times','alpha', 'beta','pm','log','}','{']:
        
        return '\\'+label
    
    if label == '÷': label= '\\div'
    if label == '×': label= '\\times'
    if label == '±': label= '\\pm'    
    if label == '∑': label= '\\sum'
    if label == 'π': label= '\\pi'
    if label == '∫': label= '\\int'        
    if label == 'θ': label= '\\theta'
    if label == '∞': label= '\\infty'
    if label == '…': label= '\\ldots' 
    if label == 'β': label= '\\beta'        
    if label == '→': label= '\\rightarrow'
    if label == '≤': label= '\\leq'
    if label == '≥': label= '\\geq' 
    if label == '<': label= '\\lt'        
    if label == '>': label= '\\gt'
    #if label == '=': label= '\\eq'    
    if label == 'σ': label= '\\sigma'     
    if label == 'ϕ': label= '\\phi'     
    if label == '′': label= '\\prime'     
    if label == 'Γ': label= '\\gamma' 
    if label == 'γ': label= '\\gamma'     
    if label == 'μ': label= '\\mu'     
    if label == 'λ': label= '\\lambda'     
    if label == 'Δ': label= '\\Delta'     
    if label == '∃': label= '\\exists'     
    if label == '∀': label= '\\forall'     
    if label == '∈': label= '\\in'  
    if label == '∂': label= '\\partial'     
    if label == '≠': label= '\\neq'   
    if label == 'α': label= '\\alpha'     
    if label == '−': label= '-'     
    
    
    return label

def build_seg_unit(c1,label,c2,ID):
    
    norm_label=normalizeSymbol(label)
    unit=""" <traceGroup xml:id="%d">
    <annotation type="truth">%s</annotation>
	<traceView traceDataRef="%d"/>
    <annotationXML href="%s"/>
	</traceGroup>\n""" % (c1,norm_label,c2,ID) 
             
    return unit


def write_mml(mml,filename,outdir):
    filename=filename.split('.')[0]
    
    inkml_tags="""<ink xmlns="http://www.w3.org/2003/InkML">
    <annotation type="UI">%s</annotation>
    <annotationXML type="truth" encoding="Content-MathML">
    <math xmlns='http://www.w3.org/1998/Math/MathML'>
    """%filename
    
    node_tags=['mi','mo','mn']#'mtr','mtable','mtd'] 
    #'mfrac','mroot','msqrt']
    
    #check if semantics exist
    new_mml=mml.findChildren()[1] if 'semantics' in str(mml.findChildren()[0]) else mml.findChildren()[0]    
                   
    with open(outdir+filename+'.inkml','w') as f:
        f.write(inkml_tags)
        f.write(str(new_mml)+'\n')
        f.write('</math>\n</annotationXML>\n')
        #add groupings
        f.write('<traceGroup xml:id="0">\n<annotation type="truth">Segmentation</annotation>\n')

        nodes=mml.findAll(node_tags)
             
        for i,subtree in enumerate(nodes):
            t1=build_seg_unit(i+1,subtree.text,i,subtree['xml:id'])          
            f.write(t1)

        count=len(nodes)
        for i,subtree in enumerate(mml.findAll('mfrac')):
            t2=build_seg_unit(count+1,'-',count,subtree['xml:id']) 
            count=count+1                    
            f.write(t2)

        for i,subtree in enumerate(mml.findAll(['mroot','msqrt'])):
            t3=build_seg_unit(count+1,'\sqrt',count,subtree['xml:id'])
            count=count+1                    
            f.write(t3)
    
        f.write('</traceGroup>\n</ink>')
    f.close()
    
if __name__=='__main__':
   
    '''
    Usage: process_mml.py file.mml outdir
           process_mml.py folder outdir

    Example: Python3 process_mml.py 'im2Markup_results/gtMML/573d26461e.mml' 'examples/'

    '''	
    if len(sys.argv) < 2:
        print('usage: process_mml.py file.mml outdir')
        print('       process_mml.py folder outdir')
        exit()
    else:
        if sys.argv[2][-1] != os.sep: sys.argv[2] += os.sep
        outDir=sys.argv[2]	
        if os.path.isfile(sys.argv[1]):
            FILES = [sys.argv[1]]
        else:
            from glob import glob
            if sys.argv[1][-1] != os.sep: sys.argv[1] += os.sep
            FILES = glob(sys.argv[1]+os.sep+"*.mml")

    print ('*** converting %d files *******'%len(FILES))
    for mmlPath in FILES: 
    #mmlPath='im2Markup_results/gtMML/573d26461e.mml'
        name=mmlPath.split('/')[-1]
        #print(name)
        soup = BeautifulSoup(open(mmlPath),'lxml')
        if soup('math'):
            body=soup('math')[0]
            clean_mml=remove_unknown_tags(body)
            id_mml=add_ID(clean_mml)
        
            write_mml(id_mml,name,outDir)
            
        else: 
            print('math tag not found for: ',name)
            continue
            
    #print(str(clean))
    
 
