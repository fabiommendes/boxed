from boxed.core import SerializationError
from subprocess import PIPE, Popen
import json
import builtins


# Maps exception names to their corresponding classes
exceptions = {
    k: v
    for k, v in vars(builtins).items()
    if isinstance(v, type) and issubclass(v, Exception)
}
exceptions['SerializationError'] = SerializationError


def run(target, args=(), kwargs=None, *, timeout=None, user='nobody'):
    """Simple sandboxing based on the existence of the python executable
    `python_boxed` with setuid capabilities.

    This function communicates with the slave process with a JSON-based stream.

    This sandboxing relies on changing the uid to the unprivileged user nobody.
    """

    # Creates and serializes input data
    data = {
        'header': 'jsonbox::0.1',
        'target': '%s.%s' % (target.__module__, target.__qualname__),
        'args': args,
        'kwargs': kwargs or {},
        'timeout': timeout,
        'user': user
    }
    serialized = json.dumps(data)

    # Execute a subprocess by sending the input JSON structure. We should
    # receive another JSON structure and interpret it
    cmd = ['python_boxed', '-m', 'boxed.jsonbox']
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                 universal_newlines=True)
    box_out, box_err = proc.communicate(input=serialized, timeout=timeout)

    # The subprocess should never raise exceptions or write in the stderr
    if box_err:
        raise RuntimeError(
            'error running function %s with:\n'
            '    args=%r\n'
            '    kwargs=%r\n\n'
            'Process returned code %s.\n'
            'Stdout:\n%s\n'
            'Error message:\n%s' % (
                data['target'], args, kwargs, proc.poll(),
                indent(box_out or '<empty>', 4),
                indent(box_err or '<empty>', 4)
            )
        )

    # The output should be JSON-encodable and would contain the result of the
    # execution
    try:
        result = json.loads(box_out)
    except ValueError:
        box_out = box_out.decode('utf8', errors='ignore')
        box_out = '\n'.join('    ' + line for line in box_out.splitlines())
        raise RuntimeError(
            'subprocess returned an invalid output:\n%s' % box_out
        )

    # Now we interpret the message using the status field of the resulting
    # JSON data
    if 'status' not in result:
        raise RuntimeError('invalid JSON output')
    status = result['status']

    if status == 'success':
        print(result['stdout'], end='')
        return result['output']

    elif status == 'invalid-handshake':
        raise RuntimeError(
            'the version of boxed installed in the subprocess is invalid.\n'
            'Handshake message: %s' % result['handshake']
        )

    elif status == 'invalid-user':
        if user == 'root':
            raise PermissionError('cannot run as superuser')
        else:
            raise PermissionError('user does not exist: %s' % user)

    elif status == 'exception':
        print('Error while running sandboxed function %s(...)' %
              target.__qualname__)
        print(result['traceback'], end='')

        try:
            exc = exceptions[result['type']]
            msg = result['message']
            raise exc(msg)
        except KeyError:
            data = '%s(%r)' % (result['type'], result['message'])
            raise RuntimeError('failed with unknown exception: %s' % data)

    elif status == 'serialization-error':
        raise SerializationError(
            'output could not be converted to JSON: %s' % result['output']
        )

    else:
        raise RuntimeError('invalid status: %s' % status)


def indent(msg, indent):
    """Indent message"""

    prefix = ' ' * indent
    return '\n'.join('    ' + line for line in msg.splitlines())

