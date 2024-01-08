from pydantic import BaseModel, Field, EmailStr


class UsuarioModel(BaseModel):
    id: str = Field(...)
    nome: str = Field(...)
    email: EmailStr = Field(...)
    senha: str = Field(...)
    avatar: str = Field(...)

    class Config:
        json_schema_extra = {
            "usuario": {
                "nome": "Fulano de tal",
                "email": "fulano@gmail.com",
                "senha": "Senha@123",
                "avatar": "fulano.png"
            }
        }


class UsuarioCriarModel(BaseModel):
    nome: str = Field(...)
    email: EmailStr = Field(...)
    senha: str = Field(...)
    avatar: str = Field(...)

    class Config:
        json_schema_extra = {
            "usuario": {
                "nome": "Fulano de tal",
                "email": "fulano@gmail.com",
                "senha": "Senha@123",
                "avatar": "fulano.png"
            }
        }


class UsuarioLoginModel(BaseModel):
    email: EmailStr = Field(...)
    senha: str = Field(...)

    class Config:
        json_schema_extra = {
            "usuario": {
                "email": "fulano@gmail.com",
                "senha": "Senha@123"
            }
        }
