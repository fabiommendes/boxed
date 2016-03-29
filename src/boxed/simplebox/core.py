import sys
import io
from boxed.core import CommunicationPipe, SerializationError
from subprocess import PIPE, Popen


def run(target, args=(), kwargs=None, *, timeout=None, serializer='pickle',
        imports=(), user='nobody'):
    """Simple sandboxing based on a python executable with setuid capabilities.

    This sandboxing relies on changing the uid to the unprivileged user nobody.
    """

    # Add target module to imports
    try:
        imports = list(imports)
        if target.__module__ not in imports:
            imports.append(target.__module__)
    except AttributeError:
        pass

    # Prepare communication
    conn = CommunicationPipe(stdout=io.StringIO(), serializer=serializer)
    conn.sendraw(' '.join(imports))
    conn.sendraw(serializer)
    conn.sendraw(user)

    # Single interaction
    if serializer == 'json':
        target = '%s.%s' % (target.__module__, target.__qualname__)
    if kwargs is None:
        kwargs = {}
    conn.sendnumber(1)                  # open execution
    conn.send([target, args, kwargs])
    conn.sendnumber(0)                  # close execution

    # Open subprocess and perform communication
    cmd = ['python_boxed', '-m', 'boxed.simplebox']
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                 universal_newlines=True)
    box_out, box_err = proc.communicate(input=conn.stdout.getvalue(),
                                        timeout=timeout)

    # Read messages from the connexion
    conn.stdin = io.StringIO(box_out)
    exc = conn.recv()  # was the username accepted?
    if exc is not None:
        raise_exc(exc)
    exc = conn.recv()  # was the result serialized correctly?
    if exc is not None:
        raise_exc(exc)

    # Process successful run
    if proc.poll() == 0:
        result, exc, out, err = conn.recv()

        # Print the output from stdout and stderr
        if out:
            print(out, end='')
        if err:
            print(err, end='', file=sys.stderr)

        # Return or raise message
        if exc is None:
            return result
        else:
            raise exc

    else:
        error_code = proc.poll()
        func_name = getattr(target, '__name__', str(target))
        raise RuntimeError(
            'error running function %s with:\n'
            '    args=%r\n'
            '    kwargs=%r\n\n'
            'Process returned code %s.\n'
            'Stdout:\n%s\n'
            'Error message:\n%s' % (
                func_name, args, kwargs, error_code,
                indent(box_out or '<empty>', 4),
                indent(box_err or '<empty>', 4)
            )
        )


def indent(msg, indent):
    """Indent message"""

    prefix = ' ' * indent
    return '\n'.join('    ' + line for line in msg.splitlines())


def raise_exc(exc):
    errormap = {
        'SerializationError': SerializationError,
    }

    if isinstance(exc, dict):
        try:
            exc = errormap[exc['error']](exc['message'])
        except KeyError:
            raise RuntimeError('invalid exception dictionary: %s' % exc)

    raise exc
