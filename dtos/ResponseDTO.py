from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseDTO(BaseModel, Generic[T]):
    mensagem: str
    dados: T
    status: int
