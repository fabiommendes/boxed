Boxed is a simple sandboxing solution to Python. It works by running arbitrary
Python functions as an unprivileged user. It relies on the builtin Linux Kernel
security, which is very good.

The API is very simple::

    from boxed import run

    result = run(target_func, args=args, kwargs=kwargs)

This will spawn a Python interpreted that drops its privileges and runs
``target_func(*args, **kwds)`` as the **nobody** user. Communication
between the master and slave processes can is carried by serialized streams
which can use pickle, cloudpickle, dill or JSON.

There is a possible vulnerability if the target function outputs a
picklable object that produces malicious side-effects when unpickled. We don't
know how to exploit this possibility, but it is theoretically possible. It is
probably not even hard to exploit using dill or cloudpickle as the serializers
since both can pickle functions by bytecode, opening many doors for attack.

The possibility of damage is greatly reduced by using a JSON serializer. The
downside is that both the inputs and the outputs of the target function must
be serializable as JSON. Besides that, the target function itself must be a
Python callable living in a public namespace: the JSON serializer just sends the
function qualified name to the sandbox. In order to use the JSON serializer,
just pass the serializer='json' argument::

    >>> from boxed import run
    >>> from math import sqrt
    >>> run(sqrt, args=(4,), serializer='json')
    2.0


How does it work?
=================

The sandbox is spawned by in a different Python interpreter called python_setuid
which is created on installation. This is just a copy of the regular interpreter
with the Linux SETUID capability enabled. This simple technique allows the
executable to change its UID, which enable it to drop its privileges early
during the sandbox execution.

This might remember the infaous SUID bit. SUID executables allows an user spawn
program to start its life with super user permissions and (hopefully) to drop
them as soon as possible while keeping only the permissions necessary for the
program to run. The classical example is a webserver. Only the super user can
listen to port 80 (or the other lower ports), thus the webserver must start its
life as root and quickly drop all privileges but that of communicating in the
desired ports.

Linux capabilities are a fine-grained version of the SUID bit. We can grant
very specific privileges to any file. The boxed library uses a Python
interpreter with the SETUID capability which grant us only the
capability of changing the UID of a process. Even if the process escalates its
privileges to run as UID=0 (the super user), none of the other permissions are
granted so it will not gain super user powers. In particular, it will not be
able to read, write or execute any file that the original user who executed
the sandbox did not have access to.

By default, boxed runs the sandbox as the `nobody` user. Upon installation,
we create a copy of the interpreter called /usr/bin/python_boxed and then
apply the command::

    $ setcap cap_setuid+ep /usr/bin/python_boxed


Does it work on Windows, OSX, BSD, etc?
=======================================

No. This technique is linux-specific. Also, it is very difficult to provide a good,
lightweight, and crossplatform sandboxing solution. Currently we have no plans
to implement sandboxing in other platforms.