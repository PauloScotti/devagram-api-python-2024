import os
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile

from middlewares.JWTMiddleware import verificar_token
from models.UsuarioModel import UsuarioCriarModel, UsuarioAtualizarModel
from repositories.UsuarioRepository import UsuarioRepository
from services.AuthService import AuthService
from services.UsuarioService import UsuarioService

router = APIRouter()
usuarioRepository = UsuarioRepository()
authService = AuthService()
usuarioService = UsuarioService()


@router.post("/", response_description="Rota para criar um novo usuário")
async def rota_criar_usuario(file: UploadFile, usuario: UsuarioCriarModel = Depends(UsuarioCriarModel)):
    try:
        caminho_foto = f'files/foto-{datetime.now().strftime("%H%M%S")}.png'

        with open(caminho_foto, 'wb+') as arquivo:
            arquivo.write(file.file.read())

        resultado = await usuarioService.registrar_usuario(usuario, caminho_foto)

        os.remove(caminho_foto)

        if not resultado['status'] == 201:
            raise HTTPException(status_code=resultado['status'], detail=resultado['mensagem'])

        return resultado
    except Exception as error:
        raise error


@router.get(
    '/me',
    response_description='Rota para buscar as informações do usuário logado',
    dependencies=[Depends(verificar_token)]
)
async def buscar_info_usuario_logado(authorization: str = Header(default='')):
    try:
        token = authorization.split(' ')[1]

        payload = authService.decodificar_token_jwt(token)

        resultado = await usuarioRepository.buscar_usuario_logado(payload["usuario_id"])

        #if not resultado['status'] == 200:
        #    raise HTTPException(status_code=resultado['status'], detail=resultado['mensagem'])

        return resultado
    except Exception as erro:
        raise erro


@router.put(
    '/me',
    response_description='Rota para buscar as informações do usuário logado',
    dependencies=[Depends(verificar_token)]
)
async def atualizar_usuario_logado(authorization: str = Header(default=''), usuario_atualizar: UsuarioAtualizarModel = Depends(UsuarioAtualizarModel)):
    try:
        token = authorization.split(' ')[1]

        payload = authService.decodificar_token_jwt(token)

        resultado = await usuarioService.atualizar_usuario_logado(payload["usuario_id"], usuario_atualizar)

        if not resultado['status'] == 200:
            raise HTTPException(status_code=resultado['status'], detail=resultado['mensagem'])

        return resultado
    except Exception as erro:
        raise erro
