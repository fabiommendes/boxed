Boxed is a simple sandboxing solution for Python. It works by running arbitrary
Python functions in a separate python interpreter as an unprivileged user.

The API is very simple::

    from boxed import run

    result = run(target_func, args=args, kwargs=kwargs)

This will spawn a Python interpreted that drops its privileges and runs
``target_func(*args, **kwds)`` as the **nobody** user. Communication
between the master and slave processes is done using serialized streams
which can use pickle, cloudpickle, dill or JSON.

There is a possible vulnerability if the target function outputs a
picklable object that produces malicious side-effects when unpickled. We don't
know how to exploit this vulnerability, but it is theoretically possible, so be
warned. Dill and cloudpickle are likely to be more vulnerable since both can
pickle function bytecodes, opening many doors for attack.

The possibility of damage is greatly reduced by using the JSON serializer.
The downside is that both inputs and outputs must be JSON-compatible (i.e., they
must be composed of basic types such as numbers, strings, lists and dicts.
Besides that, the target function itself must be a Python callable living in a
public namespace. The JSON serializer just sends the function full qualified
name to the sandbox and import this function there.

::

    >>> from boxed import run
    >>> from math import sqrt
    >>> run(sqrt, args=(4,), serializer='json')
    2.0



How does it work?
=================

The sandbox is spawned as a different Python interpreter using the python_boxed
executable which is created during installation. This is just a copy of the regular
interpreter with Linux's SETUID capability enabled. This simple technique allows a
process to change its UID during execution, which enable it to drop its privileges
early during execution.

This might remember the infamous SUID bit. SUID executables allows an user to spawn
program that starts its life with super user permissions and (hopefully) drop
them as soon as possible while keeping only the permissions necessary for it
to run. The classical example is a web server. Only the super user can
listen to port 80 (or any other lower ports), thus the web server must start its
life as root and quickly drop all privileges but those necessary to communicate in
the desired ports.

Linux capabilities is a fine-grained version of the SUID bit. It grants
very specific privileges to a program. The ``boxed`` library uses a Python
interpreter with the SETUID capability which grant us only the
permission of changing the UID of a process. Even if the process escalates its
privileges to run with UID=0 (the super user), none of the other permissions are
granted so it will not gain super powers. In particular, it will not be
able to read, write or execute any file that user who executed the sandbox did
not have access to.

By default, ``boxed`` runs the sandbox as the `nobody` user. We create a copy of
the interpreter called /usr/bin/python_boxed during installation and then apply
the command::

    $ setcap cap_setuid+ep /usr/bin/python_boxed


Does it work on Windows, OSX, BSD, etc?
=======================================

No. This technique is linux-specific. Also, it is very difficult to provide a good,
lightweight, and cross-platform sandboxing solution. We have no plans to implement
sandboxing in other platforms.