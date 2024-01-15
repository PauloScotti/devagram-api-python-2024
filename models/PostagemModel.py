from typing import List

from fastapi import UploadFile
from pydantic import BaseModel, Field

from models.UsuarioModel import UsuarioModel
from utils.DecoratorUtil import DecoratorUtil

decoratorUtil = DecoratorUtil()


class PostagemModel(BaseModel):
    id: str = Field(...),
    usuario: UsuarioModel = Field(...),
    foto: str = Field(...),
    legenda: str = Field(...),
    data: str = Field(...),
    curtidas: int = Field(...),
    comentarios: List = Field(...)

    class Config:
        json_schema_extra = {
            "postagem": {
                "id": "string",
                "usuario": "UsuarioModel",
                "foto": "string",
                "legenda": "string",
                "data": "date",
                "curtidas": "string",
                "comentarios": "List[comentarios]",
            }
        }


@decoratorUtil.form_body
class PostagemCriarModel(BaseModel):
    foto: UploadFile = Field(...),
    legenda: str = Field(...),

    class Config:
        json_schema_extra = {
            "postagem": {
                "foto": "string",
                "legenda": "string",
            }
        }
