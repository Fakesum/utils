# toml settings
A Config Loading and checking library

## Usage
This Library Checks a `config.toml` file through the specs given in a `.coinfig.template` As long as
The `Config.toml` and `.config.template` are in the same dir as the dir where python is run from.
For Example:

make_requests.py
```python
import toml_settings as settings
import requests

requests.get(settings["site"], headers=settings["headers"])
```

config.toml
```python
site = "https://example.com"

[headers]
useragents = "EX"
cookies={"one": "1", "two": 2}
```

.config.template
```python
site = {type="str"}

[headers]
cookies={optional=true, type='dict', default={}}
```
The options for checkinfg if the given option is valid, is:
1) optional, if true then it will not throw an error if missing
2) default, if optional and not specified it will use this value instead
3) type, checks if this is the correct python type.

if that is not the case, you can give it a path by importing `from toml_settings import loader` which
can be used as:
```python
from toml_settings import loader
settings = loader("./<path-to-template>/.config.template", "./<path-to-config.toml>/config.toml")
```
