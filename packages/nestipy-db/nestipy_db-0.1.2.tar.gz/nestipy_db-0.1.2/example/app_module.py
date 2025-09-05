from dotenv import dotenv_values
from nestipy.common import Module

from app_controller import AppController
from app_service import AppService
from nestipy_db import DbConfig, DbModule, AdminConfig
from src.auth.auth_module import AuthModule
from src.post.post_module import PostModule
from src.user.user_module import UserModule

env = dotenv_values()


@Module(
    imports=[
        DbModule.for_root(
            DbConfig(
                url="sqlite:///db.sqlite",
                models=[],
                admin=AdminConfig(enable=True, url="/admin"),
            )
        ),
        AuthModule,
        UserModule,
        PostModule,
    ],
    controllers=[AppController],
    providers=[AppService],
)
class AppModule: ...
