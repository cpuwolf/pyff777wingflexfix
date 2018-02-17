#!/bin/sh

#/Users/apple/Library/Python/2.7/bin/pyinstaller --windowed --onefile --clean --noconfirm ff777wingflex.py

/Users/apple/Library/Python/2.7/bin/pyinstaller  --onefile --clean --noconfirm ff777wingflex.spec

pushd dist
create-dmg ff777wingflexfixmac.app/
popd