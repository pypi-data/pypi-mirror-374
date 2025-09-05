import typing
from enum import Enum
from uuid import UUID, uuid4

import edgy

from nestipy_db import BaseModel, Model

if typing.TYPE_CHECKING:
    from ..post.post_model import Post


class Status(Enum):
    Active: str = "Active"
    Disabled: str = "Disabled"


@Model()
class User(BaseModel):
    id: UUID = edgy.UUIDField(primary_key=True, default=uuid4, editable=False)
    is_active: bool = edgy.BooleanField(default=True)
    first_name: str = edgy.CharField(max_length=50, null=True)
    last_name: str = edgy.CharField(max_length=50, null=True)
    email: str = edgy.EmailField(max_lengh=100)
    password: str = edgy.CharField(max_length=100, null=True)
    status: str = edgy.ChoiceField(choices=Status)
    react_posts: list["Post"] = edgy.ManyToManyField(
        "Post", through_tablename=edgy.NEW_M2M_NAMING
    )
    parent: typing.Optional["User"] = edgy.ForeignKey(
        "User", null=True, related_name="children"
    )


@Model()
class Profile(BaseModel):
    user: User = edgy.ForeignKey(User, on_delete=edgy.CASCADE)
