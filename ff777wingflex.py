#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Wei Shuai"
__copyright__ = "Copyright 2018 Wei Shuai <cpuwolf@gmail.com>"
__version__ = "1.0"
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
import sys
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import QThread
from PyQt4.QtGui import QFileDialog
import ConfigParser

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
                for chk in cklist:
                    fdidx=wewant[i][2].find(chk[0])
                    if fdidx != -1:
                        break;
                    j+=1
                
                if i + 1 < lenwewant:
                    newdata += cklist[j][1]+data[wewant[i][1]:wewant[i+1][0]]
                else:
                    newdata += cklist[j][1]+data[wewant[i][1]:]
                i += 1

            shutil.copy(fileobj, fileobj+".orig.obj")
                
            with open(fileobj,"w") as f:
                f.write(newdata)

def loadinputfile(filetxt):
    cookies = []
    wewant = []
    try:
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
    except IOError:
        return wewant
    return wewant
    
def findxpobj(root,cklist):
    for path, dirs, files in os.walk(root):
        for file in files:
            if file.endswith(".obj"):            # this line is new
                print os.path.join(path, file)
                processxpobj(os.path.join(path, file),cklist)



#chklist=loadinputfile("F:\\works\\GitHub\\ff777wingflex\\FF777 Flex Values.txt")
'''chklist=[["WingPress","hello"],["EngRPress","hello"]]'''
#findxpobj("C:\\Program Files\\X-Plane 11\\Aircraft\\Extra Aircraft\\Boeing777-Extended\\objects",chklist)

def myreadconfig():
    config = ConfigParser.RawConfigParser()
    config.read('ff777wingflex.cfg')
    return [config.get('basic', 'inputfile'),config.get('basic', 'outputfolder')]

        
def mywriteconfig(ifile,ofolder):
    config = ConfigParser.RawConfigParser()
    config.add_section('basic')
    config.set('basic', 'inputfile', ifile)
    config.set('basic', 'outputfolder', ofolder)
    with open('ff777wingflex.cfg', 'wb') as configfile:
        config.write(configfile)

class MyThread(QThread):
    set_text = QtCore.pyqtSignal('QString')
    def __init__(self):
        QThread.__init__(self)
        self.text_valuepath = None
        self.text_folderpath = None
    def __del__(self):
        self.wait()
    def run(self):
        self.set_text.emit(self.text_valuepath)
        chklist=loadinputfile(self.text_valuepath)
        findxpobj(os.path.abspath(self.text_folderpath),chklist)
        self.set_text.emit("<h1>finished!!</h1>")


qtCreatorFile = "main.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.pushButtonfix.clicked.connect(self.GoCrazy)
        self.pushButtonValue.clicked.connect(self.getfile)
        self.pushButton777.clicked.connect(self.getfolder)
        a=myreadconfig()
        self.lineEditvalue.setText(a[0])
        self.lineEdit777.setText(a[1])
    
    def GoCrazy(self):
        self.myThread = MyThread()
        self.myThread.text_valuepath = self.lineEditvalue.text()
        self.myThread.text_folderpath = self.lineEdit777.text()
        self.myThread.set_text.connect(self.on_set_text)
        
        self.pushButtonfix.setEnabled(False)
        self.myThread.start()

    def on_set_text(self, generated_str):
        print("Generated string : ", generated_str)
        self.label_st.setText(generated_str)
    
    def upconfig(self):
        mywriteconfig(self.lineEditvalue.text(), self.lineEdit777.text())
        
    def getfile(self):
        self.lineEditvalue.setText(QFileDialog.getOpenFileName(self, 'Open file', 'c:\\',"text files (*.txt *.*)"))
        self.upconfig()
    
    def getfolder(self):
        self.lineEdit777.setText(QFileDialog.getExistingDirectory(self, 'Select FF777 directory'))
        self.upconfig()

        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec_()
print "all done!"