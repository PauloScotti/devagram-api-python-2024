from typing import Annotated, List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, Form, Query, UploadFile

from dtos.ResponseDTO import ResponseDTO
from middlewares.JWTMiddleware import verificar_token
from models.UsuarioModel import (
    UsuarioAtualizarModel,
    UsuarioCriarModel,
    UsuarioModel,
)
from services.UsuarioService import UsuarioService
from utils.IdUtil import para_object_id

router = APIRouter()
usuarioService = UsuarioService()

UsuarioLogado = Annotated[ObjectId, Depends(verificar_token)]


@router.post(
    "/",
    summary="Cadastrar usuário, com foto opcional",
    status_code=201,
    response_model=ResponseDTO[UsuarioModel],
)
async def rota_criar_usuario(
    usuario: Annotated[UsuarioCriarModel, Form()],
    file: Optional[UploadFile] = None,
):
    novo_usuario = await usuarioService.registrar_usuario(usuario, file)
    return ResponseDTO(
        mensagem="Usuário cadastrado com sucesso!", dados=novo_usuario, status=201
    )


@router.get(
    "/me",
    summary="Dados do usuário logado",
    response_model=ResponseDTO[UsuarioModel],
)
async def buscar_info_usuario_logado(usuario_logado: UsuarioLogado):
    usuario = await usuarioService.buscar_usuario(usuario_logado)
    return ResponseDTO(mensagem="Usuário encontrado.", dados=usuario, status=200)


@router.put(
    "/me",
    summary="Atualizar o usuário logado",
    response_model=ResponseDTO[UsuarioModel],
)
async def atualizar_usuario_logado(
    usuario_logado: UsuarioLogado,
    usuario_atualizar: Annotated[UsuarioAtualizarModel, Form()],
    foto: Optional[UploadFile] = None,
):
    usuario = await usuarioService.atualizar_usuario_logado(
        usuario_logado, usuario_atualizar, foto
    )
    return ResponseDTO(mensagem="Usuário atualizado.", dados=usuario, status=200)


@router.put(
    "/seguir/{usuario_id}",
    summary="Seguir ou deixar de seguir um usuário",
    response_model=ResponseDTO[str],
)
async def follow_unfollow_usuario(usuario_id: str, usuario_logado: UsuarioLogado):
    await usuarioService.follow_unfollow_usuario(
        usuario_logado, para_object_id(usuario_id, "Usuário")
    )
    return ResponseDTO(
        mensagem="Requisição realizada com sucesso.", dados="", status=200
    )


@router.get(
    "/{usuario_id}",
    summary="Dados de um usuário",
    response_model=ResponseDTO[UsuarioModel],
    dependencies=[Depends(verificar_token)],
)
async def buscar_info_usuario(usuario_id: str):
    usuario = await usuarioService.buscar_usuario(
        para_object_id(usuario_id, "Usuário")
    )
    return ResponseDTO(mensagem="Usuário encontrado.", dados=usuario, status=200)


@router.get(
    "/",
    summary="Buscar usuários por nome ou e-mail",
    response_model=ResponseDTO[List[UsuarioModel]],
    dependencies=[Depends(verificar_token)],
)
async def listar_usuarios(filtro: Annotated[str, Query(min_length=2, max_length=100)]):
    usuarios = await usuarioService.listar_usuarios(filtro)
    return ResponseDTO(
        mensagem="Usuários listados com sucesso!", dados=usuarios, status=200
    )
