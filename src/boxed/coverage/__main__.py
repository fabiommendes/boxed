# An ugly ugly hack to fix permission errors when coverage is called within
# a boxed target.


# We first patch the infringing method on coverage.data.CoverageData class.
# Now .coverage.xxx.xxxxx files have a 666 permissions
from coverage.data import CoverageData
import os


def write_file(self, filename):
    self._original_write_file(filename)
    os.chmod(filename, 666)

CoverageData._original_write_file = CoverageData.write_file
CoverageData.write_file = write_file


# Only now we execute the py.test runner. It is necessary to patch coverage
# first otherwise it does not work.
if __name__ == '__main__':
    from pytest import main
    main()
