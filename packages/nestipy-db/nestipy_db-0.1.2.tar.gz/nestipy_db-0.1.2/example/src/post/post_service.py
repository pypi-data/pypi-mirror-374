from nestipy.common import Injectable

from .post_dto import CreatePostDto, UpdatePostDto


@Injectable()
class PostService:
    async def list(self):
        return "test"

    async def create(self, data: CreatePostDto):
        return "test"

    async def update(self, id: int, data: UpdatePostDto):
        return "test"

    async def delete(self, id: int):
        return "test"
