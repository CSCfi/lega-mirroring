import pytest
import time
import calendar
from lega_mirroring import cf_dir


def test_get_file_size():
    assert cf_dir.get_file_size('tests/testdata/file10.txt') == 6


def test_get_file_age():
    assert cf_dir.get_file_age('tests/testdata/file10.txt') == 1496209920.4538686


def test_get_time_now():
    assert cf_dir.get_time_now() == calendar.timegm(time.gmtime())

# Not working
def test_db_get_file_details():
    assert cf_dir.db_get_file_details('tests/testdata/file10.txt') != [0, 0, 0, 0, 0, 0]


def test_hash_md5_for_file():
    assert cf_dir.hash_md5_for_file('tests/testdata/file10.txt') == 'a8f5f167f44f4964e6c998dee827110c'


def test_get_md5_from_file():
    assert cf_dir.get_md5_from_file('tests/testdata/file10.txt') == 'a8f5f167f44f4964e6c998dee827110c'
    # for warning see:
    # https://stackoverflow.com/questions/12118609/python-str-object-has-no-attribute-close

''' How to test void db functions?

def test_db_update_file_detail():
def test_db_increment_passes():
def test_db_insert_new_file():
def test_db_verify_file_integrity():

'''
