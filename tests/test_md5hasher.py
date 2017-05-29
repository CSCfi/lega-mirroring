import pytest
from lega_mirroring import md5hasher_bigdir


def test_md5():
    md5sum = md5hasher_bigdir.md5('tests/data/text-file.txt')
    assert md5sum == '14758f1afd44c09b7992073ccf00b43d'
