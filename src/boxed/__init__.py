from .__meta__ import __author__, __version__
from .runners import *
import os as _os

if 'BOXED_COVERAGE' in _os.environ:
    import boxed.coverage.__main__ as _patch
