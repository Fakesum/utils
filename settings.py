# Legecy
from .tomlsettings.toml_settings.loader import loader
import sys

sys.modules[__name__] = loader()