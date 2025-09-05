from dataclasses import dataclass


@dataclass
class CreatePostDto:
    name: str


@dataclass
class UpdatePostDto(CreatePostDto):
    id: int
