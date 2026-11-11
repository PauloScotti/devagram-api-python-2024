from pydantic import BaseModel, Field


class ComentarioCriarModel(BaseModel):
    comentario: str = Field(min_length=1, max_length=1000)


class ComentarioAtualizarModel(BaseModel):
    comentario: str = Field(min_length=1, max_length=1000)
