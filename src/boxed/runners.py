"""
Common interface to different sandboxing environments.
"""

from boxed.core import SerializationError
from boxed.jsonbox import run as run_jsonbox
from boxed.picklebox import run as run_picklebox

__all__ = ['run', 'SerializationError']


def run(target, args=(), kwargs=None, *, timeout=None,
        method='best', **kwds):
    """
    Run target function in a sandboxed environment and return the results.

    The target function executes on a different python interpreter under a low
    privilege user. Everything is serialized and transmitted to the sandbox
    using either pickle, json or some other serialization protocol.

    The input arguments and return value must be serializable using the given
    protocol and any modification that the target function makes to the input
    arguments is not transmitted back from the function call.

    Args:
        target:
            Callable that shall be executed in the sandbox.
        args, kwargs:
            Position and named arguments passed to the callable.
        timeout:
            The maximum allowed time in seconds. If no timeout is given, there will
            be no time limits for execution.
        method:
            The sandboxing strategy. For now, only the 'simple' strategy is
            implemented.
        imports
            A list of modules that should be imported before lowering privileges.
            Remember that a low privilege user may not be able to import modules
            installed in the local user folders.
        serializer:
            'json', 'pickle', 'dill' or 'cloudpickle'.

            The protocol used to transmit data from/to the sandbox. Going from
            JSON to cloudpickle we trade security with the ability to handle more
            argument types. Remember that malicious code can make pickle execute
            arbitrary data during unpickling (which is done outside the sandbox).
        print_messages:
            If True, print debugging messages.
    """

    if method in ['best', 'simple']:
        return run_simplebox(target, args, kwargs, timeout=timeout, **kwds)
    else:
        raise ValueError('invalid sandbox: %r' % method)


def run_simplebox(target, args=(), kwargs=None, *, timeout=None,
                  serializer='pickle', imports=(), user='nobody', **extra):
    """Executes the target function with given args and kwargs using a simple
    sandbox based on running a python interpreter with setuid capabilities.

    This sandboxing relies on changing the UID to an unprivileged user.
    """

    runkwargs = {'timeout': timeout, 'imports': imports, 'user': user}
    runkwargs.update(extra)

    if serializer == 'json':
        return run_jsonbox(target, args, kwargs, **runkwargs)
    else:
        runkwargs['serializer'] = serializer
        return run_picklebox(target, args, kwargs, **runkwargs)
