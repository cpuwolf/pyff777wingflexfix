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
import shutil, errno
import sys
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import QThread
from PyQt4.QtGui import QFileDialog
import ConfigParser
import logging
import tempfile
from appdirs import *


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

def checkxpobj(data):
    a=findwholeline(data,"wing_tip_deflection_deg",0)
    b=findwholeline(data,"vz_acf_axis",0)
    if a[0] == -1 and a[1] == -1 and b[0] == -1 and b[1] == -1:
        return True
    return False;
        

def processxpobj(fileobj,cklist):
    listmerge = []
    
    with open(fileobj,"rU") as f:
        data = f.read()
        
        if not checkxpobj(data):
            return False

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
    return True

def loadinputfile(filetxt):
    cookies = []
    wewant = []
    try:
        with open(filetxt,"rU") as f:
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
    written = 0
    for path, dirs, files in os.walk(root):
        for file in files:
            if file.endswith(".obj"):            # this line is new
                print os.path.join(path, file)
                if processxpobj(os.path.join(path, file),cklist):
                    written += 1
                else:
                    return -1;
    return written

def backupfolder(src):
    try:
        shutil.copytree(src, src+".flex.old")
        return 1
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            return 0
        return -1

def user_path(relative_path):
    base_path = user_data_dir("ff777wingflex","cpuwolf")
    if not os.path.exists(base_path):
        os.makedirs(base_path, 0o777)
    mpath = os.path.join(base_path, relative_path)
    return mpath


    
def resource_path(relative_path): # needed for bundling
    mpath = user_path(relative_path)
    if os.path.exists(mpath):
        return mpath
                                                                                                                     
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

#chklist=loadinputfile("F:\\works\\GitHub\\ff777wingflex\\FF777 Flex Values.txt")
'''chklist=[["WingPress","hello"],["EngRPress","hello"]]'''
#findxpobj("C:\\Program Files\\X-Plane 11\\Aircraft\\Extra Aircraft\\Boeing777-Extended\\objects",chklist)

def myreadconfig():
    config = ConfigParser.RawConfigParser()
    config.read(resource_path('ff777wingflex.cfg'))
    return [config.get('basic', 'inputfile'),config.get('basic', 'outputfolder')]

        
def mywriteconfig(ifile,ofolder):
    config = ConfigParser.RawConfigParser()
    config.add_section('basic')
    config.set('basic', 'inputfile', ifile)
    config.set('basic', 'outputfolder', ofolder)
    with open(user_path('ff777wingflex.cfg'), 'wb') as configfile:
        config.write(configfile)

class MyThread(QThread):
    set_text = QtCore.pyqtSignal('QString')
    set_done = QtCore.pyqtSignal()
    def __init__(self):
        QThread.__init__(self)
        self.text_valuepath = None
        self.text_folderpath = None
    def __del__(self):
        self.wait()
    def run(self):
        self.set_text.emit("<h1>please wait...</h1>")
        chklist=loadinputfile(self.text_valuepath)
        if len(chklist) <= 0:
            self.set_text.emit("<h1>input file error</h1>")
            self.set_done.emit()
            return
        objfolderpath=os.path.abspath(self.text_folderpath)
        ret=backupfolder(objfolderpath)
        if ret < 0:
            self.set_text.emit("<h1>folder backup failed!!</h1>")
            self.set_done.emit()
            return
        elif ret == 0:
            self.set_text.emit("<h1>Don't run multiple times!</h1>")
            self.set_done.emit()
            return
        self.set_text.emit("<h1>start to process...</h1>")
        ret = findxpobj(objfolderpath,chklist)
        if ret > 0:
            self.set_text.emit("<h1>finished!!<br>"+str(ret)+" files are changed</h1>")
        elif ret == 0:
            self.set_text.emit("<h1>nothing is changed</h1>")
        else:
            self.set_text.emit("<h1>Don't run multiple times</h1>")
        self.set_done.emit()

#debug_logger = logging.getLogger('wingflex')
#debug_logger.write = debug_logger.debug    #consider all prints as debug information
#debug_logger.flush = lambda: None   # this may be called when printing
#sys.stdout = debug_logger
sys.stdout = tempfile.TemporaryFile()

qtCreatorFile = "main.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(resource_path(qtCreatorFile))

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
        print "start"
        self.myThread = MyThread()
        self.myThread.text_valuepath = self.lineEditvalue.text()
        self.myThread.text_folderpath = unicode(self.lineEdit777.text())
        self.myThread.set_text.connect(self.on_set_text)
        self.myThread.set_done.connect(self.on_set_done)
        self.pushButtonfix.setEnabled(False)
        self.myThread.start()

    def on_set_done(self):
        self.pushButtonfix.setEnabled(True)

    def on_set_text(self, generated_str):
        #print("on_set_text:", generated_str)
        self.label_st.setText(generated_str)
    
    def upconfig(self):
        mywriteconfig(self.lineEditvalue.text(), self.lineEdit777.text())
        
    def getfile(self):
        self.lineEditvalue.setText(QFileDialog.getOpenFileName(self, 'Open file', self.lineEditvalue.text(),"text files (*.txt *.*)"))
        self.upconfig()
    
    def getfolder(self):
        self.lineEdit777.setText(QFileDialog.getExistingDirectory(self, 'Select FF777 directory',unicode(self.lineEdit777.text())))
        self.upconfig()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec_()
print "all done!"