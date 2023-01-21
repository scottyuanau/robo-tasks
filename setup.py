"""
This is a setup.py script generated by py2applet

Usage:

Deployment:
    python setup.py py2app

Alias:
    python setup.py py2app -A
"""

from setuptools import setup

APP = ['robo-tasks.py']
DATA_FILES = []
OPTIONS = {}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)