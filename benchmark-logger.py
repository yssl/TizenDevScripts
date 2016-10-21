#!/usr/bin/env python
import os, datetime, time, sys
import multiprocessing as mp
import subprocess

'''
xrandr --output LVDS1 --mode 3840x2160@60    # set UHD

dlogutil DALI &     # print out log

DALI_FPS_TRACKING=1 /usr/apps/com.samsung.dali-demo/bin/perf-scroll.example --use-mesh --animate-parent -r15 -c15 -p10 -t20
DALI_FPS_TRACKING=1 /usr/apps/com.samsung.dali-demo/bin/perf-scroll.example --use-imageview --animate-parent -r15 -c15 -p10 -t20

DALI_FPS_TRACKING=1 /usr/apps/com.samsung.dali-demo/bin/perf-scroll.example --use-mesh --animate-parent -r1 -c1 -p2 -t10
'''

####################################
# settings

#copyToOutputDir = False
copyToOutputDir = True

repeatNum = 1
#repeatNum = 5

#duration = 1
#duration = 5
duration = 10
#duration = 20
#duration = 1200

device = 'hawkp'
#device = 'xu3'

#appname = 'benchmark'
appname = 'perf-scroll'

#resolution = 'FHD'
resolution = 'UHD'

#numopt = ''             # 625 images
#numopt = '-r20 -c20'    # 400 images
numopt = '-r15 -c15'    # 225 images * 13 pages

numopt1 = '-r1 -c1 -p2'    # 1 images * 2 pages
numopt2 = '-r1 -c1 -p10'    # 1 images * 10 pages
numopt3 = '-r5 -c5 -p2'    # 25 images * 2 pages
numopt4 = '-r15 -c15 -p2'    # 225 images * 5 pages
numopt5 = '-r15 -c15 -p5'    # 225 images * 5 pages
numopt6 = '-r15 -c15 -p10'    # 225 images * 10 pages
numopt7 = '-r15 -c15 -p20'    # 225 images * 20 pages
numopt8 = '-r20 -c20 -p20'    # 400 images * 20 pages
numopt9 = '-r30 -c30 -p20'    # 900 images * 20 pages

#typeopt = ''                # ImageActor
#typeopt = '--use-mesh'      # Use new renderer API (as ImageView) but shares renderers between actors when possible
#typeopt = '--use-imageview' # Use ImageView instead of ImageActor

appDir = '/usr/apps/com.samsung.dali-demo/bin/'

appArgus = [
        #'%s.example %s -t%d'%(appname, numopt, duration),
        #'%s.example %s -t%d --use-imageview'%(appname, numopt, duration),
        #'%s.example %s -t%d --use-mesh'%(appname, numopt, duration),

        #'%s.example %s -t%d --use-mesh'%(appname, numopt1, duration),
        #'%s.example %s -t%d --use-mesh'%(appname, numopt2, duration),
        #'%s.example %s -t%d --use-mesh'%(appname, numopt3, duration),
        #'%s.example %s -t%d --use-mesh'%(appname, numopt4, duration),
        #'%s.example %s -t%d --use-mesh'%(appname, numopt5, duration),
        #'%s.example %s -t%d --use-mesh'%(appname, numopt6, duration),
        #'%s.example %s -t%d --use-mesh'%(appname, numopt7, duration),

        #'%s.example %s -t%d --use-mesh --animate-parent'%(appname, numopt1, duration),
        #'%s.example %s -t%d --use-mesh --animate-parent'%(appname, numopt5, duration),
        #'%s.example %s -t%d --use-mesh --animate-parent'%(appname, numopt6, duration),
        #'%s.example %s -t%d --use-mesh --animate-parent'%(appname, numopt7, duration),

        #'%s.example %s -t%d --use-mesh --animate-parent'%(appname, numopt9, duration),
        'DALI_THREADING_MODE=0 %s.example %s -t%d --use-mesh --animate-parent'%(appname, numopt9, duration),

        #'%s.example %s -t%d --use-imageview --animate-parent'%(appname, numopt6, duration),
        ]

#modes = ['xdbg-fps', 'coregl-trace', 'dali-fps', 'dali-gles', 'ttrace']
#modes = ['xdbg-fps', 'dali-fps']   # both mode show similar results
#modes = ['xdbg-fps', 'coregl-trace', 'dali-gles', 'ttrace']
#modes = ['xdbg-fps', 'coregl-trace', 'dali-gles']
#modes = ['dali-fps']
#modes = ['coregl-trace']
#modes = ['dali-gles']
#modes = ['ttrace']
#modes = ['xdbg-fps']
modes = ['xdbg-fps--ttrace']
#modes = ['dali-fps--ttrace']

ttraceDir = '/media/Work/Code/TizenPackages/ttrace-tool/ttrace/'

outRootDir = './output/'
tempDir = './temp/'

# cpu affinity
#cpuAff = True
cpuAff = False 

if device=='xu3':
    cpuAff = False

##############
# settings for specific mode

# for xdbg-fps
beginAvgExclude = 9
endAvgExclude = 3
#beginAvgExclude = 0
#endAvgExclude = 0
minNumAvgEntries = 3

if cpuAff:
    for i in range(len(appArgus)):
        appArgus[i] = 'taskset -c 1,3 '+appArgus[i]


####################################

# sdb root on
os.system('sdb root on')

if device=='hawkp':
    # cpu affinity setting
    if cpuAff:
        tempFile = './temp.txt'
        for job, aff in affList.items():
            os.system('sdb shell "pgrep %s" > %s'%(job, tempFile))
            with open(tempFile, 'r') as f:
                pids = f.read().split()
                for pid in pids:
                    os.system('sdb shell "taskset -pc %s %s"'%(aff, pid))

    # set resolution
    if resolution=='UHD':
        os.system('sdb shell "xrandr --output LVDS1 --mode 3840x2160@60"')
    elif resolution=='FHD':
        os.system('sdb shell "xrandr --output LVDS1 --mode 1920x1080@60"')


# log start time / make log directory
startTime = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
outResultDir = os.path.expanduser(outRootDir+startTime)
if copyToOutputDir and not os.path.exists(outResultDir):
    os.makedirs(outResultDir)
if not os.path.exists(tempDir):
    os.makedirs(tempDir)

def post_process_xdbg_fps_log(logPath):
    # add average
    outLines = []
    with open(logPath, 'r') as f:
        lines = f.read().split('\n')

    # remove last line if empty
    if len(lines[len(lines)-1])==0:
        del lines[len(lines)-1]

    # remove non-fps log
    for i in range(len(lines)-1, -1, -1):
        if '[Xorg..V][LVDS][FB:(' not in lines[i]:
            del lines[i]

    enoughLines = len(lines) >= beginAvgExclude + endAvgExclude + minNumAvgEntries

    for i in range(len(lines)):
        if enoughLines and i==beginAvgExclude:
            outLines.append('--------------------------------')

        newLine = 'Line %2d: %s'%(i+1, lines[i])
        outLines.append(newLine)

        if enoughLines and i==len(lines)-1-endAvgExclude:
            outLines.append('--------------------------------')

    if enoughLines:
        fpss = []
        for line in lines[beginAvgExclude:len(lines)-endAvgExclude]:
            tokens = line.split()
            fps = float(tokens[2][:-5])
            fpss.append(fps)
        outLines.append('')
        outLines.append('Average FPS from line %d to line %d: %.1f'
                %(beginAvgExclude, len(lines)-1-endAvgExclude, sum(fpss)/float(len(fpss))))
    else:
        outLines.append('')
        outLines.append('Not enough lines to calculate stable average FPS. Needs more than %d lines.'
                %(beginAvgExclude+endAvgExclude+minNumAvgEntries))
    
    with open(logPath, 'w') as f:
        f.write('\n'.join(outLines))

def run_xdbg_fps(launchCmd, tempLogPath):
    # run
    os.system('''sdb shell "
    > /var/log/Xorg.0.log
    xdbg fpsdebug 1
    %s
    xdbg fpsdebug 0
    "'''%launchCmd)

    # pull
    os.system('sdb pull /var/log/Xorg.0.log "%s"'%tempLogPath)

    # postprocess
    post_process_xdbg_fps_log(tempLogPath)

def run_coregl_trace(launchCmd, tempLogPath):
    # run
    os.system('''sdb shell "
    export COREGL_TRACE_API=1
    %s &> /home/developer/coregl_ttrace
    export COREGL_TRACE_API=0
    "'''%launchCmd)

    # pull
    os.system('sdb pull /home/developer/coregl_ttrace "%s"'%tempLogPath)

def run_dali_fps(launchCmd, tempLogPath):
    # run
    os.system('''sdb shell "
    export DALI_FPS_TRACKING=1
    dlogutil -c
    dlogutil DALI > /home/developer/dali_fps &
    %s
    pkill dlogutil
    export DALI_FPS_TRACKING=0
    "'''%launchCmd)

    # pull
    os.system('sdb pull /home/developer/dali_fps "%s"'%tempLogPath)

def run_dali_gles(launchCmd, tempLogPath):
    # run
    os.system('''sdb shell "
    export DALI_GLES_CALL_TIME=1
    dlogutil -c
    dlogutil DALI > /home/developer/dali_gles &
    %s
    pkill dlogutil
    export DALI_GLES_CALL_TIME=0
    "'''%launchCmd)

    # pull
    os.system('sdb pull /home/developer/dali_gles "%s"'%tempLogPath)

def run_ttrace(launchCmd, tempLogPath):
    ttraceCmd = '%sttrace.py -b 10240 -o %s.html -t %d idle sched workq gfx am'%(ttraceDir, tempLogPath, duration)

    # run
    subprocess.Popen(['''sdb shell "
    export DALI_PERFORMANCE_TIMESTAMP_OUTPUT=4
    %s 
    "'''%launchCmd], shell=True)
    os.system(ttraceCmd)
    os.system('''sdb shell "
    pkill %s
    export DALI_PERFORMANCE_TIMESTAMP_OUTPUT=0
    "'''%appname)


def run_dali_fps__ttrace(launchCmd, tempLogPath):
    ttraceCmd = '%sttrace.py -b 10240 -o %s.html -t %d idle sched workq gfx am'%(ttraceDir, tempLogPath, duration)

    # run
    os.system('''sdb shell "
    export DALI_FPS_TRACKING=1
    dlogutil -c
    dlogutil DALI > /home/developer/dali_fps &
    DALI_PERFORMANCE_TIMESTAMP_OUTPUT=4 %s
    pkill dlogutil
    export DALI_FPS_TRACKING=0
    "'''%launchCmd)

    # run ttrace
    os.system(ttraceCmd)

    # pull
    os.system('sdb pull /home/developer/dali_fps "%s"'%tempLogPath)


def run_xdbg_fps__ttrace(launchCmd, tempLogPath):
    ttraceCmd = '%sttrace.py -b 10240 -o %s.html -t %d idle sched workq gfx am'%(ttraceDir, tempLogPath, duration)

    # run app
    subprocess.Popen(['''sdb shell "
    > /var/log/Xorg.0.log
    xdbg fpsdebug 1
    DALI_PERFORMANCE_TIMESTAMP_OUTPUT=4 %s
    xdbg fpsdebug 0
    "'''%launchCmd], shell=True)

    # run ttrace
    os.system(ttraceCmd)

    # pull
    os.system('sdb pull /var/log/Xorg.0.log "%s"'%tempLogPath)

    # postprocess
    post_process_xdbg_fps_log(tempLogPath)


def run(appDir, appArgu, appName, mode):
    for i in range(repeatNum):
        #launchCmd = appDir+appArgu
        pos = appArgu.find(appName)
        launchCmd = appArgu[:pos]+appDir+appArgu[pos:]

        outFileName = '[%s](%s)%s[%d].txt'%(mode, resolution, appArgu.replace('.example', ''), i)
        outFilePath = outResultDir+'/'+outFileName
        tempLogPath = tempDir+'/'+mode+'.txt'

        # run for each mode
        if mode=='xdbg-fps':
            run_xdbg_fps(launchCmd, tempLogPath)
        elif mode=='coregl-trace':
            run_coregl_trace(launchCmd, tempLogPath)
        elif mode=='dali-fps':
            run_dali_fps(launchCmd, tempLogPath)
        elif mode=='dali-gles':
            run_dali_gles(launchCmd, tempLogPath)
        elif mode=='ttrace':
            run_ttrace(launchCmd, tempLogPath)
        elif mode=='xdbg-fps--ttrace':
            run_xdbg_fps__ttrace(launchCmd, tempLogPath)
        elif mode=='dali-fps--ttrace':
            run_dali_fps__ttrace(launchCmd, tempLogPath)
        else:
            print 'Unknown mode: %s'%mode
            raise NotImplemented

        os.system('sdb shell "pkill %s"'%appname)

        if copyToOutputDir:
            if '--ttrace' in mode:
                os.system('cp "%s.html" "%s.html"'%(tempLogPath, outFilePath))
                os.system('cp "%s.html.trace" "%s.trace.html"'%(tempLogPath, outFilePath))
                os.system('cp "%s" "%s"'%(tempLogPath, outFilePath))
            elif mode=='ttrace':
                os.system('cp "%s.html" "%s.html"'%(tempLogPath, outFilePath))
                os.system('cp "%s.html.trace" "%s.html.trace"'%(tempLogPath, outFilePath))
            else:
                os.system('cp "%s" "%s"'%(tempLogPath, outFilePath))


for appArgu in appArgus:
    for mode in modes:
        run(appDir, appArgu, appname, mode)
