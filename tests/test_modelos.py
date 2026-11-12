import pytest
from bson import ObjectId
from fastapi import HTTPException
from pydantic import ValidationError

from models.UsuarioModel import (
    UsuarioAtualizarModel,
    UsuarioCriarModel,
    UsuarioLoginModel,
    UsuarioModel,
)
from utils.ConverterUtil import ConverterUtil
from utils.IdUtil import para_object_id

converter = ConverterUtil()
USUARIO_NO_BANCO = {
    "_id": ObjectId(),
    "nome": "Ana",
    "email": "ana@exemplo.com",
    "senha": "$argon2id$hash",
    "seguidores": [ObjectId(), ObjectId()],
    "seguindo": [],
}


def test_usuario_convertido_nunca_tem_senha():
    usuario = converter.usuario_converter(USUARIO_NO_BANCO)

    assert "senha" not in usuario.model_dump()
    assert "senha" not in UsuarioModel.model_fields
    assert usuario.total_seguidores == 2
    assert all(isinstance(s, str) for s in usuario.seguidores)


def test_autor_da_postagem_tambem_sai_sem_senha():
    postagem = converter.postagem_converter(
        {
            "_id": ObjectId(),
            "usuario_id": USUARIO_NO_BANCO["_id"],
            "legenda": "Oi",
            "curtidas": [ObjectId()],
            "comentarios": [],
            "usuario": [USUARIO_NO_BANCO],
        }
    )

    assert "senha" not in postagem.model_dump_json()
    assert postagem.total_curtidas == 1


def test_cadastro_rejeita_senha_curta_e_email_invalido():
    validos = {"nome": "Ana", "email": "ana@exemplo.com", "senha": "segredo-forte"}

    UsuarioCriarModel(**validos)
    for campo in ({"senha": "1234567"}, {"email": "ana"}, {"nome": "A"}):
        with pytest.raises(ValidationError):
            UsuarioCriarModel(**{**validos, **campo})


def test_login_rejeita_operador_do_mongo_e_aceita_senha_antiga_curta():
    UsuarioLoginModel(email="ana@exemplo.com", senha="1234")
    with pytest.raises(ValidationError):
        UsuarioLoginModel(email={"$ne": None}, senha="x")
    with pytest.raises(ValidationError):
        UsuarioLoginModel(email="ana@exemplo.com", senha={"$ne": None})


def test_atualizacao_leva_so_os_campos_enviados():
    assert UsuarioAtualizarModel(nome="Ana Maria").model_dump(exclude_none=True) == {
        "nome": "Ana Maria"
    }


def test_id_malformado_vira_404():
    assert isinstance(para_object_id("65a1f0c2e4b0a1b2c3d4e5f6"), ObjectId)
    with pytest.raises(HTTPException) as erro:
        para_object_id("abc", "Postagem")
    assert erro.value.status_code == 404
