#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Wei Shuai"
__copyright__ = "Copyright 2018 Wei Shuai <cpuwolf@gmail.com>"
__version__ = "1.0.0"
__email__ = "cpuwolf@gmail.com"
"""
Created on Feb 2018
@author: Wei Shuai <cpuwolf@gmail.com>

Thanks to 
https://forums.x-plane.org/index.php?/forums/topic/140285-how-to-give-your-777-better-wing-flex/

@Dusty926@x-plane.org he created fine-tuned wing flex animation based on FF777

all fine-tuned values are defined in file <FF777 Flex Values.txt>

this scripts targets to process <FF777 Flex Values.txt>, then apply all values into FF777 aircraft folder

"""

import os
import shutil

def findwholeline(data,keyword,startidx):
    idx=data[startidx:].find(keyword)
    if idx != -1:
        #print idx
        idxtmpstart = startidx+idx
        idxtmpend=data[idxtmpstart:].find("\n")
        idxend = idxtmpstart +idxtmpend
        #print idxend
        if idxtmpend != -1:
            lines=data[:idxend].splitlines()
            #print lines[-1]
            idxstart=data[startidx:].find(lines[-1])
            if idxstart != -1:
                #print idxstart,idxend
                return [startidx+idxstart,idxend]
        else:
            #file end without '\n'
            lines=data.splitlines()
            #print lines[-1]
            idxstart=data[startidx:].find(lines[-1])
            if idxstart != -1:
                #print idxstart,idxend
                return [startidx+idxstart,len(data)]
    return [-1,-1]


def findsection(data,keywordstart,keywordend):
    searchidx=0
    result=[]
    while searchidx <= len(data):
        [idxstart,idxend]=findwholeline(data,keywordstart,searchidx)
        if (idxstart != -1) and (idxend != -1):
            [idxsecstart,idxsecend]=findwholeline(data,keywordend,idxend)
            if (idxsecstart != -1) and (idxsecend != -1):
                searchidx=idxsecend
                result.append([idxstart,idxsecend,data[idxstart:idxend]])
            else:
                print "error"
                break
        else:
            break
    return result   

def processxpobj(fileobj,cklist):
    listmerge = []
    with open(fileobj,"r") as f:
        data = f.read()
        for list in cklist:
            kword = list[0]
            sections=findsection(data,kword,"ANIM_rotate_end")
            listmerge+=sections
        
        wewant = sorted(listmerge, key=lambda tup: tup[0])
        print wewant
        lenwewant = len(wewant)
        if lenwewant > 1:
            i = 0
            newdata = data[:wewant[0][0]]
            while i < lenwewant:
                j = 0
                for chk in chklist:
                    fdidx=wewant[i][2].find(chk[0])
                    if fdidx != -1:
                        break;
                    j+=1
                
                if i + 1 < lenwewant:
                    newdata += chklist[j][1]+data[wewant[i][1]:wewant[i+1][0]]
                else:
                    newdata += chklist[j][1]+data[wewant[i][1]:]
                i += 1

            shutil.copy(fileobj, fileobj+".orig.obj")
                
            with open(fileobj,"w") as f:
                f.write(newdata)

def loadinputfile(filetxt):
    cookies = []
    wewant = []
    with open(filetxt,"r") as f:
        data = f.read()
        sections=findsection(data,"ANIM_rotate_begin ","ANIM_rotate_end")
        index=1
        while index < len(sections):
            if sections[index][0]-sections[index-1][1] == 1:
                cookies.append([sections[index-1][0],sections[index][1],sections[index-1][2]])
                tmpidx=index
                tmpidx+=2
                if tmpidx < len(sections):
                    index+=2
                else:
                    index+=1
            else:
                cookies.append(sections[index])
                index+=1
        #print cookies
        for cookie in cookies:
            sp=cookie[2].split(' ')
            wewant.append([sp[-1],data[cookie[0]:cookie[1]]])
            #wewant.append([cookie[2],data[cookie[0]:cookie[1]]])
        print wewant, len(wewant)
        return wewant
    
def findxpobj(root,cklist):
    for path, dirs, files in os.walk(root):
        for file in files:
            if file.endswith(".obj"):            # this line is new
                print os.path.join(path, file)
                processxpobj(os.path.join(path, file),cklist)



chklist=loadinputfile("F:\\works\\GitHub\\ff777wingflex\\FF777 Flex Values.txt")
'''chklist=[["WingPress","hello"],["EngRPress","hello"]]'''
findxpobj("C:\\Program Files\\X-Plane 11\\Aircraft\\Extra Aircraft\\Boeing777-Extended\\objects",chklist)
print "all done!"