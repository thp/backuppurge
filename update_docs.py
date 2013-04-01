#!/usr/bin/python
# -*- coding: utf-8 -*-
# Auto-generate manpage using ReStructured Text + rst2man
# http://bitbucket.org/pyugat/mini-setup-py

PACKAGE_NAME = 'backuppurge'

import datetime
import os
import re
import subprocess

main_py = open('lib/{0}/__init__.py'.format(PACKAGE_NAME)).read()
m = dict(re.findall("\n__([a-z]+)__ = '([^']+)'", main_py))
docs = re.findall('"""(.*?)"""', main_py, re.DOTALL)

m['author'], m['author_email'] = re.match(r'(.*) <(.*)>', m['author']).groups()
m['description'], m['long_description'] = docs[0].strip().split('\n\n', 1)

##################################################################

# Date for the manpage is today's date
today = datetime.date.today().strftime('%Y-%m-%d')

# Get synopsis and options by running the main script with "--help"
# This assumes that the output is non-customized argparse output.
help_output = subprocess.check_output(['./' + PACKAGE_NAME, '--help'],
        stderr=subprocess.PIPE)
help_output = help_output.decode('utf-8')
help_output = dict(x.split(':', 1) for x in help_output.split('\n\n'))

synopsis = re.sub(r'\s+', ' ', help_output['usage'].strip())
options = help_output['optional arguments']

# ReStructured Text Markup helpers (rulers for headings)
RULER_PACKAGE_NAME = '='*len(PACKAGE_NAME)
RULER_DESCRIPTION = '-'*len(m['description'])

manpage_rst = """
{RULER_PACKAGE_NAME}
{PACKAGE_NAME}
{RULER_PACKAGE_NAME}

{RULER_DESCRIPTION}
{m[description]}
{RULER_DESCRIPTION}

:Author:         {m[author]} <{m[author_email]}>
:Date:           {today}
:Copyright:      {m[license]}
:Version:        {m[version]}
:Manual section: 1
:Manual group:   Command-line utilities

SYNOPSIS
========

{synopsis}

DESCRIPTION
===========

{m[long_description]}

OPTIONS
=======

{options}

WEBSITE
=======

{m[url]}

""".format(**locals())

manpage_filename = os.path.join('share', 'man', 'man1', PACKAGE_NAME + '.1')

# Build manpage
process = subprocess.Popen(['rst2man', '-', manpage_filename], stdin=subprocess.PIPE)
process.communicate(manpage_rst.encode('utf-8'))
process.wait()

manpage_html = os.path.join('doc', PACKAGE_NAME+'.1.html')

# Build HTML version of manpage
process = subprocess.Popen(['rst2html', '--stylesheet=doc/style.css',
    '--embed-stylesheet', '-', manpage_html], stdin=subprocess.PIPE)
process.communicate(manpage_rst.encode('utf-8'))
process.wait()

index_html = os.path.join('doc', 'index.html')

# Convert the README file to index.thml
readme_txt = open('README').read()
readme_txt = readme_txt.decode('utf-8')
readme_txt = readme_txt.format(**m)

process = subprocess.Popen(['rst2html', '--stylesheet=doc/style.css',
    '--embed-stylesheet', '-', index_html], stdin=subprocess.PIPE)
process.communicate(readme_txt.encode('utf-8'))
process.wait()

