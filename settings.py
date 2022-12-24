# Legecy
from .tomlsettings import loader as loader
import sys

sys.modules[__name__] = loader()