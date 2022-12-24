# Legecy
import .tomlsettings.loader as loader
import sys

sys.modules[__name__] = loader()