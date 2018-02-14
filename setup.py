# -*- coding: utf-8 -*-
"""
Created on Thu March 16 2017

@author: Wei Shuai <cpuwolf@gmail.com>
"""


import sys  
from cx_Freeze import setup, Executable  

build_exe_options = {"packages": ["os"], "excludes": [], "include_files": ["main.ui","ff777wingflex.cfg"]}
base = None  
if sys.platform == "win32":  
    base = "Win32GUI"  
setup(  
        name = "ff777wingflex",
        version = "1.0",  
        description = "a script to fix FF777 wingflex animation",  
		options = {"build_exe": build_exe_options}, 
        executables = [Executable("ff777wingflex.py")]) 