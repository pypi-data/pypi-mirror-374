import sys
import tomllib
from pathlib import Path

from pydantic import BaseModel, ValidationError


class ConfigStack(BaseModel):
    name: str
    # server: str
    # source_dir: str | Path
    # target_dir: str


class ConfigServer(BaseModel):
    ip: str
    user: str = "root"
    ensure_docker: bool = True
    apt: list[str] = []


class ConfigBuild(BaseModel):
    tags: list[str] = []
    root: str | Path


class Config(BaseModel):
    stack: ConfigStack
    server: ConfigServer
    build: dict[str, ConfigBuild]


def resolve_path(config_file_root: Path, param_name: str, path_str: str | Path) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = config_file_root / path

    if not path.exists():
        print(f"❌ {param_name} `{path}` does not exist.")
        sys.exit(1)

    return path.resolve()


def read_config_file(config_path: Path) -> Config | None:
    with open(config_path, "rb") as f:
        toml_data = tomllib.load(f)
        try:
            config = Config.model_validate(toml_data)
        except ValidationError as e:
            print("❌ Invalid configuration found. Here are the issues:")
            for error in e.errors():
                field_path = ".".join(map(str, error["loc"]))
                error_message = error["msg"]
                print(f"  - **Field `{field_path}`**: {error_message}")
            return None

    # check if directories exist and set optional fields
    # config.stack.source_dir = resolve_path(
    #     Path(config_path).parent, "stack.source_dir", config.stack.source_dir
    # )

    if config.server.ensure_docker:
        if "docker.io" not in config.server.apt:
            config.server.apt.append("docker.io")
        if "docker-compose-v2" not in config.server.apt:
            config.server.apt.append("docker-compose-v2")

    for service, d in config.build.items():
        if len(d.tags) == 0:
            d.tags.append(service)  # the default tag is the service name
        d.root = resolve_path(Path(config_path).parent, f"build.{service}.root", d.root)

    return config
