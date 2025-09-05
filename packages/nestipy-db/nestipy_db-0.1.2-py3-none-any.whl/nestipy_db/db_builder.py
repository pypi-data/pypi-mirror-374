from dataclasses import dataclass, field
from typing import Optional, Callable

from nestipy.dynamic_module import ConfigurableModuleBuilder

from .db_model import BaseModel


@dataclass
class AdminConfig:
    enable: bool = field(default=False)
    url: str = field(default="/admin")
    title: str = field(default="Admin Dashboard")
    panel_title: str = field(default="Admin Panel")
    api_prefix: str = field(default="/api")
    email: str = field(default="test@admin.com")
    password: str = field(default="admin")
    email_field: str = field(default="email")
    password_field: str = field(default="password")
    encrypt_password: Callable[[str], str] = field(default=lambda password: password)
    model: Optional[BaseModel] = field(default=None)
    jwt_secret: str = field(default="jwt_secret")


@dataclass
class DbConfig:
    url: str
    admin: Optional[AdminConfig] = field(default=None)
    models: list[BaseModel] = field(default_factory=lambda: [])
    # options: dict = field(default_factory=lambda: {})


ConfigurableModuleClass, DB_CONFIG = (
    ConfigurableModuleBuilder[DbConfig]().set_method("for_root").build()
)
