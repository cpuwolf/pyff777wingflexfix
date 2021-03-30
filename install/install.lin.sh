#!/bin/sh

#/Users/apple/Library/Python/2.7/bin/pyinstaller --windowed --onefile --clean --noconfirm ff777wingflex.py

push ..
pyinstaller  --onefile --clean --noconfirm ../ff777wingflex.spec

