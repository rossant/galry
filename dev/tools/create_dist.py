import os
from distutils.core import run_setup

pathname = os.path.abspath(os.path.dirname(__file__))
os.chdir(pathname)
os.chdir('../') # work from root
run_setup('setup.py', ['bdist_wininst'])
run_setup('setup.py', ['sdist', '--formats=gztar,zip'])
