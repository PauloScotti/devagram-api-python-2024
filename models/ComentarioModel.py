from pydantic import BaseModel, Field

from utils.DecoratorUtil import DecoratorUtil

decoratorUtil = DecoratorUtil()


class ComentarioModel(BaseModel):
    usuario_id: str = Field(...),
    comentario: str = Field(...)


@decoratorUtil.form_body
class ComentarioCriarModel(BaseModel):
    comentario: str = Field(...)


@decoratorUtil.form_body
class ComentarioAtualizarModel(BaseModel):
    comentario: str = Field(...)
