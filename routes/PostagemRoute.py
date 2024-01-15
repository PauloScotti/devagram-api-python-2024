import os

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile
from middlewares.JWTMiddleware import verificar_token
from models.ComentarioModel import ComentarioCriarModel
from models.PostagemModel import PostagemCriarModel
from services.AuthService import AuthService
from services.UsuarioService import UsuarioService
from services.PostagemService import PostagemService

router = APIRouter()
authService = AuthService()
usuarioService = UsuarioService()
postagemService = PostagemService()


@router.post("/", response_description="Rota para criar uma nova postagem", dependencies=[Depends(verificar_token)])
async def rota_criar_postagem(authorization: str = Header(default=''), postagem: PostagemCriarModel = Depends(PostagemCriarModel)):
    try:
        token = authorization.split(' ')[1]
        payload = authService.decodificar_token_jwt(token)
        resultado_usuario = await (usuarioService.buscar_usuario(payload['usuario_id']))

        usuario_logado = resultado_usuario["dados"]

        resultado = await postagemService.cadastrar_postagem(postagem, usuario_logado["id"])

        #if not resultado['status'] == 201:
        #    raise HTTPException(status_code=resultado["status"], detail=resultado["mensagem"])

        return resultado
    except Exception as error:
        raise error


@router.get(
    '/',
    response_description='Rota para listar as postagens',
    dependencies=[Depends(verificar_token)]
)
async def listar_postagens():
    try:
        resultado = await postagemService.listar_postagens()

        if not resultado['status'] == 200:
            raise HTTPException(status_code=resultado["status"], detail=resultado["mensagem"])

        return resultado

    except Exception as erro:
        raise erro


@router.get(
    '/me',
    response_description='Rota para listar as postagens do usuário logado',
    dependencies=[Depends(verificar_token)]
)
async def buscar_info_usuario_logado(authorization: str = Header(default='')):
    try:

        return {
            "teste": "Ok"
        }

    except Exception as erro:
        raise erro


@router.put(
    '/curtir/{postagem_id}',
    response_description="Rota para curtir/descurtir uma postagem",
    dependencies=[Depends(verificar_token)]
)
async def curtir_descurtir_postagem(postagem_id: str, authorization: str = Header(default='')):
    token = authorization.split(' ')[1]
    payload = authService.decodificar_token_jwt(token)
    resultado_usuario = await (usuarioService.buscar_usuario(payload['usuario_id']))

    usuario_logado = resultado_usuario["dados"]

    resultado = await postagemService.curtir_descurtir(postagem_id, usuario_logado["id"])

    if not resultado['status'] == 200:
        raise HTTPException(status_code=resultado["status"], detail=resultado["mensagem"])

    return resultado

@router.put(
    '/comentar/{postagem_id}',
    response_description="Rota para criar um comentário em uma postagem",
    dependencies=[Depends(verificar_token)]
)
async def comentar_postagem(postagem_id: str, authorization: str = Header(default=''), comentario: ComentarioCriarModel = Depends(ComentarioCriarModel)):
    token = authorization.split(' ')[1]
    payload = authService.decodificar_token_jwt(token)
    resultado_usuario = await (usuarioService.buscar_usuario(payload['usuario_id']))

    usuario_logado = resultado_usuario["dados"]

    resultado = await postagemService.criar_comentario(postagem_id, usuario_logado["id"], comentario.comentario)

    if not resultado['status'] == 200:
        raise HTTPException(status_code=resultado["status"], detail=resultado["mensagem"])

    return resultado
