from typing import Annotated

from nestipy.common import Controller, Get, Post, Put, Delete
from nestipy.ioc import Inject, Body, Param

from .post_dto import CreatePostDto, UpdatePostDto
from .post_service import PostService


@Controller("posts")
class PostController:
    post_service: Annotated[PostService, Inject()]

    @Get()
    async def list(self) -> str:
        return await self.post_service.list()

    @Post()
    async def create(self, data: Annotated[CreatePostDto, Body()]) -> str:
        return await self.post_service.create(data)

    @Put("/{id}")
    async def update(
        self,
        post_id: Annotated[int, Param("id")],
        data: Annotated[UpdatePostDto, Body()],
    ) -> str:
        return await self.post_service.update(post_id, data)

    @Delete("/{id}")
    async def delete(self, post_id: Annotated[int, Param("id")]) -> None:
        return await self.post_service.delete(post_id)
