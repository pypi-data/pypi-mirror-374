from nestipy.common import Injectable

from .auth_dto import CreateAuthDto, UpdateAuthDto


@Injectable()
class AuthService:
    async def list(self):
        return "test"

    async def create(self, data: CreateAuthDto):
        return "test"

    async def update(self, id: int, data: UpdateAuthDto):
        return "test"

    async def delete(self, id: int):
        return "test"
