import os
import io
import sys
import math
import pytest
import boxed
from boxed import SerializationError


@pytest.fixture
def run():
    from boxed import jsonbox

    return jsonbox.run


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
