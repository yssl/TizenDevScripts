#!/usr/bin/env python
import os, time

# LaunchingTimeLogger
#
# rpm-installer.py
# - Helper script for repetitive installation of sets of rpms. Edit and use it if you need.

#mode = 'node'
mode = 'native'

device = 'xu3'

localDir = '/media/Work/Binary/PrebuildRPMs/2015-12-launching-3.0/'

if device=='xu3':
    rpmDirOnPC = {
            'node':'%s/dali-1.1.14-node/'%localDir,
            'native':'%s/dali-1.1.14/'%localDir
            }

rpmDirOnDevice = {
        'node':'/home/developer/dali-1.1.14-node/',
        'native':'/home/developer/dali-1.1.14/'
        }

os.system('sdb root on')
os.system('sdb shell "mkdir /home/developer"')

os.system('sdb push %s/*.rpm %s'%(rpmDirOnPC[mode], rpmDirOnDevice[mode]))
os.system('sdb push %s/*.tpk %s'%(rpmDirOnPC[mode], rpmDirOnDevice[mode]))
os.system('sdb push %s/*.tar %s'%(rpmDirOnPC[mode], rpmDirOnDevice[mode]))

if device == 'xu3':
    os.system('''sdb shell "
    mkdir %s
    cd %s
    rpm -Uvh --force --nodeps *.rpm
    su - owner -c \\"pkgcmd -i -t tpk -q -p %s/*.tpk\\"
    #pkg_initdb
    su - owner -c \\"aul_test reload\\"
    "'''%(rpmDirOnDevice[mode], rpmDirOnDevice[mode], rpmDirOnDevice[mode]))

if mode=='node':
    os.system('''sdb shell "
    cd %s
    cat *.tar | tar -xvf - -i
    "'''%rpmDirOnDevice[mode])
