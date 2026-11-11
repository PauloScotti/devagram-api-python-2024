from fastapi import APIRouter

from dtos.ResponseDTO import ResponseDTO
from models.UsuarioModel import UsuarioLoginModel, UsuarioModel
from services.AuthService import AuthService

router = APIRouter()
authService = AuthService()


@router.post(
    "/login",
    summary="Entrar e receber o token de acesso",
    response_model=ResponseDTO[UsuarioModel],
)
async def login(usuario: UsuarioLoginModel):
    usuario_logado = await authService.login_service(usuario)
    return ResponseDTO(
        mensagem="Login realizado com sucesso!", dados=usuario_logado, status=200
    )
