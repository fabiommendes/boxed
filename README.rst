Boxed is a simple sandboxing solution to Python. It works by running arbitrary
Python functions in a regular interpreter as an unprivileged user.

The API is very simple::

    from boxed import run

    result = run(target_func, args=args, kwargs=kwargs)

This will spawn a Python interpreted that drops its privileges and runs
``target_func(*args, **kwds)`` as the **nobody** user. Communication
between the master and slave processes is carried by serialized streams
which can use pickle, cloudpickle, dill or JSON.

There is a possible vulnerability if the target function outputs a
picklable object that produces malicious side-effects when unpickled. We don't
know how to exploit it, but it is theoretically possible so be warned. It is
probably not so to break from the sandbox if you are using dill or cloudpickle
as the serializers since both can pickle function bytecodes, opening many doors
for attack.

The possibility of damage is greatly reduced by using the JSON serializer.
The downside is that both inputs and outputs must be JSON-compatible (i.e., they
must be composed of basic types such as numbers, strings, lists and dicts.
Besides that, the target function itself must be a Python callable living in a
public namespace: the JSON serializer just sends the function full qualified
name to the sandbox and import this function there.

::

    >>> from boxed import run
    >>> from math import sqrt
    >>> run(sqrt, args=(4,), serializer='json')
    2.0



How does it work?
=================

The sandbox is spawned by in a different Python interpreter called python_boxed
which is created during installation. This is just a copy of the regular interpreter
with the Linux SETUID capability enabled. This simple technique allows a process
to change its UID during execution, which enable it to drop its privileges early
during the sandbox execution.

This might remember the infaous SUID bit. SUID executables allows an user to spawn
program that starts its life with super user permissions and (hopefully) drop
them as soon as possible while keeping only the permissions necessary for it
to run. The classical example is a webserver. Only the super user can
listen to port 80 (or the other lower ports), thus the webserver must start its
life as root and quickly drop all privileges but that of communicating in the
desired ports.

Linux capabilities are a fine-grained version of the SUID bit. We can grant
very specific privileges to any file. The boxed library uses a Python
interpreter with the SETUID capability which grant us only the
permission of changing the UID of a process. Even if the process escalates its
privileges to run as UID=0 (the super user), none of the other permissions are
granted so it will not gain super powers. In particular, it will not be
able to read, write or execute any file that user who executed the sandbox did
not have access to.

By default, boxed runs the sandbox as the `nobody` user. Upon installation,
we create a copy of the interpreter called /usr/bin/python_boxed and then
apply the command::

    $ setcap cap_setuid+ep /usr/bin/python_boxed


Does it work on Windows, OSX, BSD, etc?
=======================================

No. This technique is linux-specific. Also, it is very difficult to provide a good,
lightweight, and cross-platform sandboxing solution. Currently we have no plans
to implement sandboxing in other platforms.