import sys
from . import loader

sys.modules[__name__] = loader()
