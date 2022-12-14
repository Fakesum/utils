import sys

def __botloader() -> dict:
    import toml
    template = toml.load(".config.template")
    config = toml.load("config.toml")

    def validate(keys):
        for key in keys:
            if type(key) == dict:
                validate(key)
            try:
                config[key]
            except KeyError:
                if "optional" in template[key] and template[key]["optional"] == True:
                    if "default" in template[key]:
                        config[key] = template[key]["default"]
                    continue
                else:
                    raise RuntimeError("non-optional key ", key, " not in config.toml")
            if "type" in template[key]:
                if not (type(config[key]) == eval(template[key]["type"])):
                    raise RuntimeError(f"""{key} in config.toml should be of type: {template[key]["type"]}""")
            
            if "range" in template[key]:
                if not (template[key]["range"][1] >= config[key] >= template[key]["range"][0]):
                    raise RuntimeError(f"""{key} in config.toml should be between range {template[key]["range"][0]} - {template[key]["range"][1]}""")
            
    validate(template.keys())
    return config

try:
    sys.modules[__name__] = __botloader()
except FileNotFoundError:
    raise RuntimeError(".config.template and config.toml do not exsit")