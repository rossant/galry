import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

LONG_DESCRIPTION = \
"""Galry is a high performance interactive visualization package in Python. It lets you visualize and navigate into very large plots in real time, by using the graphics card as much as possible. Galry is written directly on top of PyOpenGL for the highest performance possible."""

if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

if __name__ == '__main__':

    setup(
        zip_safe=False,
        name='galry',
        version='0.3.1',
        author='Cyrille Rossant',
        author_email='rossant@github',
        packages=['galry',
                  'galry.managers',
                  'galry.processors',
                  'galry.test',
                  'galry.visuals',
                  'galry.visuals.fontmaps',
                  ],
        package_data={
            'galry': ['cursors/*.png', 'icons/*.png'],
            'galry.visuals': ['fontmaps/*.*'],
            'galry.test': ['autosave/*REF.png'],
        },
        # scripts=[''],
        url='https://github.com/rossant/galry',
        license='LICENSE.md',
        description='High-performance interactive visualization in Python.',
        long_description=LONG_DESCRIPTION,
        install_requires=[
        ],
    )
