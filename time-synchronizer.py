#!/usr/bin/env python
import subprocess, os

# time-synchronizer.py
# - Set Tizen device's system time to your PC's one.
# 
# usage:
# 1. Make the device to be sdb connectable with your PC.
# 2. Run the script (./time-synchronize.py, if you made the file executable).

# Get root
os.system('sdb root on')

# Get current PC time
proc = subprocess.Popen(['LANG=en_US date -u'], stdout=subprocess.PIPE, shell=True)
(out_pc, err) = proc.communicate()
print 'Your PC time: %s'%out_pc

# Get current target time
proc = subprocess.Popen(['sdb shell "LANG=en_US date -u"'], stdout=subprocess.PIPE, shell=True)
(out_target, err) = proc.communicate()
print 'Current target time: %s'%out_target

# Set PC time to target
print 'Applying PC time to target...'
os.system('sdb shell "date --set \\"%s\\""'%out_pc)
print

# Get new target time
proc = subprocess.Popen(['sdb shell "LANG=en_US date -u"'], stdout=subprocess.PIPE, shell=True)
(out_target, err) = proc.communicate()
print 'New target time: %s'%out_target
