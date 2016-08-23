import pytest
from boxed.core import capture_print


def test_capture_print():
    with capture_print() as data:
        print('foo')

    assert data == 'foo\n'

