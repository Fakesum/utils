import sys
from . import loader

try:
    sys.modules[__name__] = loader()
except FileNotFoundError:
    raise RuntimeError(".config.template and/or config.toml do not exists")