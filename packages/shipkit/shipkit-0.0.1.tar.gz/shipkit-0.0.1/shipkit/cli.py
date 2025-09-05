import sys
from pathlib import Path

import click
import rich

from backend import process
from config import read_config_file


def find_config_file(root: Path) -> Path | None:
    root = root.resolve()
    path = root / "shipkit.toml"
    if path.exists():
        return path

    if str(root) != root.anchor:
        root = root.parent
        return find_config_file(root)
    else:
        return None


@click.command()
@click.argument(
    "config", type=click.Path(exists=True, file_okay=True, dir_okay=False), required=False
)
def main(config: Path | None = None):
    """
    Bla bla
    """
    if isinstance(config, str):
        config = Path(config)

    if config is None:
        rich.print(
            "No shipkit.toml config file provided. Searching for config file in parent directories."
        )
        config = find_config_file(Path())

    if not config:
        rich.print("No config file found")
        return

    shipkit_config = read_config_file(config)
    if not shipkit_config:
        return

    ret = process(shipkit_config)
    sys.exit(ret)


if __name__ == "__main__":
    main()
