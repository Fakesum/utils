# Legecy
from .tomlsettings.tomlsettings import loader
import sys

sys.modules[__name__] = loader()