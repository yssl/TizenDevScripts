#!/usr/bin/env python
import os, datetime, time, sys
import multiprocessing as mp

# runtct.py v0.1
# usage: ./runtct.py [utc/ict] [package name] [tc start index] [tc end index]
#        [tc start index] and [tc end index] are optional.
#
# Before running the script, change tctRootPath to your local tct directory

# time out for each tc func (sec)
timeOut = 3

# tct root dir (local tct git)
tctRootPath = './tct/'

# log dir
log_directory = '~/runtct-log/'

tctType = sys.argv[1]
tctPackage = sys.argv[2]

if len(sys.argv) > 3:
    startIndex = int(sys.argv[3])
else:
    startIndex = 0

if len(sys.argv) > 4:
    endIndex = int(sys.argv[4])
else:
    endIndex = -1

###################################
# classes & functions
class MultiWriter:
    def __init__(self, *writers):
        self.writers = writers
    def write(self, text):
        for w in self.writers: 
            w.write(text)
    def close(self, text):
        for w in self.writers: 
            w.close(text)
    def flush(self):
        pass
    def close(self):
        pass
    
class DispFileWriter(MultiWriter):
    def __init__(self, filename, appending=True):
        self.logfile = file(filename, 'a' if appending else 'w')
        MultiWriter.__init__(self, sys.stdout, self.logfile)
    def flush(self):
        self.logfile.flush()
    def close(self):
        self.logfile.close()
        
class StdoutReplacer:
    def __init__(self, writer):
        self.stdout_saved = sys.stdout
        self.writer = writer
        self.on()
    def flush(self):
        self.writer.flush()
    def close(self):
        self.writer.close()
        self.off()
    def on(self):
        sys.stdout = self.writer
    def off(self):
        sys.stdout = self.stdout_saved
        
class DispFileStdoutReplacer(StdoutReplacer):
    def __init__(self, filename, appending=True):
        StdoutReplacer.__init__(self, DispFileWriter(filename, appending))
        
def execute(command, insertStr, writer):
    popen = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines_iterator = iter(popen.stdout.readline, "")
    for line in lines_iterator:
        print insertStr+line, # yield line
        writer.flush()
    retcode = popen.wait()
    return retcode

###################################
# prepare

log_directory = os.path.expanduser(log_directory)
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

gstarttime = datetime.datetime.now()
logname = gstarttime.strftime('%Y-%m-%d--%H-%M-%S')
logpath = os.path.join(log_directory, logname+'.txt')
stdreplacer = DispFileStdoutReplacer(logpath)

###################################
# main logic

totalstarttime = datetime.datetime.now()
print '================================================================================'
print 'runtct-main.py v0.1'
print 'usage: python runtct-main.py [utc/ict] [package name] [tc start index] [tc end index]'
print '       [tc start index] and [tc end index] are optional.'
print 'STARTED at %s'%totalstarttime
print '================================================================================'

os.system('sdb root on')

SUCCEEDED = 0
FAILED = 1
CRASHED = 2

def runtct(tctPackage, tcFuncName):
    result = SUCCEEDED
    errorcode = 0

    #ret = os.system('/opt/usr/apps/core-%s-tests/bin/tct-%s-core %s'%(tctPackage,tctPackage,tcFuncs[i]))
    #os.system('sdb shell "/opt/usr/apps/core-%s-tests/bin/tct-%s-core %s"'%(tctPackage,tctPackage,tcFuncName))

    # remove previous tc result
    os.system('sdb shell "rm /tmp/tcresult"')

    # execute a tc
    execute('sdb shell "/opt/usr/apps/core-%s-tests/bin/tct-%s-core %s"'%(tctPackage,tctPackage,tcFuncName))

    # pull tc result file
    pull_ret = os.system('sdb pull /tmp/tcresult /tmp')
    if pull_ret != 0:
        # if no tcresult file exists, then the tc function crashed (not finished correctly)
        result = CRASHED
    else:
        # check content of tcresult to know passed or failed
        with open('/tmp/tcresult') as f:
            errorcode = int(f.read())
            if errorcode != 0:
                result = FAILED
    return (result, errorcode)

pool = mp.Pool()

# get tc header file name
tctPath = tctRootPath+'src/'+tctType+'/'+tctPackage+'/'
tctHeader = tctPath+'tct-'+tctPackage+'-core.h'

# read tc header and get all tc func names
tcFuncs = []
with open(tctHeader, 'r') as f:
    code = f.read()
    codeLines = code.split('\n')
    for i in range(len(codeLines)):
        line = codeLines[i]
        tokens = line.split(' ')
        if len(tokens) > 2:
            if tokens[0]=='extern' and len(tokens[2])>7 and tokens[2][:7]=='UtcDali':
                tcFuncs.append(tokens[2].split('(')[0])

if endIndex == -1:
    endIndex = len(tcFuncs)-1

# start
starttime = datetime.datetime.now()
print '============================================================'
print 'STARTED at %s'%starttime
print 'Run %d %s for %s ([%d]~[%d])'%(endIndex-startIndex+1, tctType, tctPackage, startIndex, endIndex)
print

numPass = 0
for i in range(startIndex, endIndex+1):

    # sleep is required to avoid unclear exception maybe due to 
    # too many executions of sdb commands
    time.sleep(.1)

    result = pool.apply_async(runtct, args=(tctPackage, tcFuncs[i]))

    try:
        # only wait for timeOut
        result, errorcode = result.get(timeout=timeOut)
    except mp.TimeoutError:
        # time out means fail
        msg = 'Fail - exceeded %d sec timeout'%timeOut
    else:
        # else
        if result == CRASHED:
            msg = 'Fail - crashed'
        elif result == FAILED:
            msg = 'Fail - exit code %d'%errorcode
        else:
            msg = 'Pass'
            numPass += 1
    print '[%d] %s'%(i, tcFuncs[i])
    print ': %s'%(msg)
    print

endtime = datetime.datetime.now()
print 'FINISHED at %s'%endtime
print 'Run %d %s for %s ([%d]~[%d])'%(endIndex-startIndex+1, tctType, tctPackage, startIndex, endIndex)
print 'Pass / Total: %d / %d'%(numPass, endIndex-startIndex+1)
print 'Fail / Total: %d / %d'%(endIndex-startIndex+1-numPass, endIndex-startIndex+1)
print '============================================================'
print
