import os
from pathlib import Path

import click
from click_aliases import ClickAliasedGroup

from .db_util import modify_app_module


@click.group(cls=ClickAliasedGroup)
def db_main():
    pass


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)
        open(os.path.join(path, "__init__.py"), "a").close()
    return path


@db_main.command(name="generate", aliases=["g", "gen", "new"])
@click.argument("name")
@click.argument("entity", required=False, default=None)
def new(name: str, entity: str = None) -> None:
    current_dir = Path(__file__).resolve().parent
    stub_path = current_dir / "stubs" / "model.stub"
    model_dir = os.path.join(os.getcwd(), "src", entity or name.lower())
    mkdir(model_dir)

    with open(stub_path, "r") as stub_file:
        content = stub_file.read().replace("{{name}}", name.capitalize())
        stub_file.close()
        model_path = os.path.join(model_dir, f"{name.lower()}_model.py")
        if not os.path.exists(model_path):
            with open(model_path, "w") as file:
                file.write(content)
                file.close()
            modify_app_module(name, entity or name.lower(), model_dir)
