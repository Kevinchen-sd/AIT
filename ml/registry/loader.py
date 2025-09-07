import yaml, importlib
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent

def load_model(name: str, version: str | None = None):
    spec_path = REGISTRY_PATH / f"{name}.yaml"
    spec = yaml.safe_load(spec_path.read_text())
    if version and version != spec["version"]:
        raise ValueError(f"Expected {version}, found {spec['version']}")
    module = importlib.import_module(spec["artifact"].replace("/", ".").removesuffix(".py"))
    cls = getattr(module, spec["entrypoint"])
    return cls(spec.get("params", {})), spec
