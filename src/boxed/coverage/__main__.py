# An ugly ugly hack to fix permission errors when coverage is called within
# a boxed target.


# We first patch the infringing method on coverage.data.CoverageData class.
# Now .coverage.xxx.xxxxx files have a 666 permissions
import os
import stat

from coverage.data import CoverageData

if not os.path.exists('/tmp/boxed/'):
    os.mkdir('/tmp/boxed')
    os.chmod('/tmp/boxed',
             stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH |
             stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH |
             stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


# Patch write_file to change names from .coverageXXX to /tmp/boxed/.coverageXXX
# These files also gain 666 permissions to be manipulated by both the default
# user and nobody
def write_file(self, filename):
    """
    Write the coverage data to `filename`.
    """

    if self._debug and self._debug.should('dataio'):
        self._debug.write("Writing data to %r" % (filename,))

    covname = os.path.abspath('.coverage')
    if filename.startswith(covname):
        filename = '/tmp/boxed/.coverage' + filename[len(covname):]

    if not filename.startswith('/tmp/'):
        raise ValueError('invalid file to write', filename)

    with open(filename, 'w') as fdata:
        self.write_fileobj(fdata)

    os.chmod(filename,
             stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH |
             stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


CoverageData.write_file = write_file


# Only now we execute the py.test runner. It is necessary to patch coverage
# first otherwise it does not work.
if __name__ == '__main__':
    from pytest import main

    main()
