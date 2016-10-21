import subprocess, os

#targetRootDir = './'
#targetRootDir = '/media/Work/Binary/PrebuildRPMs/2015-11-compare-node-native-fridge/2.4-tv-product/native-1.1.9/usr'
#targetRootDir = '/media/Work/Binary/PrebuildRPMs/2015-11-compare-node-native-fridge/2.4-tv-product/node-1.1.9/usr'
#targetRootDir = '/media/Work/Binary/PrebuildRPMs/2015-11-compare-node-native-fridge/3.0-tv-xu3/native-1.1.9-time-logger/usr'
targetRootDir = '/media/Work/Binary/PrebuildRPMs/2015-11-compare-node-native-fridge/3.0-tv-xu3/node-1.1.9-time-logger/usr'

targetFilePatterns = ['*.so','*.node','*fridge.example']

#################################
# get target file list
findopt = ''
for i in range(len(targetFilePatterns)):
    pattern = targetFilePatterns[i]
    findopt += '-ipath \''+pattern+'\' -print'
    if i < len(targetFilePatterns)-1:
        findopt += ' -o '

targetFilePaths = []
proc = subprocess.Popen(['find '+targetRootDir+' '+findopt], stdout=subprocess.PIPE, shell=True)
(out, err) = proc.communicate()
out = out.strip()
if len(out) > 0:
    targetFilePaths.extend(out.split('\n'))

for path in targetFilePaths:
    print '############################'
    print '# %s'%os.path.basename(path)
    proc = subprocess.Popen(['readelf -d %s | grep NEEDED'%path], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print out
