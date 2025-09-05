from nestipy.common import Module

from nestipy_db import DbModule
from .user_controller import UserController
from .user_model import Profile, User
from .user_service import UserService


@Module(
    imports=[DbModule.for_feature(User, Profile)],
    providers=[UserService],
    controllers=[UserController],
)
class UserModule: ...
