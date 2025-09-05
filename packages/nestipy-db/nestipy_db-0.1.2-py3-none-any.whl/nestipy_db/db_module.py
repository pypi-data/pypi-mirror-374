import os
import platform
import typing
import uuid
from pathlib import Path
from typing import Annotated, Any, Type, Coroutine

import jwt
from edgy import and_, or_
from edgy.contrib.admin.utils.models import get_model_json_schema
from nestipy.common import Module, Request, Response, cors, UploadFile
from nestipy.core.adapter import HttpAdapter
from nestipy.dynamic_module import NestipyModule, MiddlewareConsumer
from nestipy.ioc import Inject
from nestipy.metadata import Reflect
from nestipy.types_ import NextFn
from orjson import orjson

from .db_builder import ConfigurableModuleClass, DB_CONFIG, DbConfig, AdminConfig
from .db_command import DbCommand
from .db_meta import DbMetadata
from .db_middleware import DbMiddleware
from .db_model import BaseModel as Model
from .db_service import DbService
from .utils.transformer import ModelTransformer


def str_to_bool(value: str) -> bool:
    value = value.lower().strip()
    if value in ("y", "yes", "t", "true", "on", "1"):
        return True
    if value in ("n", "no", "f", "false", "off", "0"):
        return False
    raise ValueError(f"Invalid boolean string: {value}")


FILTER_OPERATOR_MAP: dict[str, str] = {
    "in": "in",
    "exact": "exact",
    "like": "exact",
    "iexact": "iexact",
    "ilike": "iexact",
    "contains": "contains",
    "icontains": "icontains",
    "lt": "lt",
    "lte": "lte",
    "gt": "gt",
    "gte": "gte",
    "isnull": "isnull",
    "isempty": "isempty",
}


@Module(providers=[DbService, DbCommand])
class DbModule(ConfigurableModuleClass, NestipyModule):
    _models: list[Type[Model]] = []
    _config: Annotated[DbConfig, Inject(DB_CONFIG)]
    _service: Annotated[DbService, Inject()]
    adapter: Annotated[HttpAdapter, Inject()]

    def configure(self, consumer: MiddlewareConsumer):
        consumer.apply(cors(), DbMiddleware).for_route(self._config.admin.url)

    # ---------- Helpers ----------

    def _get_model(
        self, req: Request, res: Response
    ) -> Coroutine[Any, Any, Response] | Model:
        model_name = str(req.path_params.get("model", "")).capitalize()
        _, registry = self._service.get_connection()
        model = registry.get_model(model_name)
        if not model:
            return res.status(404).json({"error": "Model not found"})
        return typing.cast(Model, model)

    def _get_filters(
        self, req: Request, res: Response
    ) -> tuple[Model, dict[str, Any], dict[str, Any]]:
        model = self._get_model(req, res)
        schema = self._get_model_schema(model)
        and_filters: dict[str, Any] = {}
        or_filters: dict[str, Any] = {}
        filters = orjson.loads(req.query_params.get("filters", "[]"))

        for f in filters:
            field, op, value = f["field"], f["operator"], f["value"]
            if op == "__search__":
                for fi in str(field).split(","):
                    result = next(
                        (x for x in schema["fields"] if x["name"] == fi), None
                    )
                    key = f"{fi}__contains"
                    or_filters[key] = (
                        self._to_uuid_if_valid(value)
                        if result and result["type"] == "uuid"
                        else value
                    )
                continue

            result = next((x for x in schema["fields"] if x["name"] == field), None)
            lookup = FILTER_OPERATOR_MAP.get(op, "")
            key = f"{field}__{lookup}" if lookup else field
            and_filters[key] = (
                self._to_uuid_if_valid(value)
                if result and result["type"] == "uuid"
                else value
            )

        return model, and_filters, or_filters

    @classmethod
    def _get_model_schema(cls, model: Model, phase: str = "create") -> dict[str, Any]:
        schema = get_model_json_schema(
            typing.cast(Type[Model], model),
            mode="validation",
            include_callable_defaults=True,
            phase=phase,
        )
        return ModelTransformer(schema).transform()

    @classmethod
    def _cast_form_value(cls, value: Any) -> Any:
        """
        Normalize incoming form values:
        - Try UUID
        - Try boolean
        - Try int/float
        - Try JSON
        - Leave UploadFile untouched
        - Fallback: string
        """
        if isinstance(value, UploadFile):
            return value

        # Try UUID
        val = cls._to_uuid_if_valid(value)
        if isinstance(val, uuid.UUID):
            return val

        if isinstance(value, str):
            # Boolean
            if value.lower() in ("true", "false"):
                return bool(str_to_bool(value))

            # Integer
            if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
                return int(value)

            # Float
            try:
                return float(value)
            except ValueError:
                pass

            # JSON
            try:
                return orjson.loads(value)
            except (ValueError, TypeError):
                pass

        # Default: leave as-is
        return value

    @staticmethod
    def _to_uuid_if_valid(value: Any) -> Any:
        if isinstance(value, str):
            try:
                return uuid.UUID(value)
            except ValueError:
                pass
        return value

    @staticmethod
    def _auth_success_response(
        res: Response, payload: dict[str, Any], config: AdminConfig
    ):
        return res.status(201).json(
            {
                "token": jwt.encode(payload, config.jwt_secret, algorithm="HS256"),
                "user": payload,
                "python_version": platform.python_version(),
                "system_version": f"{platform.version()}",
                "env": os.environ.get("APP_ENV", "development"),
                "title": config.title,
                "panel_title": config.panel_title,
            }
        )

    # ---------- Lifecycle ----------
    async def on_startup(self):
        models: list[Type[Model]] = Reflect.get_metadata(
            self.__class__, DbMetadata.Models, []
        )
        self._setup_model(list(set((self._config.models or []) + models)))
        db, _ = self._service.get_connection()
        await db.connect()

        if not self._config.admin:
            return

        current_dir = str(Path(__file__).parent.resolve())
        self.adapter.static(
            f"/{self._config.admin.url.strip('/')}/static",
            os.path.join(current_dir, "static"),
        )

        # ---------- Handlers ----------
        async def admin_auth(req: Request, res: Response, _next: NextFn):
            body = await req.json()
            admin_cfg = self._config.admin
            payload = {
                admin_cfg.email_field: body[admin_cfg.email_field],
                admin_cfg.password_field: admin_cfg.encrypt_password(
                    body[admin_cfg.password_field]
                ),
            }
            if admin_cfg.model:
                user = await admin_cfg.model.query.filter(**payload).limit(1)
                if user:
                    return await self._auth_success_response(res, payload, admin_cfg)
            elif (
                admin_cfg.email == payload[admin_cfg.email_field]
                and admin_cfg.password == payload[admin_cfg.password_field]
            ):
                return await self._auth_success_response(res, payload, admin_cfg)

            return await res.status(401).json({"error": "Not authorized"})

        async def admin_config(_req: Request, res: Response, _next: NextFn):
            return await res.json(
                {
                    "python_version": platform.python_version(),
                    "system_version": f"{platform.version()}",
                    "env": os.environ.get("APP_ENV", "development"),
                    "title": self._config.admin.title,
                    "panel_title": self._config.admin.panel_title,
                }
            )

        async def get_admin_dashboard_stats(req: Request, res: Response, _next: NextFn):
            stats = {m.__name__: await m.query.count() for m in set(models)}
            return await res.json(stats)

        async def get_admin_models(req: Request, res: Response, _next: NextFn):
            phase = req.query_params.get("phase", "view")
            form_models = {
                m.__name__: self._get_model_schema(typing.cast(Model, m), phase)
                for m in set(models)
            }
            return await res.json(list(form_models.values()))

        async def get_admin_model_view(req: Request, res: Response, _next: NextFn):
            model, and_filters, or_filters = self._get_filters(req, res)
            page = int(req.query_params.get("page", 1))
            limit = int(req.query_params.get("limit", 10))
            query = (
                typing.cast(Model, model).query.offset((page - 1) * limit).limit(limit)
            )
            if and_filters:
                query = query.filter(and_.from_kwargs(**and_filters))
            if or_filters:
                query = query.filter(or_.from_kwargs(**or_filters))
            data = await query
            return await res.json({"data": [d.model_dump() for d in data]})

        async def create_admin_model_post(req: Request, res: Response, _next: NextFn):
            model = self._get_model(req, res)
            body = await req.form() or await req.json()
            model_data = await typing.cast(Model, model).query.create(
                **{k: self._cast_form_value(v) for k, v in body.items()}
            )
            return await res.json({"data": model_data.model_dump()})

        async def update_admin_model_post(req: Request, res: Response, _next: NextFn):
            model = self._get_model(req, res)
            pk, pk_name = (
                str(req.path_params.get("id", "")),
                str(req.path_params.get("pk", "")),
            )
            body = await req.form() or await req.json()
            pk_val = self._to_uuid_if_valid(pk)
            try:
                pk_val = int(pk)
            except ValueError:
                pass
            model_data = (
                await typing.cast(Model, model)
                .query.filter(**{pk_name: pk_val})
                .update(**{k: self._cast_form_value(v) for k, v in body.items()})
            )
            return await res.json({"data": model_data})

        async def delete_admin_model_post(req: Request, res: Response, _next: NextFn):
            model = self._get_model(req, res)
            pk, pk_name = (
                str(req.path_params.get("id", "")),
                str(req.path_params.get("pk", "")),
            )
            pk_val = self._to_uuid_if_valid(pk)
            try:
                pk_val = int(pk)
            except ValueError:
                pass
            deleted = (
                await typing.cast(Model, model)
                .query.filter(**{pk_name: pk_val})
                .delete()
            )
            return await res.json({"data": deleted})

        # ---------- Routes ----------
        prefix = f"/{self._config.admin.url.strip('/')}/{self._config.admin.api_prefix.strip('/')}"
        model_path = f"{prefix}/models/{{model}}"

        routes = [
            (self.adapter.post, f"{prefix}/auth", admin_auth),
            (self.adapter.get, f"{prefix}/config", admin_config),
            (self.adapter.get, f"{prefix}/stats", get_admin_dashboard_stats),
            (self.adapter.get, f"{prefix}/models", get_admin_models),
            (self.adapter.get, model_path, get_admin_model_view),
            (self.adapter.post, model_path, create_admin_model_post),
            (
                self.adapter.post,
                f"{model_path}/{{id}}/edit/{{pk}}",
                update_admin_model_post,
            ),
            (
                self.adapter.post,
                f"{model_path}/{{id}}/delete/{{pk}}",
                delete_admin_model_post,
            ),
            # (self.adapter.get, self.adapter.create_wichard(f"/{self._config.admin.url.strip('/')}"), render_template),
        ]
        for method, path, handler in routes:
            method(path, handler, {})

    async def on_shutdown(self):
        db, _ = self._service.get_connection()
        await db.disconnect()

    @classmethod
    def for_feature(cls, *models: Type[Model]) -> Type["DbModule"]:
        for m in models:
            if (
                Reflect.get_metadata(m, DbMetadata.ModelMeta, False)
                and m not in cls._models
            ):
                if m.__name__ not in [c.__name__ for c in cls._models]:
                    cls._models.append(m)
                Reflect.set_metadata(cls, DbMetadata.Models, cls._models)
        return cls

    def _setup_model(self, models: list[Type[Model]]) -> None:
        db, registry = self._service.get_connection()
        for model in models:
            model.add_to_registry(registry, on_conflict="replace", database=db)
