from typing import List, Optional

from pydantic import BaseModel, Field

from models.UsuarioModel import UsuarioModel


class ComentarioRespostaModel(BaseModel):
    comentario_id: str
    usuario_id: str
    comentario: str


class PostagemModel(BaseModel):
    id: str
    usuario_id: str
    foto: str = ""
    legenda: str = ""
    data: str = ""
    curtidas: List[str] = []
    comentarios: List[ComentarioRespostaModel] = []
    usuario: Optional[UsuarioModel] = None
    total_curtidas: int = 0
    total_comentarios: int = 0


class PostagemCriarModel(BaseModel):
    legenda: str = Field(min_length=1, max_length=2200)
