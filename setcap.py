import os
import sys


def main():
    py_path = os.path.realpath(sys.executable)
    boxed_path = '/usr/bin/python_boxed'
    with open(py_path, 'rb') as src:
        with open(boxed_path, 'wb') as dest:
            dest.write(src.read())
    os.system('setcap cap_setuid+ep %s' % boxed_path)
    os.system('chmod +x %s' % boxed_path)
    os.system('ls -lha /usr/bin/python*')


if __name__ == '__main__':
    main()
