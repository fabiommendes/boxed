import os
import io
import sys
import math
import pytest
from boxed.picklebox import run
from boxed.errors import SerializationError


def write_to_file(path, data):
    with open(path, 'w') as F:
        F.write(data)


def return_non_picklable_object():
    return lambda x: x*x


def test_basic_sandbox_run():
    assert run(math.sqrt, args=(4.0,)) == 2.0


def test_forbidden_sandbox_run():
    try:
        write_to_file('trash.dat', 'foo')
        with pytest.raises(PermissionError):
            run(os.unlink, args=('trash.dat',))
    finally:
        os.unlink('trash.dat')


def test_error_propagates_from_sandbox():
    with pytest.raises(ValueError):
        run(math.sqrt, args=(-1,))


def test_cannot_run_as_root():
    with pytest.raises(PermissionError):
        run(math.sqrt, (2,), user='root')


def test_cannot_run_as_invalid_user():
    with pytest.raises(PermissionError):
        run(math.sqrt, (2,), user='this_is_an_invalid_username')


def test_output_pass_through_sandbox():
    out = io.StringIO()
    stdout, sys.stdout = sys.stdout, out
    try:
        result = run(print, args=('hello world',), print_messages=False)
    finally:
        sys.stdout = stdout

    assert result is None
    assert out.getvalue() == 'hello world\n'


def test_serialization_error():
    with pytest.raises(SerializationError):
        run(return_non_picklable_object)


def test_json_serializer():
    assert run(math.sqrt, (4,), serializer='json') == 2
