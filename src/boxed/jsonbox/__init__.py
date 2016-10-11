import json
import logging

from boxed.core import return_from_status_data, execute_subprocess, indent
from boxed.errors import SerializationError

logger = logging.getLogger('boxed.jsonbox')


def run(target, args=(), kwargs=None, *, timeout=None, user='nobody',
        imports=(), print_messages=False):
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
    logger.info('called %s() on sandbox' % data['target'])
    json_data, comments = execute_subprocess(
        ['python_boxed', '-S', '-s', '-m', 'boxed.jsonbox'],
        inputs=serialized,
        timeout=timeout,
        args=args,
        kwargs=kwargs,
        target=target,
    )
    if print_messages:
        print(comments)

    # The output should be JSON-encodable and contain the result of
    # execution
    logger.debug('child sub-process finished. Processing response.')
    return return_from_status_data(json_data, comments, json.loads)
