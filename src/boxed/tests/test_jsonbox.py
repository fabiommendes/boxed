import io
import math
import os
import sys

import pytest
from boxed.core import capture_print


@pytest.fixture
def run():
    from boxed import jsonbox

    return jsonbox.run


def function_that_causes_an_error():
    function_that_raises_an_error()


def function_that_raises_an_error():
    raise ValueError('yeah, it\'s an error!')


def write_to_file(path, data):
    with open(path, 'w') as F:
        F.write(data)


def test_basic_sandbox_run(run):
    assert run(math.sqrt, args=(4.0,)) == 2.0


def test_forbidden_sandbox_run(run):
    try:
        write_to_file('trash.dat', 'foo')
        with pytest.raises(PermissionError):
            run(os.unlink, args=('trash.dat',))
    finally:
        os.unlink('trash.dat')


def test_error_propagates_from_sandbox(run):
    with pytest.raises(ValueError):
        run(math.sqrt, args=(-1,))


def test_cannot_run_as_root(run):
    with pytest.raises(PermissionError):
        assert run(math.sqrt, (2,), user='root') == math.sqrt(2)


def test_cannot_run_as_invalid_user(run):
    with pytest.raises(PermissionError):
        run(math.sqrt, (2,), user='this_is_an_invalid_username')


def test_output_pass_through_sandbox(run):
    out = io.StringIO()
    stdout, sys.stdout = sys.stdout, out
    try:
        run(print, args=('hello world',), print_messages=False)
    finally:
        sys.stdout = stdout

    assert out.getvalue() == 'hello world\n'


def test_original_traceback_can_be_retrieved_in_debugging_messages(run):
    with capture_print() as data:
        with pytest.raises(ValueError):
            run(function_that_causes_an_error, print_messages=True)

    comments = data.read()
    assert 'function_that_raises_an_error' in comments
    assert 'function_that_causes_an_error' in comments
    assert 'ValueError' in comments
    assert 'Traceback' in comments
