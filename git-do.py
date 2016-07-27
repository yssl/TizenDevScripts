#!/usr/bin/env python
import os, sys

argstr = ''
for i in range(len(sys.argv)):
    if i==0:
        continue
    argstr += sys.argv[i] + ' '

cwd = os.getcwd()
for subdir in os.listdir(cwd):
    fullsub = os.path.join(cwd,subdir)
    if os.path.isdir(fullsub):
        if '.git' in os.listdir(fullsub):
            #print 'cd %s;git %s'%(subdir, argstr)
            print
            print '## %s'%subdir
            os.system('cd %s && git %s'%(subdir, argstr))
