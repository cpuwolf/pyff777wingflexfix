# -*- coding: utf-8 -*-
"""
Created on Thu March 16 2017

@author: Wei Shuai <cpuwolf@gmail.com>
"""

from distutils.core import setup  
import py2exe
import sys  
includes = ["encodings", "encodings.*"]    
sys.argv.append("py2exe")  
options = {"py2exe":   { "bundle_files": 1 }    
                }   
setup(
    version = "1.0.0",
    description = "a script to fix FF777 wingflex animation",
    name = "FF777 wingflex patch tool",
    options = options,  
    zipfile=None,   
    console = [{"script":'ff777wingflex.py'}])
