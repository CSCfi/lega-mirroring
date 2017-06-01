import pytest
import time
import calendar
from lega_mirroring import cf_dir


def test_get_file_size():
    assert cf_dir.get_file_size('tests/testdata/file10.txt') == 6


def test_get_file_age():
    def getmtime(path):                                                          
        """This is a monkeypatch function for os.path.getmtime() which returns
        always a predefined constant value 1496209920.4538686"""
        return 1496209920.4538686
    assert cf_dir.get_file_age('tests/testdata/file10.txt') == 1496209920.4538686


def test_get_time_now():
    assert cf_dir.get_time_now() == calendar.timegm(time.gmtime())


def test_db_get_file_details():
    assert cf_dir.db_get_file_details('file100.txt') == {'id': 1, 'name': 'file100.txt', 'size': 6, 'age': 1496219121.3843114, 'passes': 3, 'verified': 1}


def test_hash_md5_for_file():
    assert cf_dir.hash_md5_for_file('tests/testdata/file10.txt') == 'a8f5f167f44f4964e6c998dee827110c'


def test_get_md5_from_file():
    assert cf_dir.get_md5_from_file('tests/testdata/file10.txt') == 'a8f5f167f44f4964e6c998dee827110c'
