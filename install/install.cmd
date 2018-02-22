set PATH=%PATH%;F:\WinPython-32bit-2.7.10.2\python-2.7.10
cd F:\works\GitHub\pyff777wingflexfix\


::python.exe setup.py build
::bdist_msi


::python.exe -m PyInstaller  --windowed --icon=777.ico --onefile --clean --noconfirm ff777wingflex.py

python.exe -m PyInstaller  --version-file=file_version_info.txt --windowed --onefile --clean --noconfirm ff777wingflex.spec

pause