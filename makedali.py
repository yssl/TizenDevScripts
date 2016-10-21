#!/usr/bin/env python
import os,sys, time, glob

maketarget = sys.argv[1]

print 'python %s'%sys.argv
print '(from CWD %s)'%os.getcwd()
print

projs = ['dali', 'dali-core','dali-adaptor','dali-toolkit','dali-demo']

preconf_debug = {}
preconf_debug['dali'] = "CXXFLAGS='-g -O0 --coverage' LDFLAGS='--coverage'"
preconf_debug['dali-core'] = "CXXFLAGS='-g -O0 --coverage' LDFLAGS='--coverage'"
preconf_debug['dali-adaptor'] = "CXXFLAGS='-g -O0 --coverage' LDFLAGS='--coverage'"
preconf_debug['dali-toolkit'] = "CXXFLAGS='-g -O0 --coverage' LDFLAGS='--coverage'"

confopts_debug = {}
confopts_debug['dali'] = "--prefix=$DESKTOP_PREFIX --enable-debug"
confopts_debug['dali-core'] = "--prefix=$DESKTOP_PREFIX --enable-debug"
#confopts_debug['dali-adaptor'] = "--prefix=$DESKTOP_PREFIX --enable-profile=UBUNTU --enable-gles=20 --enable-debug"
#confopts_debug['dali-adaptor'] = "--prefix=$DESKTOP_PREFIX --enable-profile=UBUNTU --enable-gles=20 --enable-debug --with-node-js=/media/Work/Code/NonTizenProjs/node-v0.12.4/deps/uv/include"
confopts_debug['dali-adaptor'] = "--prefix=$DESKTOP_PREFIX --enable-profile=UBUNTU --enable-gles=20 --enable-debug --with-libuv=/media/Work/Code/NonTizenProjs/node-v0.12.4/deps/uv/include"
confopts_debug['dali-toolkit'] = "--prefix=$DESKTOP_PREFIX --enable-debug"
confopts_debug['dali-demo'] = "-DCMAKE_INSTALL_PREFIX=$DESKTOP_PREFIX -DCMAKE_BUILD_TYPE=Debug"

preconf_release = {}
confopts_release = {}
confopts_release['dali'] = '--prefix=$DESKTOP_PREFIX'
confopts_release['dali-core'] = '--prefix=$DESKTOP_PREFIX'
#confopts_release['dali-adaptor'] = '--prefix=$DESKTOP_PREFIX --enable-profile=UBUNTU --enable-gles=20'
#confopts_release['dali-adaptor'] = "--prefix=$DESKTOP_PREFIX --enable-profile=UBUNTU --enable-gles=20 --with-node-js=/media/Work/Code/NonTizenProjs/node-v0.12.4/deps/uv/include"
confopts_release['dali-adaptor'] = "--prefix=$DESKTOP_PREFIX --enable-profile=UBUNTU --enable-gles=20 --with-libuv=/media/Work/Code/NonTizenProjs/node-v0.12.4/deps/uv/include"
#confopts_release['dali-adaptor'] = "--prefix=$DESKTOP_PREFIX --enable-profile=UBUNTU --enable-gles=20 --enable-feedback --with-libuv=/media/Work/Code/NonTizenProjs/node-v0.12.4/deps/uv/include"
confopts_release['dali-toolkit'] = '--prefix=$DESKTOP_PREFIX'
confopts_release['dali-demo'] = '-DCMAKE_INSTALL_PREFIX=$DESKTOP_PREFIX -DCMAKE_BUILD_TYPE=Release'

deps_dir = {}
deps_dir['dali'] = './dali-core/.deps/'
deps_dir['dali-core'] = './dali-core/.deps/'
deps_dir['dali-adaptor'] = './adaptor/.deps/'
deps_dir['dali-toolkit'] = './dali-toolkit/.deps/'

dali_env_opt = os.environ.get('DESKTOP_PREFIX')

outputs = {}
outputs['dali'] = dali_env_opt+'/lib/libdali-core.so'
outputs['dali-core'] = dali_env_opt+'/lib/libdali-core.so'
outputs['dali-adaptor'] = dali_env_opt+'/lib/libdali-adaptor.so'
outputs['dali-toolkit'] = dali_env_opt+'/lib/libdali-toolkit.so'
outputs['dali-demo'] = dali_env_opt+'/bin/dali-demo'

exist_projs = []
for proj in projs:
    packaging_dir = './%s/packaging/'%proj
    findglobs = glob.glob(packaging_dir+'*.spec')
    if len(findglobs) > 0:
        exist_projs.append(proj)

def autoreconf(proj):
    if proj!='dali-demo':
        ret = os.system('cd %s/build/tizen/; autoreconf --install'%(proj))
        if ret!=0:  # because ret=0~255, ret=512 can be interpreted as 0.
            exit(1)

def configure(proj, confopt, preconf):
    if proj!='dali-demo':
        ret = os.system('cd %s/build/tizen/; %s ./configure %s'%(proj, preconf, confopt))
    else:
        ret = os.system('cd %s/build/tizen/; cmake %s .'%(proj, confopt))
    if ret!=0:  # because ret=0~255, ret=512 can be interpreted as 0.
        exit(1)

def install(proj):
    ret = os.system('cd %s/build/tizen/; make install -j8'%(proj))
    if ret!=0:  # because ret=0~255, ret=512 can be interpreted as 0.
        exit(1)

def build(proj):
    ret = os.system('cd %s/build/tizen/; make all -j8'%(proj))
    if ret!=0:  # because ret=0~255, ret=512 can be interpreted as 0.
        exit(1)

def clean(proj):
    ret = os.system('cd %s/build/tizen/; make clean'%(proj))
    if ret!=0:  # because ret=0~255, ret=512 can be interpreted as 0.
        exit(1)
    if proj in deps_dir:
        ret = os.system('cd %s/build/tizen/; rm -rf %s'%(proj, deps_dir[proj]))
        if ret!=0:  # because ret=0~255, ret=512 can be interpreted as 0.
            exit(1)

def run(filepath):
    if '-example.cpp' in filepath:
        filename = os.path.basename(filepath)
        runfile = filename.replace('-example.cpp', '.example')
    elif '-example.h' in filepath:
        filename = os.path.basename(filepath)
        runfile = filename.replace('-example.h', '.example')
    elif 'benchmark' in filepath:
        runfile = 'benchmark.example'
    else:
        runfile = 'dali-demo'
    #ret = os.system('cd $DESKTOP_PREFIX/bin; ./%s'%runfile)
    ret = os.system('cd $DESKTOP_PREFIX/bin; ./%s -w 480 -h 800'%runfile)
    if ret!=0:  # because ret=0~255, ret=512 can be interpreted as 0.
        exit(1)

def getLatestFileIndex(filepaths):
    lastest_proj = 0
    lastest_time = -1
    for proj, filepath in filepaths.items():
        if os.path.exists(filepath) and os.path.getmtime(filepath) > lastest_time:
            lastest_proj = proj
            lastest_time = os.path.getmtime(filepath)
        #print filepaths[i], time.ctime(os.path.getmtime(filepaths[i]))
    return lastest_proj

if len(sys.argv) > 2:
    filepath = sys.argv[2]

    for proj in exist_projs:
        if proj+'/' in filepath:
            target_proj = proj
            break

    if target_proj=='':
        print 'cannot recognize project of %s.'%filepath
        exit()

    if maketarget=='configure_release':
        autoreconf(target_proj)
        configure(target_proj, confopts_release[target_proj], preconf_release[target_proj] if target_proj in preconf_release else '')

    elif maketarget=='configure_debug':
        autoreconf(target_proj)
        configure(target_proj, confopts_debug[target_proj], preconf_debug[target_proj] if target_proj in preconf_debug else '')

    elif maketarget=='install':
        install(target_proj)

    elif maketarget=='install_smart':
        latest_proj = getLatestFileIndex(outputs)
        if projs.index(target_proj) < projs.index(latest_proj):
            earlier_index = proj_index
        else:
            earlier_index = latest_index
        for i in range(earlier_index, len(projs)):
            install(projs[i])
            #print i, projs[i]

    elif maketarget=='build':
        build(target_proj)

    elif maketarget=='clean':
        clean(target_proj)

    elif maketarget=='run':
        run(filepath)

    # instead of...
    #call s:nnoreicmap('<expr>','<F9>',"':Dispatch python make.py install '.expand('%:p').'; if [ $? -eq 0 ]; then python make.py run '.expand('%:p').'; fi<CR>'")
    #call s:nnoreicmap('<expr>','<C-S-A-F9>',"':Dispatch python make.py install_all '.expand('%:p').'; if [ $? -eq 0 ]; then python make.py run '.expand('%:p').'; fi<CR>'")
    elif maketarget=='install2run':
        install(target_proj)
        run(filepath)

    elif maketarget=='install_all2run_release':
        for proj in exist_projs:
            print proj
            clean(proj)
            autoreconf(proj)
            configure(proj, confopts_release[proj], preconf_release[proj] if proj in preconf_release else '')
            install(proj)
        run(filepath)

    elif maketarget=='install_all2run_debug':
        for proj in exist_projs:
            #clean(proj)
            autoreconf(proj)
            configure(proj, confopts_debug[proj], preconf_debug[proj] if proj in preconf_debug else '')
            install(proj)
        run(filepath)

else:
    if maketarget=='configure_all_release':
        for proj in exist_projs:
            autoreconf(proj)
            configure(proj, confopts_release[proj], preconf_release[proj] if proj in preconf_release else '')

    elif maketarget=='configure_all_debug':
        for proj in exist_projs:
            autoreconf(proj)
            configure(proj, confopts_debug[proj], preconf_debug[proj] if proj in preconf_debug else '')

    elif maketarget=='install_all_release':
        for proj in exist_projs:
            clean(proj)
            autoreconf(proj)
            configure(proj, confopts_release[proj], preconf_release[proj] if proj in preconf_release else '')
            install(proj)

    elif maketarget=='install_all_debug':
        for proj in exist_projs:
            clean(proj)
            autoreconf(proj)
            configure(proj, confopts_debug[proj], preconf_debug[proj] if proj in preconf_debug else '')
            install(proj)

    elif maketarget=='build_all':
        for proj in exist_projs:
            build(proj)

    elif maketarget=='clean_all':
        for proj in exist_projs:
            clean(proj)
