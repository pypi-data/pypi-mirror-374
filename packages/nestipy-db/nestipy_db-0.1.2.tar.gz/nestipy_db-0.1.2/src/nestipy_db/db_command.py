import asyncio
import importlib
import inspect
import os
import sys
import typing
from pathlib import Path
from typing import Annotated

from edgy import Instance, monkay
from edgy.cli.cli import edgy_cli
from nestipy.commander import BaseCommand, Command
from nestipy.ioc import Inject

from .db_builder import DbConfig, DB_CONFIG
from .db_cli import db_main
from .db_service import DbService


@Command(name="db", desc="Db edgy command alias")
class DbCommand(BaseCommand):
    _config: Annotated[DbConfig, Inject(DB_CONFIG)]
    _service: Annotated[DbService, Inject()]

    def get_full_args(self):
        full_args = self.get_arg()[:]
        for k, v in self.get_opt().items():
            if isinstance(v, bool) and v:
                full_args.append(f"--{k}")
            else:
                full_args.append(f"--{k}={v}")
        return full_args

    async def _run_edgy_command_from_args(self, app):
        if not os.environ.get("EDGY_DATABASE_URL"):
            os.environ["EDGY_DATABASE_URL"] = self._config.url
        _, registry = self._service.get_connection()
        edgy_app = registry.asgi(app)
        monkay.set_instance(Instance(registry=registry, app=edgy_app))

        loop = asyncio.get_running_loop()

        def run_cli():
            full_args = self.get_full_args()
            result = edgy_cli.main(args=full_args, standalone_mode=False)
            if inspect.isawaitable(result):
                return asyncio.run(typing.cast(typing.Coroutine, result))
            return result

        await loop.run_in_executor(None, run_cli)

    async def run(self):
        args = self.get_arg()
        opts = self.get_opt()
        if len(args) > 0 and args[0] == "new":
            full_args = self.get_full_args()
            db_main.main(args=full_args, standalone_mode=False)
            self.success("Model created successfully")
        else:
            path = "main:app"
            if opts.get("app") is not None:
                path = opts.get("app")
                del opts["app"]
            module_path, app_name = path.split(":")
            module_file_path = Path(module_path).resolve()
            module_name = module_file_path.stem
            sys.path.append(str(module_file_path.parent))
            mod = importlib.import_module(module_name)
            app = getattr(mod, app_name)
            await self._run_edgy_command_from_args(app)
