The easiest way to install boxed is using pip::

    $ sudo python -m pip install boxed

This will fetch the archive and its dependencies from the internet and install
it for you. You may need to run ``python3`` in order to select the correct
python version.

If you download the tarball, unpack it, and execute::

    $ sudo python setup.py install

This package must be installed as the superuser since it requires priviledges
to set the correct capabilities to the ``python_boxed`` interpreter.


Troubleshoot
------------

Some Linux distributions (e.g. Ubuntu) install Python without installing pip.
Please install it before. If you don't have root privileges, download the
get-pip.py script at https://bootstrap.pypa.io/get-pip.py and execute it as
``python get-pip.py --user``.
