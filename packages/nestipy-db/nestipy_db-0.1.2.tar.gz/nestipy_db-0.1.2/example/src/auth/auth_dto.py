from dataclasses import dataclass


@dataclass
class CreateAuthDto:
    name: str


@dataclass
class UpdateAuthDto(CreateAuthDto):
    id: int
