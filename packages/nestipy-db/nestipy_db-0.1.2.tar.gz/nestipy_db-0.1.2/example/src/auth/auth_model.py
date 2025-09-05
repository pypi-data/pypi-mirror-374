import enum
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import Json
import edgy
from nestipy_db import BaseModel, Model


class CharChoice(enum.Enum):
    a = "A"
    b = "B"


@Model()
class Auth(BaseModel):
    id: UUID = edgy.UUIDField(primary_key=True, default=uuid4, editable=False)
    token: str = edgy.CharField(unique=True, max_length=255)
    my_file: edgy.FileField = edgy.FileField()
    date: datetime = edgy.DateField()
    binary: bytes = edgy.BinaryField()
    my_image: edgy.ImageField = edgy.ImageField()
    password: str = edgy.PasswordField()
    url: str = edgy.URLField(max_length=255)
    float_field: float = edgy.FloatField()
    json_text: Json = edgy.JSONField()
    decimal: float = edgy.DecimalField(decimal_places=2, max_digits=10)
    text: str = edgy.TextField()
    big_integer: int = edgy.BigIntegerField()
    time: datetime = edgy.TimeField()
    duration: datetime = edgy.DurationField()
    ip: str = edgy.IPAddressField()
    char_choice: float = edgy.CharChoiceField(CharChoice)
    created_at: datetime = edgy.DateTimeField(auto_now_add=True)
    updated_at: datetime = edgy.DateTimeField(auto_now=True)
