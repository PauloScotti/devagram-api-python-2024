from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from models.PostagemModel import PostagemModel
from repositories.Database import database
from utils.ConverterUtil import ConverterUtil

postagem_collection = database.get_collection("postagem")
converterUtil = ConverterUtil()

# Junta o autor da postagem sem trazer o hash da senha dele.
COM_AUTOR = [
    {
        "$lookup": {
            "from": "usuario",
            "localField": "usuario_id",
            "foreignField": "_id",
            "as": "usuario",
        }
    },
    {"$project": {"usuario.senha": 0}},
]


class PostagemRepository:
    async def criar_postagem(self, legenda: str, usuario_id: ObjectId) -> PostagemModel:
        resultado = await postagem_collection.insert_one(
            {
                "usuario_id": usuario_id,
                "legenda": legenda,
                "curtidas": [],
                "comentarios": [],
                "data": datetime.now(),
            }
        )
        return await self.buscar_postagem(resultado.inserted_id)

    async def definir_foto(self, id: ObjectId, url: str) -> PostagemModel:
        await postagem_collection.update_one({"_id": id}, {"$set": {"foto": url}})
        return await self.buscar_postagem(id)

    async def listar_postagens(self, usuario_id: Optional[ObjectId] = None) -> List[PostagemModel]:
        etapas = [{"$match": {"usuario_id": usuario_id}}] if usuario_id else []
        cursor = postagem_collection.aggregate(
            [*etapas, {"$sort": {"data": -1}}, *COM_AUTOR]
        )
        return [converterUtil.postagem_converter(p) async for p in cursor]

    async def buscar_postagem(self, id: ObjectId) -> Optional[PostagemModel]:
        postagem = await postagem_collection.find_one({"_id": id})
        return converterUtil.postagem_converter(postagem) if postagem else None

    async def curtir(self, id: ObjectId, usuario_id: ObjectId):
        await postagem_collection.update_one(
            {"_id": id}, {"$addToSet": {"curtidas": usuario_id}}
        )

    async def descurtir(self, id: ObjectId, usuario_id: ObjectId):
        await postagem_collection.update_one(
            {"_id": id}, {"$pull": {"curtidas": usuario_id}}
        )

    async def adicionar_comentario(self, id: ObjectId, usuario_id: ObjectId, comentario: str):
        await postagem_collection.update_one(
            {"_id": id},
            {
                "$push": {
                    "comentarios": {
                        "comentario_id": ObjectId(),
                        "usuario_id": usuario_id,
                        "comentario": comentario,
                    }
                }
            },
        )

    async def atualizar_comentario(self, id: ObjectId, comentario_id: ObjectId, comentario: str):
        await postagem_collection.update_one(
            {"_id": id, "comentarios.comentario_id": comentario_id},
            {"$set": {"comentarios.$.comentario": comentario}},
        )

    async def remover_comentario(self, id: ObjectId, comentario_id: ObjectId):
        await postagem_collection.update_one(
            {"_id": id},
            {"$pull": {"comentarios": {"comentario_id": comentario_id}}},
        )

    async def deletar_postagem(self, id: ObjectId):
        await postagem_collection.delete_one({"_id": id})
