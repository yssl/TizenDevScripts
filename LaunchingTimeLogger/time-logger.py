#!/usr/bin/env python
import os, time, subprocess, datetime

# LaunchingTimeLogger
#
# time-logger.py
# - Measure launching time speed of your app on a Tizen device.
#
# Usage:
# 1. Make the device sdb connectable with your PC.
#
# 2. Define time checking points on your app code. For example,
#   - Before main() starts
#   - When initialization event received
#   - Before UI layout is built
#   - After UI layout is built
#   - Before first rendering call (swapbuffer call)
#   - After first rendering call (swapbuffer call)
#   - Before/after other potentially time-consuming code blocks
#
# 3. Add code to print out current time (UNIX epoch time - since 1970.1.1) with the logging keyword
#    by using cout or printf (for stdout print out) or dlog_print or DALI_LOG_ERROR (for Tizen dlog)
#    Default logging keyword: (time-logger)
#
#   (cpp example)
#   #include <sys/time.h>
#   unsigned long long getMS()
#   {
#     struct timeval tv;
#     gettimeofday(&tv, NULL);
#     unsigned long long millisecondsSinceEpoch =
#       (unsigned long long)(tv.tv_sec) * 1000 +
#       (unsigned long long)(tv.tv_usec) / 1000;
#     return millisecondsSinceEpoch;
#   }
#   ...
#   void AnotherFunction()
#   {
#     cout << endl << "(time-logger)Begin DoSomething: " << getMS() << endl;   // or
#     DALI_LOG_ERROR("(time-logger)Begin DoSomething: %llu  ", getMS());       // or
#     dlog_print(DLOG_ERROR, "DALI", "(time-logger)Begin DoSomething: %llu  ", getMS());
#
#     DoSomething();
#
#     cout << endl << "(time-logger)End__ DoSomething: " << getMS() << endl;   // or
#     DALI_LOG_ERROR("(time-logger)End__ DoSomething: %llu  ", getMS());       // or
#     dlog_print(DLOG_ERROR, "DALI", "(time-logger)End__ DoSomething: %llu  ", getMS());
#   }
#   
#   reference: 
#       https://review.tizen.org/gerrit/#/c/54831/
#
#   (js example)
#   console.log('\n(time-logger)Begin doSomething: '+Math.floor(Date.now()));
#   doSomething();
#   console.log('\n(time-logger)End__ doSomething: '+Math.floor(Date.now()));   
#
# 4. Update the value of cwdOnDevice, cmdOnDevice, killCmds (mandatory).
#
# 5. Update the value of outDir, timeOut, trialInterval, repeatNum if you need (optional).
#
# 6. Run the script.
#
# 7. Log files are generated in ./output. After all trial finished, run summarizer.py to get summarized result.
#
# How it works:
# 1. Push time-logger-device.sh to device.
# 2. Run the specified command via time-logger-device.sh on the device. (to record command invoking time)
# 3. All printed out logs are saved to temp file on the device and then pulled to host PC.
# 4. Look through the log file and append time-logger logs only again to the end of the log file.
# 5. Repeat step 2 ~ 4 for given repitition count.
# 5. summarizer.py reads all host PC log files and calculates & prints avg, max, min of each time item.

#########################################
# Setting variables

# Output dir in which log files generated.
outDir = './output/'

# Time out for each trial (sec).
timeOut = 2.

# Time interval between end of prev trial and begin of next trial.
trialInterval = 1.

# Number of trials
repeatNum = 10


# Current working directory on which cmdOnDevice will be run.
#cwdOnDevice = '/home/developer/dali-1.1.14-node/hello-button/'
#cwdOnDevice = '/home/developer/dali-1.1.14-node/bee-test/'
cwdOnDevice = '/home/developer/'

# Command that will be invoked on Tizen device to excute the trial.
#cmdOnDevice = 'XDG_RUNTIME_DIR=/run node hello-button.js'
#cmdOnDevice = 'su - owner -c \\\\\\"app_launcher -s test-hello-button.example\\\\\\"'
cmdOnDevice = 'su - owner -c \\\\\\"app_launcher -s org.example.test-hello-button\\\\\\"'

# Logging command 
#logCmd = 'dlogutil DALI'
#logCmd = 'dlogutil | grep DALI'
#logCmd = 'journalctl -f'
logCmd = 'journalctl -f LOG_TAG=DALI'

# Commands to kill processes relevant to previous trial.
killCmds = [
        'pkill -9 node',
        'pkill -9 test-hello',
        'pkill -9 journalctl',
        ]

#########################################
# Logic

# root on
os.system('sdb root on')

# push time-logger-device.sh to device
os.system('sdb push time-logger-device.sh /home/developer')

os.system('sdb shell "export XDG_RUNTIME_DIR=/run"')

for r in range(repeatNum):
    #####################
    # running & logging

    # host log file names are determined from current time
    nowTime = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
    logPath = '%s/%s.txt'%(outDir, nowTime)

    # start logging on device (non-blocking call)
    subprocess.Popen(['''sdb shell "%s > /home/developer/temp.txt"'''%logCmd],
            shell=True)

    # start target application (cmdOnDevice) on device via time-logger
    # to record command invoking time as well (non-blocking call)
    subprocess.Popen(['''sdb shell "
            cd %s
            /home/developer/time-logger-device.sh %s" > %s'''
            %(cwdOnDevice, cmdOnDevice, logPath)], shell=True)
    time.sleep(timeOut)

    # once the timeOut reached, then kill all processes.
    for killCmd in killCmds:
        os.system('sdb shell "%s"'%killCmd)

    # wait trialInterval before next trial
    time.sleep(trialInterval)

    # pull log file on device
    os.system('sdb pull /home/developer/temp.txt temp.txt')
    # convert device log file to host log file
    os.system('cat temp.txt >> %s'%logPath)

    #####################
    # postprocess log

    # collect all logged lines containing the logging keyword and store them to timeLines
    timeLines = []
    with open(logPath, 'r') as f:
        lines = f.read().split('\n')
        start = False
        for i in range(len(lines)):
            line = lines[i]
            if '(time-logger)' in line:
                pos = line.find('(time-logger)')
                timeLines.append(line[pos:])

    # choose logged lines only after 'Invoking command' time and store them to newLines,
    # because older logs can be shown by journalctl or dlogutil.
    newLines = []
    for i in range(len(timeLines)):
        if len(timeLines[i])==0:
            continue
        tokens = timeLines[i].split(':')
        label = tokens[0].replace('(time-logger)','')
        try:
            elapsedTime = int(tokens[1].split()[0])
        except ValueError:
            print timeLines[i]
            print 'ValueError'
            exit()

        if label == 'Invoking command':
            startTime = elapsedTime

        if elapsedTime-startTime >= 0:
            newLine = '%s: %d'%(label, elapsedTime-startTime)
            newLines.append(newLine)

    # append lines in newLines to the end of the host log file
    with open(logPath, 'a') as f:
        f.write('\n')
        f.write('# Milliseconds since invoking command\n')
        f.write('\n'.join(newLines))
