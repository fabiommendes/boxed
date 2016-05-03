import io
import sys
import json
import pwd
import os
import importlib
import traceback
from boxed.core import SerializationError

# Read data and check handshake
data = json.loads(input())
if data['header'] != 'jsonbox::0.1':
    print(json.dumps({
        'status': 'invalid-handshake',
        'handshake': 'jsonbox::0.1',
    }))
    raise SystemExit(0)


# Sets the UID to the low privilege user in order to prevent harm...
try:
    username = data.get('user', 'nobody')
    if username == 'root':
        raise PermissionError
    userinfo = pwd.getpwnam(username)
except (KeyError, PermissionError):
    print(json.dumps({
        'status': 'invalid-user',
    }))
    raise SystemExit(0)
os.setuid(userinfo.pw_uid)


# Caches the real stderr and stdout
real_stderr = sys.stderr
real_stdout = sys.stdout
sys.stdout = sys.stderr = io.StringIO()


# Execute target function
mod, _, func = data['target'].partition('.')
mod = importlib.import_module(mod)
target = getattr(mod, func)
try:
    output = target(*data['args'], **data['kwargs'])
except Exception as ex:
    tb_data = io.StringIO()
    traceback.print_tb(ex.__traceback__, limit=-2, file=tb_data)
    print(json.dumps({
        'status': 'exception',
        'type': ex.__class__.__name__,
        'message': str(ex),
        'traceback': tb_data.getvalue(),
    }), file=real_stdout)
    raise SystemExit(0)

# Convert result to JSON and return
data = {
    'status': 'success',
    'stdout': sys.stdout.getvalue(),
    'output': output,
}

try:
    print(json.dumps(data), file=real_stdout)
except ValueError:
    print(json.dumps({
        'status': 'serialization-error',
        'output': str(output),
    }), file=real_stdout)
