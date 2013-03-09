import os
from shutil import copy, rmtree
# from distutils.core import run_setup
from subprocess import call, Popen, PIPE

def symlink(source, target):
    """Cross-platform symlink"""
    os_symlink = getattr(os, "symlink", None)
    if callable(os_symlink):
        os_symlink(source, target)
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(target, source, flags) == 0:
            raise ctypes.WinError()

pathname = os.path.abspath(os.path.dirname(__file__))
os.chdir(pathname)

# work from root
os.chdir('../../')

# clean up first
for dir in os.listdir('.'):
    if dir.endswith('egg-info'):
        rmtree(dir)

# create symlink to dependencies
links = [(os.path.realpath('../qtools/qtools'), 'qtools')]
for source, target in links:
    if not os.path.exists(target):
        symlink(source, target)

# copy setup.py and remove commented lines so that external dependencies
# are built into the package
uncomment = False
with open('setup.py', 'r') as fr:
    with open('setup_dev.py', 'w') as fw:
        for line in fr:
            if line.strip() == '#<':
                uncomment = True
                # pass this line
                fw.write(line)
                continue
            elif line.strip() == '#>':
                uncomment = False
            # uncomment lines
            if uncomment:
                fw.write(line.replace('# ', ''))
            # or copy lines
            else:
                fw.write(line)
            
# build the distribution
call('python setup_dev.py bdist_wininst sdist --formats=gztar,zip')

# clean up
os.remove('setup_dev.py')
# for _, target in links:
    # os.remove(target)
