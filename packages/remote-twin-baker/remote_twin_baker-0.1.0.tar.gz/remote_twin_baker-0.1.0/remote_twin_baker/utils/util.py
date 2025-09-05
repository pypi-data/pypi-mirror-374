from importlib.resources import files

# Third Party Libraries
import yaml


def load_config():
    config_path = files("remote_twin_baker").joinpath("config.yaml")
    with config_path.open("r") as f:
        return yaml.safe_load(f)