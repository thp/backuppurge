# -*- coding: utf-8 -*-
#
# backuppurge: Selectively purge daily full backups
#
# Copyright (c) 2013, 2015 Thomas Perl <m@thp.io>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""
Selectively purge daily full backups

Lists files in that should be purged in a backup strategy where daily backups
are kept for *DAYS* days, monthly backups for *MONTHS* months and yearly backups
for *YEARS* years. Monthly and yearly backups are always the oldest possible
daily backup (e.g. first of month and first of year that is available).

Files are expected to have their date embedded as ``YYYY-MM-DD`` somewhere in
the filename, e.g. ``homedir-2013-03-31.tgz``

For monthly and yearly backups, the first day available will be kept (e.g.
January 1st for yearly, but if that is not available, January 2nd will be
kept, etc..).

This program can be used together with xargs(1) from GNU findutils::

    backuppurge --print0 /var/backups/ | xargs -r -0 rm

Only files directly in the specified **DIRECTORY** will be searched (in the
above example, ``/var/backups/homedir-2013-03-31.tgz`` will be considered,
but not ``/var/backups/etc/etc-2013-03-31.tgz``). This prevents accidental
deletion of files. If --include-directories (-D) is used, directories directly
below the path will be included in the search (e.g. the directory
``/var/backups/etc-2015-07-24/`` will be included in the purge search).

This script assumes daily backups are FULL backups, not incremental. For
example, a full daily backup of your ``/etc`` can be created by adding
(``crontab -e``) a command like the following to your crontab(5) file::

    tar czf /var/backups/etc/etc-$(date +%F).tgz /etc
"""


from __future__ import print_function

import logging
import warnings

import datetime
import re
import os

__author__ = 'Thomas Perl <m@thp.io>'
__license__ = 'Simplified BSD License'
__url__ = 'http://thp.io/2013/backuppurge/'
__version__ = '1.0.3'


class MixedFilenames(BaseException):
    """
    Raised when the list of filenames passed to PurgeList don't have
    the same prefix and postfix (before/after the date).
    """
    pass


class NoBackupsFound(Warning):
    """
    Warning raised when no backup files (with a date) are found.
    """
    pass

warnings.simplefilter('always', NoBackupsFound)


def find_backups(directory, include_directories):
    """
    Find backup files in directory
    """
    return filter(lambda f: (include_directories and os.path.isdir(f)) or os.path.isfile(f),
                  map(lambda filename: os.path.join(directory, filename), os.listdir(directory)))


class PurgeList:
    def __init__(self, filenames, today, prefix):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.filenames = filenames
        self.today = today
        self.prefix = prefix

        # Check prefix of files (before date), bail out if not all equal
        self.check_file_list()

        # By default, purge everything
        self.purge = set(self.filenames)

    def check_file_list(self):
        regex = re.compile(r'^(.*)(\d{4}-\d{2}-\d{2})(.*)$')

        # Remove all filenames without a date string in them
        self.filenames = list(filter(regex.match, self.filenames))

        if self.prefix is not None:
            self.filenames = [filename for filename in self.filenames
                              if regex.match(filename).group(1) == self.prefix]

        if len(self.filenames) == 0:
            warnings.warn('File list is empty', NoBackupsFound)
            return

        prefixes, _, postfixes = map(set, zip(*[regex.match(filename).groups()
            for filename in self.filenames]))

        if len(prefixes) != 1:
            raise MixedFilenames('Non-unique prefixes: {0}'.format(prefixes))

        if len(postfixes) != 1:
            raise MixedFilenames('Non-unique postfixes: {0}'.format(postfixes))

    def keep(self, filename, kind):
        """Mark filename to be kept"""
        if filename is None:
            return

        if filename in self.purge:
            self.logger.info('Keeping file for %s: %s', kind, filename)
            self.purge.remove(filename)
        else:
            self.logger.debug('File for %s already kept: %s', kind, filename)

    def get_all(self, year, month=None, day=None):
        """Get all backups for a specific year"""

        month_re = r'{0:02d}'.format(month) if month else r'\d{2}'
        day_re = r'{0:02d}'.format(day) if day else r'\d{2}'

        regex = re.compile(r'{0:04d}-{1:s}-{2:s}'.format(year, month_re, day_re))

        return sorted(filter(regex.search, self.filenames))

    def get_first(self, year, month=None, day=None):
        """Get first backup for a specific year, month or day

        get_first(2013) -> First available backup in 2013
        get_first(2013, 3) -> First available backup in March 2013
        get_first(2013, 3, 31) -> First available backup for March 31st 2013
        """
        matches = self.get_all(year, month, day)
        if matches:
            return matches[0]

        return None

    def recent_days(self, count):
        day = self.today
        while count > 0:
            yield (day.year, day.month, day.day)
            day -= datetime.timedelta(days=1)
            count -= 1

    def recent_months(self, count):
        month = (self.today.year, self.today.month)
        while count > 0:
            yield month
            if month[1] == 1:
                month = (month[0]-1, 12)
            else:
                month = (month[0], month[1]-1)
            count -= 1

    def recent_years(self, count):
        year = self.today.year
        while count > 0:
            yield year
            year -= 1
            count -= 1

    def keep_daily(self, days):
        for year, month, day in self.recent_days(days):
            self.keep(self.get_first(year, month, day), 'daily')

    def keep_monthly(self, months):
        for year, month in self.recent_months(months):
            self.keep(self.get_first(year, month),
                    'monthly ({0}-{1:02d})'.format(year, month))

    def keep_yearly(self, years):
        for year in self.recent_years(years):
            self.keep(self.get_first(year), 'yearly ({0})'.format(year))

    def get_filenames(self):
        return self.purge


def main(directory, days, months, years, separator, include_directories, prefix):
    today = datetime.date.today()
    filenames = find_backups(directory, include_directories)

    purge_list = PurgeList(filenames, today, prefix)
    purge_list.keep_daily(days)
    purge_list.keep_monthly(months)
    purge_list.keep_yearly(years)

    purge_files = purge_list.get_filenames()
    if purge_files:
        print(separator.join(purge_files), end=separator)

