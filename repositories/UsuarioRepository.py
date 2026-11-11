import re
from typing import List, Optional

from bson import ObjectId

from models.UsuarioModel import UsuarioModel
from repositories.Database import database
from utils.ConverterUtil import ConverterUtil

usuario_collection = database.get_collection("usuario")
converterUtil = ConverterUtil()

LIMITE_DE_RESULTADOS = 50


class UsuarioRepository:
    async def criar_usuario(self, nome: str, email: str, senha_hash: str) -> UsuarioModel:
        resultado = await usuario_collection.insert_one(
            {
                "nome": nome,
                "email": email,
                "senha": senha_hash,
                "seguidores": [],
                "seguindo": [],
            }
        )
        return await self.buscar_usuario(resultado.inserted_id)

    async def listar_usuarios(self, filtro: str) -> List[UsuarioModel]:
        # Texto do usuário em $regex: sem escapar, vira injeção de expressão regular.
        padrao = {"$regex": re.escape(filtro), "$options": "i"}
        cursor = usuario_collection.find(
            {"$or": [{"nome": padrao}, {"email": padrao}]}
        ).limit(LIMITE_DE_RESULTADOS)
        return [converterUtil.usuario_converter(usuario) async for usuario in cursor]

    async def buscar_usuario(self, id: ObjectId) -> Optional[UsuarioModel]:
        usuario = await usuario_collection.find_one({"_id": id})
        return converterUtil.usuario_converter(usuario) if usuario else None

    async def email_ja_cadastrado(self, email: str, exceto_id: Optional[ObjectId] = None) -> bool:
        consulta = {"email": email}
        if exceto_id:
            consulta["_id"] = {"$ne": exceto_id}
        return await usuario_collection.count_documents(consulta, limit=1) > 0

    async def buscar_credenciais(self, email: str) -> Optional[dict]:
        """Único ponto que devolve o hash da senha: uso exclusivo do login."""
        usuario = await usuario_collection.find_one(
            {"email": email}, {"_id": 1, "senha": 1}
        )
        return {"id": usuario["_id"], "senha": usuario["senha"]} if usuario else None

    async def atualizar_usuario(self, id: ObjectId, dados_usuario: dict) -> Optional[UsuarioModel]:
        if dados_usuario:
            await usuario_collection.update_one({"_id": id}, {"$set": dados_usuario})
        return await self.buscar_usuario(id)

    async def seguir(self, usuario_id: ObjectId, seguido_id: ObjectId):
        # $addToSet é atômico: dois cliques simultâneos não duplicam o seguidor.
        await usuario_collection.update_one(
            {"_id": seguido_id}, {"$addToSet": {"seguidores": usuario_id}}
        )
        await usuario_collection.update_one(
            {"_id": usuario_id}, {"$addToSet": {"seguindo": seguido_id}}
        )

    async def deixar_de_seguir(self, usuario_id: ObjectId, seguido_id: ObjectId):
        await usuario_collection.update_one(
            {"_id": seguido_id}, {"$pull": {"seguidores": usuario_id}}
        )
        await usuario_collection.update_one(
            {"_id": usuario_id}, {"$pull": {"seguindo": seguido_id}}
        )
