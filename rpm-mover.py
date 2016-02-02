#!/usr/bin/env python
import os, glob

# rpm-mover.py
# - Move debug & devel rpms to ./debug & ./devel.
# 
# usage:
# 1. cd to a directory having a bunch of rpm files.
# 2. Run the script.
#
# tips:
# - Give the script file execute permission using chmod +x,
#   then you can just run it by ./rpm-mover.py.
# - It would be more convinent if you add the directory having
#   this script to PATH environment variable.
#   ex) export PATH=$PATH:'/home/yourhome/your-script-dir'

try:
    os.mkdir('debug')
except OSError:
    pass
try:
    os.mkdir('devel')
except OSError:
    pass

for fileName in os.listdir('./'):
    if not os.path.isdir(fileName) and '.rpm' in fileName:
        if 'debug' in fileName:
            os.system('mv %s debug/%s'%(fileName, fileName))
        elif 'devel' in fileName:
            os.system('mv %s devel/%s'%(fileName, fileName))
