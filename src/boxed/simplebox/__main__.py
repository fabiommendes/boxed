import io
import os
import pwd
import sys
import importlib
from boxed.core import CommunicationPipe, SerializationError

# Caches the real stderr and stdout
real_stderr = sys.stderr
real_stdout = sys.stdout
sys.stdout = sys.stderr = io.StringIO()


# Utility
def serialization_error(error):
    if is_json:
        return {'error': 'SerializationError',
                'message': str(error)}
    else:
        return SerializationError(str(error))


# Load the list of modules before setuid (the running user may not have access
# to all modules that the calling user has).
handshake = 'python-boxed::0.1'
conn = CommunicationPipe(real_stdout)
conn.sendraw(handshake)
msg = conn.recvraw()
if msg != handshake:
    raise SystemExit(1)

for mod in conn.recvraw().split():
    importlib.import_module(mod)
conn.serializer = conn.recvraw()
is_json = conn.serializer == 'json'


# Sets the UID to the low privilege user in order to prevent harm...
username = conn.recvraw()
if username == 'root':
    conn.senderror(PermissionError('cannot change user to root'))
    raise SystemExit(1)
else:
    try:
        userinfo = pwd.getpwnam(username)
        os.setuid(userinfo.pw_uid)
    except KeyError:
        conn.senderror(PermissionError('invalid username: %s' % username))
        raise SystemExit(1)
    except Exception as exc:
        conn.senderror(exc)
        raise SystemExit(1)
conn.send(None)


# Start interaction with Python master: transfer data using b85 encoded pickled
# streams. The main process reads an input string from stdin and prints back
# the result to stdout. This is done until an empty string is received.
while True:
    # Fetch data
    if not conn.recvnumber():
        raise SystemExit(0)
    func, args, kwds = conn.recv()
    if is_json:
        mod, _, name = func.rpartition('.')
        try:
            mod = importlib.import_module(mod)
            func = getattr(mod, name)
        except Exception as exc:
            conn.send(serialization_error(
                'could not recover function %s. got an %s: %s' %
                (func, type(exc).__name__, exc)))
            continue

    # Execute capturing stderr and stdout
    out = io.StringIO()
    err = io.StringIO()
    exc = None

    try:
        real_stdout, sys.stdout = sys.stdout, out
        real_stderr, sys.stderr = sys.stderr, err
        result = func(*args, **kwds)
    except Exception as ex:
        result = None
        exc = ex
    finally:
        sys.stdout = real_stdout
        sys.stderr = real_stderr

    out = out.getvalue()
    err = err.getvalue()

    # Send results
    try:
        data = conn.prepare([result, out, err])
    except Exception as exc:
        conn.senderror(exc)
    else:
        conn.send(None)
        if exc is None:
            conn.send(None)
        else:
            conn.senderror(exc)
        conn.sendraw(data)
