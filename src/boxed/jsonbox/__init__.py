import json
from boxed.core import return_from_status_data, execute_subprocess, indent, SerializationError


def run(target, args=(), kwargs=None, *, timeout=None, user='nobody',
        imports=()):
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
        'user': user,
        'imports': imports,
    }
    try:
        serialized = json.dumps(data)
    except Exception as ex:
        raise SerializationError(ex)

    # Execute a subprocess by sending the input JSON structure. We should
    # receive another JSON structure and interpret it
    json_data, comments = execute_subprocess(
        ['python_boxed', '-m', 'boxed.jsonbox'],
        inputs=serialized,
        timeout=timeout,
        args=args,
        kwargs=kwargs,
        target=target,
    )

    # The output should be JSON-encodable and contain the result of
    # execution
    try:
        result = json.loads(json_data)
    except Exception as ex:
        ex_name = type(ex).__name__
        raise SerializationError(
            '%s: %r\n'
            'Payload:\n'
            '%s\n'
            'Debug:\n'
            '%s' % (ex_name, ex, indent(json_data, 4), indent(comments, 4))
        )

    return return_from_status_data(result)
