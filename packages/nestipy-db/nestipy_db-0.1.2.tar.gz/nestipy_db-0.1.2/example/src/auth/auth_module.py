from nestipy.common import Module
from nestipy_db import DbModule

from .auth_controller import AuthController
from .auth_model import Auth
from .auth_service import AuthService


@Module(
    providers=[AuthService],
    controllers=[AuthController],
    imports=[DbModule.for_feature(Auth)],
)
class AuthModule: ...
