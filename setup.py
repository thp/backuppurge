#!/usr/bin/python
# -*- coding: utf-8 -*-
# Minimalistic, automatic setup.py file for Python modules
# Copyright (c) 2008-2013 Thomas Perl <thp.io/about>

PACKAGE_NAME = 'backuppurge'

# Assumptions:
#  1. Package name equals main script file name (and only one script)
#  2. Main script contains docstring + dunder-{author, license, url, version}
#  3. Data files are in "share/", will be installed in $(PREFIX)/share
#  4. Only a single module that has the same name as the package

from distutils.core import setup

import os
import re

main_py = open(PACKAGE_NAME+'.py').read()
m = dict(re.findall("\n__([a-z]+)__ = '([^']+)'", main_py))
docs = re.findall('"""(.*?)"""', main_py, re.DOTALL)

m['name'] = PACKAGE_NAME
m['author'], m['author_email'] = re.match(r'(.*) <(.*)>', m['author']).groups()
m['description'], m['long_description'] = docs[0].strip().split('\n\n', 1)
m['download_url'] = m['url'] + PACKAGE_NAME + '-' + m['version'] + '.tar.gz'

m['scripts'] = [PACKAGE_NAME]
m['py_modules'] = [PACKAGE_NAME]
m['data_files'] = [(dirname, [os.path.join(dirname, file) for file in files])
        for dirname, _, files in os.walk('share')]

setup(**m)

