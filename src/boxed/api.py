"""
Common interface to different sandboxing environments.
"""

from boxed.core import SerializationError
from boxed.simplebox import run as simplebox_run

__all__ = ['run', 'SerializationError']


def run(target, args=(), kwargs=None, *, timeout=None,
        method='best', **kwds):
    """Run target function in a sandboxed environment and return the results.

    Everything is pickle-encoded and transmitted to the sandboxed child process.
    All arguments and return type must be pickable and any modification the
    target function makes to the input arguments is not transmitted back from
    the function call.

    Parameters
    ----------

    target : callable
        Callable that shall be executed in the sandbox.
    args, kwargs :
        Arguments passed to the callable.
    timeout : float
        The maximum allowed time in seconds. If no timeout is given, there will
        be no time limits for execution.
    method : str
        The sandboxing strategy. For now, only the 'simple' strategy is
        implemented.
    serializer : 'pickle', 'dill' or 'cloudpickle'
        The pickler used to transmit data from/to the sandbox. The default
        pickler is the fastest but cannot handle a few objects. Dill and
        cloudpickle are similar alternatives that extend Python's default
        pickler to handle a vast array of new objects.
    """

    if method in ['best', 'simple']:
        return simplebox_run(target, args, kwargs, timeout=timeout, **kwds)
    else:
        raise ValueError('invalid sandbox: %r' % method)
