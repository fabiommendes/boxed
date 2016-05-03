from boxed.core import return_from_status_data, execute_subprocess, indent
from boxed.core import get_serializer, get_deserializer, SerializationError


def run(target, args=(), kwargs=None, *, timeout=None, user='nobody',
        imports=(), serializer='pickle'):
    """Simple sandboxing based on the existence of the python executable
    `python_boxed` with setuid capabilities.

    This function communicates with the slave process with a JSON-based stream.

    This sandboxing relies on changing the uid to the unprivileged user nobody.
    """

    # Chooses the pickler
    serializer_func = get_serializer(serializer)

    # Creates and serializes input data
    data = {
        'header': 'picklebox::0.1',
        'target': '%s.%s' % (target.__module__, target.__qualname__),
        'args': args,
        'kwargs': kwargs or {},
        'user': user,
        'imports': imports,
    }
    serialized = serializer_func(data)

    # Execute a subprocess by sending the input JSON structure. We should
    # receive another JSON structure and interpret it
    json_data, comments = execute_subprocess(
        ['python_boxed', '-m', 'boxed.picklebox'],
        inputs='%s\n%s' % (serializer, serialized),
        timeout=timeout,
        args=args,
        kwargs=kwargs,
        target=target,
    )

    # The output should be a pickle stream and would contain the result of
    # execution
    deserializer = get_deserializer(serializer)
    result = deserializer(json_data)
    return return_from_status_data(result)
