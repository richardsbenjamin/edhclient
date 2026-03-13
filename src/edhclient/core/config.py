import importlib.resources
import tomllib

class EDHConfig:
    def __init__(self):
        self._load_config()

    def _load_config(self):
        config_file = importlib.resources.files("edhclient.config").joinpath("config.toml")
        
        if not config_file.is_file():
             raise FileNotFoundError("config.toml not found in edhclient.config")

        with config_file.open("rb") as f:
            data = tomllib.load(f)
            auth_data = data.get("auth", {})
            for key, value in auth_data.items():
                setattr(self, key.upper(), value)

            datasets_data = data.get("datasets", {})
            for key, value in datasets_data.items():
                setattr(self, key.upper(), value)


edh_config = EDHConfig()