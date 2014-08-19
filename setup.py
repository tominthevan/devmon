#!/usr/bin/env python3

from distutils.core import setup

setup(name='DevMon',
      version='0.0.1',
      description='Device monitor',
      author='Tom Moore',
      author_email='',
      url='',
      packages=['devMonitor', 'devMonitor.ads1x15', 'devMonitor.configObjects'],
      scripts=['DevMon'],
      data_files=[('/usr/share/devmon', ['DevMonitor.ini']),],
      )
