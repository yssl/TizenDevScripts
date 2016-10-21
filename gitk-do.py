#!/usr/bin/env python
import os,sys, time
import subprocess

wins = ['terminal','dali-core','dali','dali-adaptor','dali-toolkit','dali-demo']

openedwins = []
for win in wins:
    if win=='terminal': 
        openedwins.append(win)
        continue
    try:
        subprocess.Popen('gitk', cwd='./%s'%win)
        openedwins.append(win)
        time.sleep(.2)
    except OSError as e:
        print e

# git window size
#w = 960
w = 700
h = 540-20

# screen resolution
sw = 1920
sh = 1080 

win_pos_size = {}
win_pos_size['terminal'] = (w*2,0,sw-w*2,sh)
win_pos_size['dali-core'] = (0,0,w,h)
win_pos_size['dali'] = (0,0,w,h)
win_pos_size['dali-adaptor'] = (w,0,w,h)
win_pos_size['dali-toolkit'] = (0,h,w,h)
win_pos_size['dali-demo'] = (w,h,w,h)

# time to open all git windows
time.sleep(2.5)

# gitk windows
wmctrl_output = subprocess.check_output("wmctrl -l", shell=True)
wmctrl_token = wmctrl_output.split('\n')
for i in range(len(openedwins)):
    win = openedwins[i]
    #print wmctrl_token[-2-len(wins)+1+i]
    win_id = wmctrl_token[-2-len(openedwins)+1+i].split()[0]
    os.system('wmctrl -i -r "%s" -e 0,%s,%s,%s,%s'%(win_id, win_pos_size[win][0],win_pos_size[win][1],win_pos_size[win][2],win_pos_size[win][3]))
