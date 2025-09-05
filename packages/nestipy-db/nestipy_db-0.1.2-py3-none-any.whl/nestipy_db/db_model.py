import typing
import edgy


class BaseModel(edgy.Model):
    query: typing.ClassVar[edgy.QuerySet] = typing.cast(edgy.QuerySet, edgy.Manager())

    class Meta:
        abstract = True
        registry = False
