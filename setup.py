# -*- coding: utf-8 -*-
"""
Run this code to include the wiki-gendersort class in your Python environment
"""

import os
import site

st_pkg = site.getsitepackages()[0]

cwd = os.path.abspath(os.path.dirname(__file__))

paths = []
paths.append(os.path.join(cwd, 'src'))

filepath = os.path.join(st_pkg, 'wiki-gendersort.pth')

with open(filepath, 'w') as FILE:
    for path in paths:
        FILE.write(path)
        FILE.write('\n')
