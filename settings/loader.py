def loader(template_name = ".config.template", config_name ="config.toml") -> dict:
    import toml
    _template = toml.load(template_name)
    _config = toml.load(config_name)

    def validate(config, template, keys):
        for key in keys:
            if not (key in config):
                if ("optional" in template[key]) and (template[key]["optional"] == True):
                    if "default" in template[key]:
                        config[key] = template[key]["default"]
                    continue
                else:
                    raise RuntimeError(f"non-optional key {key} not in config.toml")

            if type(config[key]) == dict:
                validate(config[key], template[key], template[key].keys())
            
            if "type" in template[key]:
                if not (type(config[key]) == eval(template[key]["type"])):
                    raise RuntimeError(f"""{key} in config.toml should be of type: {template[key]["type"]}""")
            
            if "range" in template[key]:
                if not (template[key]["range"][1] >= config[key] >= template[key]["range"][0]):
                    raise RuntimeError(f"""{key} in config.toml should be between range {template[key]["range"][0]} - {template[key]["range"][1]}""")
        return config
    return validate(_config, _template, _template.keys())

import sys
sys.modules[__name__] = loader