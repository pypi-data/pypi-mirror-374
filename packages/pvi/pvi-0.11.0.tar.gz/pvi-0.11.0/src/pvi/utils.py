from pathlib import Path


def find_pvi_yaml(yaml_name: str, yaml_paths: list[Path]) -> Path | None:
    """Find a yaml file in given directory"""
    for yaml_path in yaml_paths:
        if yaml_path.is_dir():
            if yaml_name in [f.name for f in yaml_path.iterdir()]:
                return yaml_path / yaml_name
    return None
