from nestipy.common import Injectable

from .user_dto import CreateUserDto, UpdateUserDto
from .user_model import Profile


@Injectable()
class UserService:
    async def list(self):
        users: list[Profile] = await Profile.query.select_related("user").all()
        return [u.model_dump() for u in users]

    async def create(self, data: CreateUserDto):
        return "test"

    async def update(self, id: int, data: UpdateUserDto):
        return "test"

    async def delete(self, id: int):
        return "test"
