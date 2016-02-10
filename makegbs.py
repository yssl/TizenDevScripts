#!/usr/bin/env python
import os, sys, time, glob, datetime
import argparse, traceback

##########################
# user setting

projs = ['dali','dali-core','dali-adaptor','dali-toolkit','dali-demo','homescreen-lite','homescreen','volt-engine','dali-menu','direct-rpm-install','direct-pkg-install']

gbsconf_file = '~/.gbs.conf'
devicehome_dir = '/home/developer'
#devicehome_dir = '/home/root'
local_obs_config_dir = os.path.dirname(__file__)+'/'
copy_addon_rpms_dir = '~/copy_addon_rpms/'

#copyrpm_dest = '/media/yoonsang/14_04_AMD64/copyrpm/'
copyrpm_dest = '~/Download/dali-rpm/'

install_device_cmds                       = {}

install_device_cmds['dali']               = 'rpm -Uvh --force --nodeps'
install_device_cmds['dali-core']          = 'rpm -Uvh --force --nodeps'
install_device_cmds['dali-adaptor']       = 'rpm -Uvh --force --nodeps'
install_device_cmds['dali-toolkit']       = 'rpm -Uvh --force --nodeps'
#install_device_cmds['dali']               = 'pkgcmd -i -t rpm -q -p'
#install_device_cmds['dali-core']          = 'pkgcmd -i -t rpm -q -p'
#install_device_cmds['dali-adaptor']       = 'pkgcmd -i -t rpm -q -p'
#install_device_cmds['dali-toolkit']       = 'pkgcmd -i -t rpm -q -p'

#install_device_cmds['dali-demo']          = 'pkgcmd -i -t rpm -q -p'
install_device_cmds['dali-demo']          = 'rpm -Uvh --force --nodeps'

install_device_cmds['homescreen']         = 'pkgcmd -i -t rpm -q -p'
#install_device_cmds['homescreen']         = 'rpm -Uvh --force --nodeps'

install_device_cmds['volt-engine']        = 'rpm -Uvh --force --nodeps'
install_device_cmds['dali-menu']          = 'pkgcmd -i -t rpm -q -p'
install_device_cmds['direct-rpm-install'] = 'rpm -Uvh --force --nodeps'
install_device_cmds['direct-pkg-install'] = 'pkgcmd -i -t rpm -q -p'

#install_device_cmds['homescreen-lite']    = 'pkgcmd -i -t rpm -q -p'


#raw_gbsopts                    = {}
#raw_gbsopts['dali']            = '--define "%enable_dali_smack_rules 1"'
#raw_gbsopts['dali-core']       = '--define "%enable_dali_smack_rules 1"'
#raw_gbsopts['dali-adaptor']    = '--spec dali-adaptor-mobile.spec'
#raw_gbsopts['dali-toolkit']    = '--define "%enable_dali_smack_rules 1"'
#raw_gbsopts['dali-demo']       = '--define "%enable_dali_smack_rules 1"'
#raw_gbsopts['homescreen-lite'] = ''
#raw_gbsopts['volt-engine']            = ''

plugin_rpms = {}
#plugin_rpms['dali-toolkit'] = ['dali-toolkit-dali-script-plugin-v8']

addon_rpms = {}
addon_rpms['dali'] = ['dali','dali-devel','dali-integration-devel']
addon_rpms['dali-core'] = ['dali','dali-devel','dali-integration-devel']
addon_rpms['dali-adaptor'] = ['dali-adaptor','dali-adaptor-devel']
addon_rpms['dali-toolkit'] = ['dali-toolkit','dali-toolkit-devel']

##########################
# parser
parser = argparse.ArgumentParser()
parser.add_argument('argv', nargs='+')
parser.add_argument('-P', nargs='?', default='')
parser.add_argument('-D', nargs='?', default='')
parser.add_argument('-A', nargs='?', default='')
parser.add_argument('-R', nargs='?', default='')
args = parser.parse_args()
#print args
#exit()
args.argv.insert(0,None)

##########################
# read .gbs.conf (extract gbsopts)

import ConfigParser
gbsconf = ConfigParser.SafeConfigParser()
gbsconf.read(os.path.expanduser(gbsconf_file))

if args.P=='':
    try:
        profile = gbsconf.get('general', 'profile')
    except:
        profile = 'profile-direct-install'
else:
    profile = args.P
local_obs_config_file = args.D
direct_rpm_file = args.R
architecture = args.A

if profile!='profile-direct-install':
    buildroot = gbsconf.get(profile, 'buildroot')

    repos_str = gbsconf.get(profile, 'repos')
    repos_list = repos_str.split(', ')
    repos = repos_list[0]

    url = gbsconf.get(repos, 'url')
    #print url
else:
    buildroot = ''
    repos = ''
    url = ''


#if 'download.tizen.org' in url: # tizen.org
    #gbsopts = raw_gbsopts

#elif '168.219.209.55' in url:   # spin server
    #local_obs_config_file = local_obs_config_dir

    #if '2.3' in url:
        #local_obs_config_file += '23'
    #elif '2.4' in url:
        #local_obs_config_file += '24'

    #if 'mobile' in url:
        #local_obs_config_file += '_mobile'
    #elif 'wearable' in url:
        #local_obs_config_file += '_wearable'

    #if 'emulator' in url:
        #local_obs_config_file += '_emulator'
    #elif 'target' in url:
        #local_obs_config_file += '_target'

    #if not os.path.exists(local_obs_config_file):
        #print 'Local obs config file %s does not exist'%local_obs_config_file
        #exit(1)

    #gbsopts = {}
    #for proj in projs:
        #gbsopts[proj] = '-D %s'%local_obs_config_file

#elif '168.219.244.109' in url:   # tv
    #gbsopts = {}
    #for proj in projs:
        #gbsopts[proj] = ''

#if 'emulator' in url:
    #architecture = 'i586'
#else:
    #architecture = 'armv7l'

gbsopts = {}
for proj in projs:
    gbsopts[proj] = ''
    gbsopts[proj] += '-P %s -D %s -A %s'%(profile, local_obs_config_file, architecture)

#if '168.219.244.109' in url:   # tv
    ##if 'dali-adaptor' in gbsopts:
        ##gbsopts['dali-adaptor'] += ' --define "%profile tv"'
    #if 'dali-toolkit' in gbsopts:
        #gbsopts['dali-toolkit'] += ' --define "%dali_toolkit_v8_plugin 1"'


##########################
# read .spec (extract Name, Version, Release from .spec)

exist_projs = []

def getNameFromSpec(specfile):
    f = open(specfile, 'r')
    for line in f:
        if(line.split(':')[0]=='Name'):
            return line.split()[1].strip()
def getVersionFromSpec(specfile):
    f = open(specfile, 'r')
    for line in f:
        if(line.split(':')[0]=='Version'):
            return line.split()[1].strip()
def getReleaseFromSpec(specfile):
    f = open(specfile, 'r')
    for line in f:
        if(line.split(':')[0]=='Release'):
            return line.split()[1].strip()
package_names = {}
versions = {}
releases = {}
for proj in projs:
    packaging_dir = './%s/packaging/'%proj
    specfiles = glob.glob(packaging_dir+'*.spec')
    for specfile in specfiles:
        exist_projs.append(proj)
        if proj not in package_names:
            package_names[proj] = []
            versions[proj] = []
            releases[proj] = []
        package_names[proj].append(getNameFromSpec(specfile))
        versions[proj].append(getVersionFromSpec(specfile))
        releases[proj].append(getReleaseFromSpec(specfile))
    #else:
        #print 'Any files like %s*.spec do not exist'%packaging_dir

##########################
# parse cmd arguments

maketarget = args.argv[1]

target_proj = ''
if len(args.argv) > 2:
    filepath = args.argv[2]

    if 'direct-rpm-install/' in filepath:
        target_proj = 'direct-rpm-install'
    elif 'direct-pkg-install/' in filepath:
        target_proj = 'direct-pkg-install'
    else:
        for proj in exist_projs:
            if proj+'/' in filepath:
                target_proj = proj 
                break

        if target_proj=='':
            print 'cannot recognize project of %s.'%filepath

selected_proj = target_proj if target_proj!='' else '('+exist_projs.__str__()+')'

##########################
# print info

start_time = datetime.datetime.now()
print '================================================================================'
print 'makegbs.py'
print
print 'STARTED at %s'%start_time
print '%% makegbs.py %s %s'%(maketarget, selected_proj)
print '================================================================================'
print

print 'Activated GBS Configuration:'
print '  profile:       ', profile
print '  repos:         ', repos 
print '  buildroot:     ', buildroot 
print '  architecture:  ', architecture
print '  url:           ', url 
print 

print 'Exec Info:'
print '  CWD :', os.getcwd()
cmdstr = 'full: $ python '
for arg in sys.argv:
    cmdstr += arg + ' '
print '  '+cmdstr
print

print 'Project Info:'
print '  Selected Project: ', selected_proj
print '  Existing Projects:', exist_projs
print '  All Projects:     ', projs
print

##########################
# auto generated dictionaries (rpmpaths, rpm_files, 

rpm_files = {}
rpm_filepaths = {}

if profile!='profile-direct-install':
    rpm_dir = '%s/local/repos/%s/%s/RPMS/'%(os.path.expanduser(buildroot), profile.split('.')[1], architecture)
    #print rpmpath

    addon_rpm_filepaths = {}
    #rpm_infixes = ['','debuginfo-','debugsource-']
    rpm_infixes = ['']
    for proj in exist_projs:
        if proj not in rpm_files:
            rpm_files[proj] = []
            rpm_filepaths[proj] = []

        for infix in rpm_infixes:
            for i_rpm in range(len(package_names[proj])):
                rpmname = '%s-%s%s-%s.%s.rpm'%(package_names[proj][i_rpm],infix,versions[proj][i_rpm],releases[proj][i_rpm],architecture)
                rpm_files[proj].append(rpmname)
                rpm_filepaths[proj].append(rpm_dir+rpmname)

        if proj in plugin_rpms:
            for plugin_name in plugin_rpms[proj]:
                rpm_files[proj].append('%s-%s-%s.%s.rpm'%(plugin_name,versions[proj],releases[proj],architecture))
                rpm_filepaths[proj].append(rpm_dir+rpm_files[proj][-1])

        if proj in addon_rpms:
            for rpmname in addon_rpms[proj]:
                if proj not in addon_rpm_filepaths:
                    addon_rpm_filepaths[proj] = []
                addi_rpm_file = '%s-%s-%s.%s.rpm'%(rpmname,versions[proj],releases[proj],architecture)
                addon_rpm_filepaths[proj].append(rpm_dir+addi_rpm_file)
else:
    rpm_files[target_proj] = [os.path.basename(direct_rpm_file)]
    rpm_filepaths[target_proj] = [direct_rpm_file]

##########################
# functions
def gbsbuild(proj, gbsopt, first_compile):
    if first_compile > 0:
        cmd = 'gbs build -A %s --include-al --ccache %s %s'%(architecture, gbsopt, proj)
    else:
        cmd = 'gbs build -A %s --include-al --ccache --noinit %s %s'%(architecture, gbsopt, proj)

    start_time = datetime.datetime.now()
    print '============================================================'
    print 'gbsbuild %s'%proj
    print
    print 'STARTED at %s'%start_time
    print '$ '+cmd
    print '============================================================'
    print

    ret = os.system(cmd)

    end_time = datetime.datetime.now()
    print
    print '============================================================'
    print 'gbsbuild %s'%proj
    print
    print 'FINISHED at %s'%end_time
    print 'Elapsed time:', end_time - start_time
    print '$ '+cmd
    print '============================================================'
    print

    return ret

def sdbpush(proj, rpm_filepaths, sdb_option=''):
    start_time = datetime.datetime.now()
    print '============================================================'
    print 'sdbpush %s'%proj
    print
    print 'STARTED at %s'%start_time
    print '============================================================'
    print

    for rpm_filepath in rpm_filepaths:
        cmd = ''
        #cmd += 'sdb root hoston;'
        #cmd += 'sdb root hostoff;'
        cmd += 'sdb root on; sdb %s push %s %s;'%(sdb_option, rpm_filepath, devicehome_dir)
        #cmd += 'sdb root hostoff;'
        print '$ '+cmd
        ret = os.system(cmd)

    end_time = datetime.datetime.now()
    print
    print '============================================================'
    print 'sdbpush %s'%proj
    print
    print 'FINISHED at %s'%end_time
    print 'Elapsed time:', end_time - start_time
    print '============================================================'
    print

    return ret

def copy_addon_rpms(proj, addon_rpm_filepaths):
    dir = os.path.expanduser(copy_addon_rpms_dir+'/'+profile)
    if(not os.path.exists(dir)):
        os.makedirs(dir)

    cmd = ''
    if addon_rpm_filepaths:
        for addi_path in addon_rpm_filepaths:
            cmd += 'cp %s %s;'%(addi_path, dir)

    start_time = datetime.datetime.now()
    print '============================================================'
    print 'copy_addon_rpms %s'%proj
    print
    print 'STARTED at %s'%start_time
    print '============================================================'
    print

    print '$ '+cmd
    ret = os.system(cmd)

    end_time = datetime.datetime.now()
    print
    print '============================================================'
    print 'FINISHED at %s'%end_time
    print 'Elapsed time:', end_time - start_time
    print '============================================================'
    print

    return ret

def copyrpm(proj, rpm_filepaths, destdir):
    dir = os.path.expanduser(destdir)
    if(not os.path.exists(dir)):
        os.makedirs(dir)

    start_time = datetime.datetime.now()
    print '============================================================'
    print 'copyrpm %s'%proj
    print
    print 'STARTED at %s'%start_time
    print '============================================================'
    print

    for rpm_filepath in rpm_filepaths:
        cmd = 'cp %s %s'%(rpm_filepath, destdir)
        print '$ '+cmd
        ret = os.system(cmd)

    end_time = datetime.datetime.now()
    print
    print '============================================================'
    print 'FINISHED at %s'%end_time
    print 'Elapsed time:', end_time - start_time
    print '============================================================'
    print

    return ret

def device_install(proj, install_device_cmd, rpm_files, sdb_option=''):
    start_time = datetime.datetime.now()
    print '============================================================'
    print 'device_install %s'%proj
    print
    print 'STARTED at %s'%start_time
    print '============================================================'
    print

    for rpm_file in rpm_files:
        cmd = ''
        #cmd += 'sdb root hoston;'
        #cmd += 'sdb root hostoff;'

        cmd += 'sdb root on; sdb %s shell "change-booting-mode.sh --update; cd %s; %s %s";'%(sdb_option, devicehome_dir, install_device_cmd, rpm_file)
        #cmd += 'sdb root hostoff;'
        print '$ '+cmd
        ret = os.system(cmd)

    end_time = datetime.datetime.now()
    print
    print '============================================================'
    print 'device_install %s'%proj
    print
    print 'FINISHED at %s'%end_time
    print 'Elapsed time:', end_time - start_time
    print '============================================================'
    print

    return ret

def device_run(proj, sdb_option=''):
    #if '-example.' in filepath:
        #filename = os.path.basename(filepath)
        #runfile = filename.replace('-example.cpp', '.example')
    #else:
        #runfile = 'dali-demo'
    runfile = 'dali-demo'
    cmd = ''
    #cmd += 'sdb root hoston;'
    #cmd += 'sdb root hostoff;'
    cmd += 'sdb root on; sdb %s shell "/usr/apps/com.samsung.dali-demo/bin/%s";'%(sdb_option, runfile)
    #cmd += 'sdb root hostoff;'

    print '============================================================'
    print 'device_run %s'%proj
    print
    print '$ '+cmd
    print '============================================================'
    print

    ret = os.system(cmd)
    return ret

def getLatestFileIndex(filepaths):
    lastest_proj = 0
    lastest_time = -1
    for proj, filepath in filepaths.items():
        if os.path.exists(filepath) and os.path.getmtime(filepath) > lastest_time:
            lastest_proj = proj
            lastest_time = os.path.getmtime(filepath)
        #print filepaths[i], time.ctime(os.path.getmtime(filepaths[i]))
    return lastest_proj

def printEndMessage(successful):
    end_time = datetime.datetime.now()
    print 
    print '================================================================================'
    print 'makegbs.py'
    if not successful:
        print sys.exc_info()
        traceback.print_exc()
    print
    if successful:
        print 'FINISHED at %s'%end_time
    else:
        print 'ERROR at %s'%end_time
    print 'Elapsed time:', end_time - start_time
    print '%% makegbs.py %s %s'%(maketarget, selected_proj)
    print '================================================================================'

try:
    if len(args.argv) > 2:
        filepath = args.argv[2]

        if maketarget=='gbsbuild':
            retcode = gbsbuild(target_proj, gbsopts[target_proj], 1)

        elif maketarget=='gbsbuild_noinit':
            retcode = gbsbuild(target_proj, gbsopts[target_proj], 0)

        elif maketarget=='sdbpush':
            retcode = sdbpush(target_proj, rpm_filepaths[target_proj])

        elif maketarget=='device_install':
            retcode = device_install(target_proj, install_device_cmds[target_proj], rpm_files[target_proj])

        elif maketarget=='push2install':
            retcode = sdbpush(target_proj, rpm_filepaths[target_proj])
            if retcode==0:
                retcode = device_install(target_proj, install_device_cmds[target_proj], rpm_files[target_proj])

        elif maketarget=='push2install-d':
            retcode = sdbpush(target_proj, rpm_filepaths[target_proj], '-d')
            if retcode==0:
                retcode = device_install(target_proj, install_device_cmds[target_proj], rpm_files[target_proj], '-d')

        elif maketarget=='push2install-e':
            retcode = sdbpush(target_proj, rpm_filepaths[target_proj], '-e')
            if retcode==0:
                retcode = device_install(target_proj, install_device_cmds[target_proj], rpm_files[target_proj], '-e')

        elif maketarget=='push2run':
            #ret = os.system('python makegbs.py sdbpush %s'%filepath)
            #if ret!=0:  # because ret=0~255, ret=512 can be interpreted as 0.
                #exit(1)
            retcode = sdbpush(target_proj, rpm_filepaths[target_proj])
            if retcode==0:
                retcode = device_install(target_proj, install_device_cmds[target_proj], rpm_files[target_proj])
            if retcode==0:
                retcode = device_run(filepath)

        elif maketarget=='gbs2install':
            retcode = gbsbuild(target_proj, gbsopts[target_proj], 1)
            if retcode==0:
                retcode = sdbpush(target_proj, rpm_filepaths[target_proj])
            if retcode==0:
                retcode = device_install(target_proj, install_device_cmds[target_proj], rpm_files[target_proj])

        elif maketarget=='gbs2install_noinit':
            retcode = gbsbuild(target_proj, gbsopts[target_proj], 0)
            if retcode==0:
                retcode = sdbpush(target_proj, rpm_filepaths[target_proj])
            if retcode==0:
                retcode = device_install(target_proj, install_device_cmds[target_proj], rpm_files[target_proj])

        elif maketarget=='gbs2copy':
            retcode = gbsbuild(target_proj, gbsopts[target_proj], 1)
            if retcode==0:
                retcode = copyrpm(target_proj, rpm_filepaths[target_proj], copyrpm_dest)

        elif maketarget=='gbs2copy_noinit':
            retcode = gbsbuild(target_proj, gbsopts[target_proj], 0)
            if retcode==0:
                retcode = copyrpm(target_proj, rpm_filepaths[target_proj], copyrpm_dest)

        elif maketarget=='gbs2run':
            retcode = gbsbuild(target_proj, gbsopts[target_proj], 1)
            if retcode==0:
                retcode = sdbpush(target_proj, rpm_filepaths[target_proj])
            if retcode==0:
                retcode = device_install(target_proj, install_device_cmds[target_proj], rpm_files[target_proj])
            if retcode==0:
                retcode = device_run(target_proj)

        elif maketarget=='gbs2run_noinit':
            retcode = gbsbuild(target_proj, gbsopts[target_proj], 0)
            if retcode==0:
                retcode = sdbpush(target_proj, rpm_filepaths[target_proj])
            if retcode==0:
                retcode = device_install(target_proj, install_device_cmds[target_proj], rpm_files[target_proj])
            if retcode==0:
                retcode = device_run(target_proj)

        elif maketarget=='run':
            ret = device_run(target_proj)

        elif maketarget=='gbsbuild_smart':
            latest_proj = getLatestFileIndex(rpm_filepaths)
            if projs.index(target_proj) < projs.index(latest_proj):
                earlier_index = proj_index
            else:
                earlier_index = projs.index(latest_proj)
            for i in range(earlier_index, len(projs)):
                retcode = gbsbuild(projs[i], gbsopts[i], 1)
                #print i, projs[i]
                if retcode!=0:
                    break

        elif maketarget=='gbs_all2run':
            for proj in exist_projs:
                retcode = gbsbuild(proj, gbsopts[proj], 1)
                if retcode!=0:
                    break
            if retcode==0:
                for proj in exist_projs:
                    retcode = sdbpush(proj, rpm_filepaths[proj])
                    if retcode!=0:
                        break
            if retcode==0:
                for proj in exist_projs:
                    retcode = device_install(proj, install_device_cmds[proj], rpm_files[proj])
                    if retcode!=0:
                        break
            retcode = device_run(filepath)

        elif maketarget=='push_all2run':
            for proj in exist_projs:
                retcode = sdbpush(proj, rpm_filepaths[proj])
                if retcode!=0:
                    break
            if retcode==0:
                for proj in exist_projs:
                    retcode = device_install(proj, install_device_cmds[proj], rpm_files[proj])
                    if retcode!=0:
                        break
            if retcode==0:
                retcode = device_run(filepath)

        elif maketarget=='copy_addon_rpms':
            retcode = copy_addon_rpms(target_proj, addon_rpm_filepaths[target_proj] if target_proj in addon_rpm_filepaths else None)

        elif maketarget=='copyrpm':
            retcode = copyrpm(target_proj, rpm_filepaths[target_proj], copyrpm_dest)

        else:
            print '\'%s\' is unknown maketarget for additional param \'%s\''%(maketarget, filepath)
            retcode = 1

    else:

        if maketarget=='gbsbuild_all':
            for proj in exist_projs:
                retcode = gbsbuild(proj, gbsopts[proj], 1)
                if retcode!=0:
                    break

        elif maketarget=='sdbpush_all':
            for proj in exist_projs:
                retcode = sdbpush(proj, rpm_filepaths[proj])
                if retcode!=0:
                    break

        elif maketarget=='device_install_all':
            for proj in exist_projs:
                retcode = device_install(proj, install_device_cmds[proj], rpm_files[proj])
                if retcode!=0:
                    break

        elif maketarget=='push2install_all':
            for proj in exist_projs:
                retcode = sdbpush(proj, rpm_filepaths[proj])
                if retcode!=0:
                    break
                retcode = device_install(proj, install_device_cmds[proj], rpm_files[proj])
                if retcode!=0:
                    break

        elif maketarget=='copy_addon_rpms_all':
            for proj in exist_projs:
                retcode = copy_addon_rpms(proj, addon_rpm_filepaths[proj] if proj in addon_rpm_filepaths else None)
                if retcode!=0:
                    break

        elif maketarget=='copyrpm_all':
            for proj in exist_projs:
                retcode = copyrpm(proj, rpm_filepaths[proj], copyrpm_dest)
                if retcode!=0:
                    break

        elif maketarget=='gbs2copy_all':
            for proj in exist_projs:
                retcode = gbsbuild(proj, gbsopts[proj], 1)
                if retcode!=0:
                    break
                retcode = copyrpm(proj, rpm_filepaths[proj], copyrpm_dest)
                if retcode!=0:
                    break

        else:
            print '\'%s\' is unknown maketarget '%(maketarget)
            retcode = 1

    if retcode!=0:
        exit(retcode)

except:
    printEndMessage(False)
    exit(1)
else:
    printEndMessage(True)
print
