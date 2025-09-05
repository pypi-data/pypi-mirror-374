import os
import re
from pathlib import Path
from typing import Annotated

import jwt
from nestipy.common import (
    NestipyMiddleware,
    Request,
    Response,
    Injectable,
    HttpException,
    HttpStatusMessages,
)
from nestipy.core import MinimalJinjaTemplateEngine
from nestipy.ioc import Inject
from nestipy.types_ import NextFn

from .db_builder import DbConfig, DB_CONFIG


@Injectable()
class DbMiddleware(NestipyMiddleware):
    _config: Annotated[DbConfig, Inject(DB_CONFIG)]
    _template_engine = MinimalJinjaTemplateEngine(
        template_dir=os.path.join(str(Path(__file__).parent.resolve()), "views")
    )

    async def use(self, req: "Request", res: "Response", next_fn: "NextFn"):
        prefix = f"/{self._config.admin.url.strip('/')}/{self._config.admin.api_prefix.strip('/')}"
        try:
            if self._is_match(prefix, req.path) and req.path != f"{prefix}/auth":
                admin_cfg = self._config.admin
                token = (req.headers.get("authorization") or "").replace("Bearer ", "")
                try:
                    payload = jwt.decode(
                        token, self._config.admin.jwt_secret, algorithms=["HS256"]
                    )
                    assert payload[admin_cfg.email_field] is not None
                    assert payload[admin_cfg.password_field] is not None
                except jwt.exceptions.InvalidTokenError as e:
                    raise HttpException(
                        403, HttpStatusMessages.UNAUTHORIZED, details=str(e)
                    )
            return await next_fn()
        except HttpException as e:
            if e.status_code == 404:
                html = self._template_engine.render(
                    "index.html",
                    {
                        "basename": self._config.admin.url,
                        "title": self._config.admin.title,
                    },
                )
                return (
                    await res.status(200).header("content-type", "text/html").send(html)
                )
            else:
                raise e

    @classmethod
    def _is_match(cls, admin_url: str, path_url: str) -> bool:
        pattern = re.compile(f"^{admin_url}")
        mitch = pattern.match(path_url)
        return mitch is not None
