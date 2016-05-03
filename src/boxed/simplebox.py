def run(target, args=(), kwargs=None, *, timeout=None, serializer='pickle',
        imports=(), user='nobody'):
    """Executes the target function with given args and kwargs using a simple
    sandbox based on running a python interpreter with setuid capabilities.

    This sandboxing relies on changing the UID to an unprivileged user.
    """

    runkwargs = {'timeout': timeout, 'imports': imports, 'user': user}

    if serializer == 'json':
        from boxed.jsonbox import run
        return run(target, args, kwargs, **runkwargs)
    else:
        runkwargs['serializer'] = serializer
        from boxed.picklebox import run
        return run(target, args, kwargs, **runkwargs)

