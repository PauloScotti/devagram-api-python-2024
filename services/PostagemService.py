from typing import List

from bson import ObjectId
from fastapi import HTTPException, UploadFile

from models.PostagemModel import PostagemModel
from providers.AWSProvider import AWSProvider
from repositories.PostagemRepository import PostagemRepository
from utils.UploadUtil import ler_imagem

awsProvider = AWSProvider()
postagemRepository = PostagemRepository()


class PostagemService:
    async def _buscar(self, postagem_id: ObjectId) -> PostagemModel:
        postagem = await postagemRepository.buscar_postagem(postagem_id)
        if not postagem:
            raise HTTPException(status_code=404, detail="Postagem não encontrada.")
        return postagem

    def _comentario(self, postagem: PostagemModel, comentario_id: ObjectId):
        for comentario in postagem.comentarios:
            if comentario.comentario_id == str(comentario_id):
                return comentario
        raise HTTPException(status_code=404, detail="Comentário não encontrado.")

    async def cadastrar_postagem(self, legenda: str, foto: UploadFile, usuario_id: ObjectId) -> PostagemModel:
        # Valida a imagem antes de gravar: postagem sem foto não deve existir.
        conteudo, tipo, extensao = await ler_imagem(foto)
        postagem = await postagemRepository.criar_postagem(legenda, usuario_id)
        url_foto = awsProvider.upload_imagem(
            f"fotos-postagem/{postagem.id}.{extensao}", conteudo, tipo
        )
        if not url_foto:
            await postagemRepository.deletar_postagem(ObjectId(postagem.id))
            raise HTTPException(
                status_code=502, detail="Não foi possível salvar a foto da postagem."
            )
        return await postagemRepository.definir_foto(ObjectId(postagem.id), url_foto)

    async def listar_postagens(self) -> List[PostagemModel]:
        return await postagemRepository.listar_postagens()

    async def listar_postagens_usuario(self, usuario_id: ObjectId) -> List[PostagemModel]:
        return await postagemRepository.listar_postagens(usuario_id)

    async def curtir_descurtir(self, postagem_id: ObjectId, usuario_id: ObjectId) -> PostagemModel:
        postagem = await self._buscar(postagem_id)
        if str(usuario_id) in postagem.curtidas:
            await postagemRepository.descurtir(postagem_id, usuario_id)
        else:
            await postagemRepository.curtir(postagem_id, usuario_id)
        return await self._buscar(postagem_id)

    async def criar_comentario(self, postagem_id: ObjectId, usuario_id: ObjectId, comentario: str) -> PostagemModel:
        await self._buscar(postagem_id)
        await postagemRepository.adicionar_comentario(postagem_id, usuario_id, comentario)
        return await self._buscar(postagem_id)

    async def deletar_comentario(self, postagem_id: ObjectId, usuario_id: ObjectId, comentario_id: ObjectId) -> PostagemModel:
        postagem = await self._buscar(postagem_id)
        comentario = self._comentario(postagem, comentario_id)
        # Pode apagar quem escreveu o comentário ou o dono da postagem.
        if str(usuario_id) not in (comentario.usuario_id, postagem.usuario_id):
            raise HTTPException(
                status_code=403, detail="Você não pode apagar este comentário."
            )
        await postagemRepository.remover_comentario(postagem_id, comentario_id)
        return await self._buscar(postagem_id)

    async def atualizar_comentario(
        self, postagem_id: ObjectId, usuario_id: ObjectId, comentario_id: ObjectId, texto: str
    ) -> PostagemModel:
        postagem = await self._buscar(postagem_id)
        comentario = self._comentario(postagem, comentario_id)
        if comentario.usuario_id != str(usuario_id):
            raise HTTPException(
                status_code=403, detail="Você não pode editar este comentário."
            )
        await postagemRepository.atualizar_comentario(postagem_id, comentario_id, texto)
        return await self._buscar(postagem_id)

    async def deletar_postagem(self, postagem_id: ObjectId, usuario_id: ObjectId):
        postagem = await self._buscar(postagem_id)
        if postagem.usuario_id != str(usuario_id):
            raise HTTPException(
                status_code=403, detail="Você não pode apagar esta postagem."
            )
        await postagemRepository.deletar_postagem(postagem_id)
