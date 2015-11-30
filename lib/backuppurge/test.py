# -*- coding: utf-8 -*-
# Unit tests for backuppurge

from __future__ import print_function

from nose.tools import *

import datetime

import backuppurge

class FixtureData:
    TODAY = datetime.date(2013, 3, 31)

    @classmethod
    def get_filenames(cls):
        def generate_filename(offset):
            date = cls.TODAY - datetime.timedelta(days=offset)
            return date.strftime('backup-%Y-%m-%d.tar.gz')

        return [generate_filename(offset) for offset in range(3*365)]

def test_last30days():
    """
    Test if last 30 days are kept (daily backups)
    """
    filenames = FixtureData.get_filenames()
    today = FixtureData.TODAY
    prefix = None

    purge_list = backuppurge.PurgeList(filenames, today, prefix)
    purge_list.keep_daily(30)

    purge_set = purge_list.get_filenames()
    keep_set = set(filenames).difference(purge_set)

    expected_keep_set = {
        'backup-2013-03-31.tar.gz', 'backup-2013-03-30.tar.gz',
        'backup-2013-03-29.tar.gz', 'backup-2013-03-28.tar.gz',
        'backup-2013-03-27.tar.gz', 'backup-2013-03-26.tar.gz',
        'backup-2013-03-25.tar.gz', 'backup-2013-03-24.tar.gz',
        'backup-2013-03-23.tar.gz', 'backup-2013-03-22.tar.gz',
        'backup-2013-03-21.tar.gz', 'backup-2013-03-20.tar.gz',
        'backup-2013-03-19.tar.gz', 'backup-2013-03-18.tar.gz',
        'backup-2013-03-17.tar.gz', 'backup-2013-03-16.tar.gz',
        'backup-2013-03-15.tar.gz', 'backup-2013-03-14.tar.gz',
        'backup-2013-03-13.tar.gz', 'backup-2013-03-12.tar.gz',
        'backup-2013-03-11.tar.gz', 'backup-2013-03-10.tar.gz',
        'backup-2013-03-09.tar.gz', 'backup-2013-03-08.tar.gz',
        'backup-2013-03-07.tar.gz', 'backup-2013-03-06.tar.gz',
        'backup-2013-03-05.tar.gz', 'backup-2013-03-04.tar.gz',
        'backup-2013-03-03.tar.gz', 'backup-2013-03-02.tar.gz',
    }

    assert_equal(len(filenames) - len(purge_set), 30)
    assert_equal(keep_set, expected_keep_set)

def test_last6months():
    """
    Test if one backup per month is kept for last 6 months
    """
    filenames = FixtureData.get_filenames()
    today = FixtureData.TODAY
    prefix = None

    purge_list = backuppurge.PurgeList(filenames, today, prefix)
    purge_list.keep_monthly(6)

    purge_set = purge_list.get_filenames()
    keep_set = set(filenames).difference(purge_set)

    expected_keep_set = {
        'backup-2013-03-01.tar.gz', 'backup-2013-02-01.tar.gz',
        'backup-2013-01-01.tar.gz', 'backup-2012-12-01.tar.gz',
        'backup-2012-11-01.tar.gz', 'backup-2012-10-01.tar.gz',
    }

    assert_equal(len(filenames) - len(purge_set), 6)
    assert_equal(keep_set, expected_keep_set)

def test_last2years():
    """
    Test if one backup per year is kept for last 2 years
    """
    filenames = FixtureData.get_filenames()
    today = FixtureData.TODAY
    prefix = None

    purge_list = backuppurge.PurgeList(filenames, today, prefix)
    purge_list.keep_yearly(2)

    purge_set = purge_list.get_filenames()
    keep_set = set(filenames).difference(purge_set)

    expected_keep_set = {
        'backup-2013-01-01.tar.gz', 'backup-2012-01-01.tar.gz',
    }

    assert_equal(len(filenames) - len(purge_set), 2)
    assert_equal(keep_set, expected_keep_set)

def test_days_months_and_years():
    """
    Test if right set of filenames is kept for days, months, years
    """
    filenames = FixtureData.get_filenames()
    today = FixtureData.TODAY
    prefix = None

    purge_list = backuppurge.PurgeList(filenames, today, prefix)
    purge_list.keep_daily(5)
    purge_list.keep_monthly(3)
    purge_list.keep_yearly(2)

    purge_set = purge_list.get_filenames()
    keep_set = set(filenames).difference(purge_set)

    expected_keep_set = {
        # Days
        'backup-2013-03-31.tar.gz', 'backup-2013-03-30.tar.gz',
        'backup-2013-03-29.tar.gz', 'backup-2013-03-28.tar.gz',
        'backup-2013-03-27.tar.gz',

        # Months
        'backup-2013-03-01.tar.gz', 'backup-2013-02-01.tar.gz',
        'backup-2013-01-01.tar.gz',

        # Years
        # 'backup-2013-01-01.tar.gz' is included in months above
        'backup-2012-01-01.tar.gz',
    }

    assert_equal(keep_set, expected_keep_set)

def test_yearly_takes_first_available():
    """
    Test if backup of January 10th is used for yearly if
    January 1-9 don't exist
    """

    filenames = FixtureData.get_filenames()
    today = FixtureData.TODAY
    prefix = None

    # Simulate missing backups for January 1st - January 9th
    filenames.remove('backup-2013-01-01.tar.gz')
    filenames.remove('backup-2013-01-02.tar.gz')
    filenames.remove('backup-2013-01-03.tar.gz')
    filenames.remove('backup-2013-01-04.tar.gz')
    filenames.remove('backup-2013-01-05.tar.gz')
    filenames.remove('backup-2013-01-06.tar.gz')
    filenames.remove('backup-2013-01-07.tar.gz')
    filenames.remove('backup-2013-01-08.tar.gz')
    filenames.remove('backup-2013-01-09.tar.gz')

    purge_list = backuppurge.PurgeList(filenames, today, prefix)
    purge_list.keep_yearly(2)

    purge_set = purge_list.get_filenames()
    keep_set = set(filenames).difference(purge_set)

    expected_keep_set = {
        'backup-2013-01-10.tar.gz', 'backup-2012-01-01.tar.gz',
    }

    assert_equal(len(filenames) - len(purge_set), 2)
    assert_equal(keep_set, expected_keep_set)

def test_monthly_takes_first_available():
    """
    Test if backup of March 5th is used for monthly if
    March 1-4 don't exist
    """
    filenames = FixtureData.get_filenames()
    today = FixtureData.TODAY
    prefix = None

    # Simulate missing backups for March 1st - March 4th
    filenames.remove('backup-2013-03-01.tar.gz')
    filenames.remove('backup-2013-03-02.tar.gz')
    filenames.remove('backup-2013-03-03.tar.gz')
    filenames.remove('backup-2013-03-04.tar.gz')

    purge_list = backuppurge.PurgeList(filenames, today, prefix)
    purge_list.keep_monthly(2)

    purge_set = purge_list.get_filenames()
    keep_set = set(filenames).difference(purge_set)

    expected_keep_set = {
        'backup-2013-03-05.tar.gz', 'backup-2013-02-01.tar.gz',
    }

    assert_equal(len(filenames) - len(purge_set), 2)
    assert_equal(keep_set, expected_keep_set)

@raises(backuppurge.MixedFilenames)
def test_wrong_prefix_fails():
    """
    Test if having files with different prefix fails
    """
    filenames = [
        'homedir-2013-03-31.tar.gz',
        'backup-2013-03-21.tar.gz',
    ]
    today = FixtureData.TODAY
    prefix = None

    purge_list = backuppurge.PurgeList(filenames, today, prefix)

@raises(backuppurge.MixedFilenames)
def test_wrong_postfix_fails():
    """
    Test if having files with different postfix fails
    """
    filenames = [
        'backup-2013-03-31.tar.gz',
        'backup-2013-03-21.tar.bz2',
    ]
    today = FixtureData.TODAY
    prefix = None

    purge_list = backuppurge.PurgeList(filenames, today, prefix)

def test_ignore_nonempty():
    """
    Test that files / directories without a date are ignored
    """
    filenames = [
        'backup-2013-03-31.tgz',
        '.git',
        'README',
    ]
    today = FixtureData.TODAY
    prefix = None

    purge_list = backuppurge.PurgeList(filenames, today, prefix)
    purge_set = purge_list.get_filenames()

    assert '.git' not in purge_set
    assert 'README' not in purge_set


def test_multiple_prefixes_when_specifying_prefix():
    homedirs = [
        'homedir-2013-03-31.tar.gz',
        'homedir-2012-12-24.tar.gz',
        'homedir-2001-08-30.tar.gz',
    ]
    backups = [
        'backup-2013-03-21.tar.gz',
        'backup-2013-01-21.tar.gz',
        'backup-2001-03-21.tar.gz',
    ]
    filenames = homedirs + backups
    today = FixtureData.TODAY

    prefix_to_expected_keep_set = {
        'backup-': set(homedirs).union({
            'backup-2013-03-21.tar.gz',
        }),
        'homedir-': set(backups).union({
            'homedir-2013-03-31.tar.gz',
        }),
    }

    def check_with_prefix(prefix, expected_keep_set):
        purge_list = backuppurge.PurgeList(filenames, today, prefix)
        purge_list.keep_daily(30)
        purge_set = purge_list.get_filenames()
        print('Purge set:', purge_set)
        keep_set = set(filenames).difference(purge_set)
        print('Keep set:', keep_set)

        assert_equal(keep_set, expected_keep_set)

    for prefix, expected_keep_set in prefix_to_expected_keep_set.items():
        yield check_with_prefix, prefix, expected_keep_set
