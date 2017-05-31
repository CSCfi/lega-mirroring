import pytest
from lega_mirroring import md5hasher_dir


def test_md5():
    md5sum = md5hasher_dir.md5('tests/data/text-file.txt')
    assert md5sum == 'd881b69b0aca33bcf5dbc7dc5c448cc2'
