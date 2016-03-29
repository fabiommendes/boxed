import pytest
from boxed.pinteract import Pinteract


def test_simple_interaction():
    p = Pinteract(['echo', 'foo'])
    assert p.receive() == 'foo\n'


def test_io_interaction():
    # Simple echo program
    p = Pinteract(['python3', '-c', 'print(input("foo: "))'])
    assert p.receive() == 'foo: '
    p.send('bar')
    assert p.receive() == 'bar\n'

if __name__ == '__main__':
    pytest.main('test_pinteract.py')