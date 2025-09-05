from datetime import datetime
from uuid import UUID, uuid4

import edgy
from ..user.user_model import User
from nestipy_db import BaseModel, Model


@Model()
class Post(BaseModel):
    id: UUID = edgy.UUIDField(primary_key=True, default=uuid4, editable=False)
    title: str = edgy.CharField(max_length=256, default="")
    user: User = edgy.ForeignKey(User, on_delete=edgy.CASCADE, related_name="posts")
    reaction: list[User] = edgy.ManyToManyField(
        User, through_tablename=edgy.NEW_M2M_NAMING
    )
    created_at: datetime = edgy.DateTimeField(auto_now_add=True)
    updated_at: datetime = edgy.DateTimeField(auto_now=True)
