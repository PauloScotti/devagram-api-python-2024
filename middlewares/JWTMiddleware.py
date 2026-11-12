from bson import ObjectId
from fastapi import Header, HTTPException

from services.AuthService import AuthService

authService = AuthService()


async def verificar_token(authorization: str = Header(default="")) -> ObjectId:
    """Dependência das rotas protegidas: devolve o id do usuário logado."""
    esquema, _, token = authorization.partition(" ")
    if esquema != "Bearer" or not token:
        raise HTTPException(
            status_code=401, detail="Necessário token para autenticação."
        )
    usuario_id = authService.decodificar_token_jwt(token)
    if not usuario_id or not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")
    return ObjectId(usuario_id)
