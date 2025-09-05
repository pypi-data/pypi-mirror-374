from nestipy.common import Module

from nestipy_db import DbModule
from .post_controller import PostController
from .post_model import Post
from .post_service import PostService


@Module(
    imports=[DbModule.for_feature(Post)],
    providers=[PostService],
    controllers=[PostController],
)
class PostModule: ...
