from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

SENHA_MINIMA = 8


class UsuarioModel(BaseModel):
    """Usuário como sai da API. Não tem senha, de propósito."""

    id: str
    nome: str
    email: EmailStr
    foto: str = ""
    seguidores: List[str] = []
    seguindo: List[str] = []
    total_seguidores: int = 0
    total_seguindo: int = 0
    postagens: List = []
    total_postagem: int = 0
    token: str = ""


class UsuarioCriarModel(BaseModel):
    nome: str = Field(min_length=3, max_length=50)
    email: EmailStr
    senha: str = Field(min_length=SENHA_MINIMA, max_length=128)


class UsuarioLoginModel(BaseModel):
    email: EmailStr
    # Sem tamanho mínimo: contas antigas têm senhas mais curtas.
    senha: str = Field(min_length=1, max_length=128)


class UsuarioAtualizarModel(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    senha: Optional[str] = Field(default=None, min_length=SENHA_MINIMA, max_length=128)
