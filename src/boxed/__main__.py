import subprocess
import sys

import boxed


def exec_func(*args, **kwargs):
    out = subprocess.check_output(*args, **kwargs)
    return out.decode('utf8')


def main():
    """
    Run a program in sandbox.
    """

    if sys.argv[1:]:
        try:
            out = boxed.run(exec_func, args=[sys.argv[1:]], serializer='json')
            print(out)
        except RuntimeError as ex:
            raise SystemExit(ex)
    else:
        print('boxed COMMAND [args]\n'
              '\n'
              'Run given command in a sandboxed environment')


if __name__ == '__main__':
    main()
