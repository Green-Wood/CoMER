#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 11:43:15 2019
replace node tags with absolute path

@author: mxm7832
"""

import sys
import os

def write_lg(lg,tag,outlg):
    
    filename=lg.split('/')[-1]
    outlg=outDir+filename
    #print(filename)
    with open(outlg,'w') as out:
        
        for line in open(lg):
            if line.startswith('O'):
                parts=line.strip().split(', ')
                newline=parts[0]+', '+parts[1]+', '+parts[2]+', '+parts[3]+', '+tag[parts[1]]+'\n'                
                line=newline
            '''    
            elif line.startswith('R') or line.startswith('EO'):
                parts=line.strip().split(', ')
                tag=norm_relTag(parts[3])
                newline=parts[0]+', '+parts[1]+', '+parts[2]+', '+tag+', '+parts[4]+'\n'
                line=newline
            '''
            out.write(line)
    out.close()    
            

def norm_relTag(input_tag):
    if input_tag in ['R','Right','r','HORIZONTAL','horizontal','HOR']:
        return 'R'
    
    if input_tag in ['Sub','SUB','SUBSC']:
        return 'Sub'

    if input_tag in ['Sup','SUP','SUPER']:
        return 'Sup'

    if input_tag in ['Above','ABOVE','a','A','UPPER','ULIMIT']:
        return 'Above'

    if input_tag in ['Below','BELOW','b','B','UNDER','LLIMIT']:
        return 'Below'

    if input_tag in ['I','Inside']:
        return 'Inside'

    return input_tag

def update_LG_node_grouping(lg,outDir):
    edge_dict={}
    obj_list=[]
    txt=open(lg) 
    for line in txt:
        if line.startswith('R') or line.startswith('EO'):
            _,parent,child,rel,_=line.strip().split(', ')
            if child not in edge_dict.keys():
                edge_dict[child]=parent,rel
            # check for sqrt condition  
            elif edge_dict[child][1]=='Right': 
                print(edge_dict[child][1])
                pass
            elif edge_dict[child][1]=='Inside': 
                edge_dict[child]=parent,rel
            else:
                print('multiple key!')
                pass
    
        if line.startswith('O'):
            obj_id=line.strip().split(', ')[1]
            obj_list.append(obj_id)
    #finding the relative positions        
    tag={}
    for node in obj_list:
        path=''
        key=node
        while key:
            if key in edge_dict.keys():
                next_key,rel=edge_dict[key]
                #norm rel tags 
                rel=norm_relTag(rel)
                #print(rel)
                #path.insert(0,rel)
                path=rel+path
                key=next_key
            else:
                break
                #key=False
        tag[node]='O'+path
    
    write_lg(lg,tag,outDir)
    
if __name__=='__main__':
    
    if len(sys.argv) < 3:
        print('usage: node_tags.py file.lg outDir')
        print('       node_tags.py folder outDir')
        exit()
    else:
        if sys.argv[2][-1] != os.sep: sys.argv[2] += os.sep
        outDir=sys.argv[2]
	            
        if os.path.isfile(sys.argv[1]):
            FILES = [sys.argv[1]]
        else:
            from glob import glob
            if sys.argv[1][-1] != os.sep: sys.argv[1] += os.sep
            FILES = glob(sys.argv[1]+os.sep+"*.lg")

    for lgfile in FILES:
        #print(lgfile)
        update_LG_node_grouping(lgfile,outDir)        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
