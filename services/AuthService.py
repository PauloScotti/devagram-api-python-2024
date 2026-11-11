from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from decouple import config
from fastapi import HTTPException

from models.UsuarioModel import UsuarioLoginModel, UsuarioModel
from repositories.UsuarioRepository import UsuarioRepository
from utils.AuthUtil import AuthUtil

ALGORITMO = "HS256"
VALIDADE = timedelta(days=7)

usuarioRepository = UsuarioRepository()
authUtil = AuthUtil()


class AuthService:
    def gerar_token_jwt(self, usuario_id: str) -> str:
        payload = {
            "usuario_id": usuario_id,
            "exp": datetime.now(timezone.utc) + VALIDADE,
        }
        return jwt.encode(payload, config("JWT_SECRET"), algorithm=ALGORITMO)

    def decodificar_token_jwt(self, token: str) -> Optional[str]:
        """Devolve o id do usuário, ou None se o token for inválido ou expirado."""
        try:
            payload = jwt.decode(
                token,
                config("JWT_SECRET"),
                algorithms=[ALGORITMO],
                options={"require": ["exp", "usuario_id"]},
            )
        except jwt.PyJWTError:
            return None
        usuario_id = payload["usuario_id"]
        return usuario_id if isinstance(usuario_id, str) else None

    async def login_service(self, usuario: UsuarioLoginModel) -> UsuarioModel:
        # Mesma resposta para e-mail inexistente e senha errada: não revela
        # quais e-mails têm conta.
        credenciais = await usuarioRepository.buscar_credenciais(usuario.email)
        valida, precisa_regravar = (
            authUtil.verificar_senha(usuario.senha, credenciais["senha"])
            if credenciais
            else (False, False)
        )
        if not valida:
            raise HTTPException(status_code=401, detail="E-mail ou Senha incorretos.")

        if precisa_regravar:
            await usuarioRepository.atualizar_usuario(
                credenciais["id"],
                {"senha": authUtil.gerar_senha_criptografada(usuario.senha)},
            )

        usuario_encontrado = await usuarioRepository.buscar_usuario(credenciais["id"])
        usuario_encontrado.token = self.gerar_token_jwt(usuario_encontrado.id)
        return usuario_encontrado
