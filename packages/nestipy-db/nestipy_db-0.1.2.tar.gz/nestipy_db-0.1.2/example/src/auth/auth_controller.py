from typing import Annotated

from nestipy.common import Controller, Get, Post, Put, Delete
from nestipy.ioc import Inject, Body, Param

from .auth_dto import CreateAuthDto, UpdateAuthDto
from .auth_service import AuthService


@Controller("auths")
class AuthController:
    auth_service: Annotated[AuthService, Inject()]

    @Get()
    async def list(self) -> str:
        return await self.auth_service.list()

    @Post()
    async def create(self, data: Annotated[CreateAuthDto, Body()]) -> str:
        return await self.auth_service.create(data)

    @Put("/{id}")
    async def update(
        self,
        auth_id: Annotated[int, Param("id")],
        data: Annotated[UpdateAuthDto, Body()],
    ) -> str:
        return await self.auth_service.update(auth_id, data)

    @Delete("/{id}")
    async def delete(self, auth_id: Annotated[int, Param("id")]) -> None:
        return await self.auth_service.delete(auth_id)
