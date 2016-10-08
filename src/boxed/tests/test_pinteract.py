import os
from contextlib import contextmanager

from boxed.pinteract import Pinteract


@contextmanager
def c_main(src):
    src = """
#include<stdio.h>

int main() {
    %s
    return 0;
}
    """ % src
    dirname = os.path.dirname(__file__)
    fname = os.path.join(dirname, 'test_pinteract_example.c')
    try:
        with open(fname, 'w') as F:
            F.write(src)
        yield Pinteract(['tcc', fname, '-run'])
    finally:
        os.remove(fname)


#
# Simple CLI programs
#
def test_simple_interaction():
    p = Pinteract(['echo', 'foo'])
    assert p.receive() == 'foo\n'


#
# Python programs
#
def test_io_interaction():
    p = Pinteract(['python3', '-c', 'print(input("foo: "))'])
    assert p.receive() == 'foo: '
    p.send('bar')
    assert p.receive() == 'bar\n'


def test_send_two_inputs():
    p = Pinteract(['python3', '-c', 'x = input(); y = input(); print(x + y)'])
    p.send('foo')
    p.send('bar')
    assert p.receive() == 'foobar\n'


def test_intercalate_inputs_and_outputs():
    p = Pinteract(
        ['python3', '-c', 'x = input("x"); y = input("y"); print(x + y)'])
    assert p.receive() == 'x'
    p.send('foo')
    assert p.receive() == 'y'
    p.send('bar')
    assert p.receive() == 'foobar\n'


def test_can_sleep_between_two_inputs():
    p = Pinteract(['python3', '-c', 'import time; '
                                    'input("foo: "); '
                                    'time.sleep(0.07); '
                                    'print(input("bar: "))'])
    assert p.receive() == 'foo: '
    p.send('bar')
    assert p.receive_non_empty() == 'bar: '
    p.send('bar')
    assert p.receive() == 'bar\n'


#
# C programs
#
def test_read_c_program():
    with c_main('puts("hello world");') as p:
        assert p.receive() == 'hello world\n'


def test_send_two_inputs_to_c_program():
    src = 'char a[100], b[100]; ' \
          'scanf("%s", a); scanf("%s", b);' \
          'printf("%s%s\n", a, b);'

    with c_main(src) as p:
        p.send('foo')
        p.send('bar')
        assert p.receive() == 'foobar\n'


def test_intercalate_inputs_and_outputs_in_c_program():
    src = 'char a[100], b[100]; ' \
          'printf("a: "); scanf("%s", a); ' \
          'printf("b: "); scanf("%s", b);' \
          'printf("%s%s\n", a, b);'

    with c_main(src) as p:
        assert p.receive() == 'a: '
        p.send('foo')
        assert p.receive() == 'b: '
        p.send('bar')
        assert p.receive() == 'foobar\n'
