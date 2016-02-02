#!/usr/bin/env python
import os
import numpy as np

# LaunchingTimeLogger
#
# summarizer.py
# - Summarize raw log files.
# 
# Usage:
# 1. Check ./output dir has raw log files (e.g. 2015-12-22--09-37-14.txt, ...)
#    or sub directories only.
# 2. If so, just run the script.
#
# Summary file example:
# 
#   # Command: (your command)
#   
#   # Milliseconds since invoking command
#   # Number of data: 20
#                                                 AVG (DIFF)    MIN    MAX
#   Invoking command                        :       0    175      0      0
#   Begin main()                            :     175      3    142    233
#   Begin HelloWorldController()            :     178      0    148    235
#   End__ HelloWorldController()            :     178      0    149    235
#   Begin MainLoop()                        :     178     35    149    236
#   Begin OnInit()                          :     213      5    183    271
#   End__ OnInit()                          :     218     65    188    278
#   Begin first SwapBuffers() call          :     283      8    241    329
#   End__ first SwapBuffers() call          :     291           250    337

outDir = './output/'

print '# Summarizing...'

categorizedFileNames = {}
for fileName in os.listdir(outDir):
    if not os.path.isdir(outDir+fileName):
        tokens = fileName.split('-')
        mode = tokens[0]
        if mode not in categorizedFileNames:
            categorizedFileNames[mode] = []

        categorizedFileNames[mode].append(fileName)

for category, fileNames in categorizedFileNames.items():
    summaryPath = '%s/%s--summary.txt'%(outDir, category)
    labelSet = []
    valueSet = []

    # read & sum
    for f in range(len(fileNames)):
        fileName = fileNames[f]
        labels = []
        values = []
        with open(outDir+fileName, 'r') as file:
            print 'processing %s...'%fileName
            lines = file.read().split('\n')
            commandLine = ''
            dataSection = False
            for line in lines:
                if '# Command:' in line:
                    commandLine = line

                elif line == '# Milliseconds since invoking command':
                    dataSection = True
                    labels.append(commandLine)
                    labels.append('')
                    labels.append(line)
                    labels.append('# Number of data: %d'%len(fileNames))
                    labels.append('%-40s  %7s%7s%7s%7s'%('','AVG','(DIFF)','MIN','MAX'))
                    values.extend([-1]*5)

                elif dataSection:
                    tokensLine = line.split(':')
                    label = tokensLine[0]
                    value = int(tokensLine[1])

                    if len(labels)>0 and labels[-1]==label:
                        continue

                    labels.append(label)
                    values.append(value)

        ## manipulate swap buffer record
        #swapBufferStartIndex = -1
        #swapBufferEndIndex = -1
        #prevValue = -1
        #diffTime = -1
        #for l in range(len(labels)):
            #label = labels[l]

            #if swapBufferStartIndex==-1:
                #if '1th SwapBuffers()' in label:
                    #swapBufferStartIndex = l
                    #prevValue = values[l]
            #else:
                #if l > swapBufferStartIndex:
                    #diffTime = values[l]-prevValue
                    #prevValue = values[l]

                    #if diffTime > 1000: # for hawkp native later swapbuffering
                        #swapBufferEndIndex = l-1
                        #break

        #if swapBufferEndIndex==-1:
            #swapBufferEndIndex = len(labels)-1

        #labels = labels[:swapBufferStartIndex+2]+labels[swapBufferEndIndex+1-2:swapBufferEndIndex+1]
        #values = values[:swapBufferStartIndex+2]+values[swapBufferEndIndex+1-2:swapBufferEndIndex+1]
        #labels[-4] = 'Begin first SwapBuffers() call'
        #labels[-3] = 'End__ first SwapBuffers() call'
        #labels[-2] = 'Begin last SwapBuffers() call'
        #labels[-1] = 'End__ last SwapBuffers() call'

        labelSet.append(labels)
        valueSet.append(values)

    #exit()

    # calc & write
    numFiles = len(fileNames)
    numLabels = len(labelSet[0])
    dataMat = np.zeros((numLabels, numFiles))
    for f in range(numFiles):
        for l in range(numLabels):
            dataMat[l,f] = valueSet[f][l]

    with open(summaryPath, 'w') as file:
        for l in range(numLabels):
            label = labelSet[0][l]
            if dataMat[l,0] == -1:
                file.write('%s\n'%label)
            else:
                avgValue = np.average(dataMat[l,:])
                minValue = np.min(dataMat[l,:])
                maxValue = np.max(dataMat[l,:])

                if l==numLabels-1:
                    file.write('%-40s: %7d%7s%7d%7d\n'%(label, avgValue, '', minValue, maxValue))
                else:
                    nextAvgValue = np.average(dataMat[l+1,:])
                    file.write('%-40s: %7d%7d%7d%7d\n'%(label, avgValue, int(nextAvgValue)-int(avgValue), minValue, maxValue))
