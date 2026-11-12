from typing import List, Optional

from bson import ObjectId
from fastapi import HTTPException, UploadFile

from models.UsuarioModel import (
    UsuarioAtualizarModel,
    UsuarioCriarModel,
    UsuarioModel,
)
from providers.AWSProvider import AWSProvider
from repositories.PostagemRepository import PostagemRepository
from repositories.UsuarioRepository import UsuarioRepository
from utils.AuthUtil import AuthUtil
from utils.UploadUtil import ler_imagem

awsProvider = AWSProvider()
usuarioRepository = UsuarioRepository()
postagemRepository = PostagemRepository()
authUtil = AuthUtil()


class UsuarioService:
    async def _enviar_foto(self, usuario_id, foto: Optional[UploadFile]) -> Optional[str]:
        if foto is None:
            return None
        conteudo, tipo, extensao = await ler_imagem(foto)
        return awsProvider.upload_imagem(
            f"fotos-perfil/{usuario_id}.{extensao}", conteudo, tipo
        )

    async def registrar_usuario(self, usuario: UsuarioCriarModel, foto: Optional[UploadFile]) -> UsuarioModel:
        if await usuarioRepository.email_ja_cadastrado(usuario.email):
            raise HTTPException(
                status_code=400,
                detail=f"E-mail {usuario.email} já cadastrado no sistema.",
            )

        novo_usuario = await usuarioRepository.criar_usuario(
            usuario.nome,
            usuario.email,
            authUtil.gerar_senha_criptografada(usuario.senha),
        )
        url_foto = await self._enviar_foto(novo_usuario.id, foto)
        if url_foto:
            novo_usuario = await usuarioRepository.atualizar_usuario(
                ObjectId(novo_usuario.id), {"foto": url_foto}
            )
        return novo_usuario

    async def buscar_usuario(self, id: ObjectId) -> UsuarioModel:
        usuario = await usuarioRepository.buscar_usuario(id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        usuario.postagens = await postagemRepository.listar_postagens(id)
        usuario.total_postagem = len(usuario.postagens)
        return usuario

    async def listar_usuarios(self, filtro: str) -> List[UsuarioModel]:
        return await usuarioRepository.listar_usuarios(filtro)

    async def atualizar_usuario_logado(
        self, id: ObjectId, dados: UsuarioAtualizarModel, foto: Optional[UploadFile]
    ) -> UsuarioModel:
        alteracoes = dados.model_dump(exclude_none=True)
        if "email" in alteracoes and await usuarioRepository.email_ja_cadastrado(
            alteracoes["email"], exceto_id=id
        ):
            raise HTTPException(
                status_code=400,
                detail=f"E-mail {alteracoes['email']} já cadastrado no sistema.",
            )
        if "senha" in alteracoes:
            alteracoes["senha"] = authUtil.gerar_senha_criptografada(alteracoes["senha"])

        url_foto = await self._enviar_foto(id, foto)
        if url_foto:
            alteracoes["foto"] = url_foto

        usuario = await usuarioRepository.atualizar_usuario(id, alteracoes)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        return usuario

    async def follow_unfollow_usuario(self, usuario_logado_id: ObjectId, usuario_seguido_id: ObjectId):
        if usuario_logado_id == usuario_seguido_id:
            raise HTTPException(
                status_code=400, detail="Você não pode seguir a si mesmo."
            )
        seguido = await usuarioRepository.buscar_usuario(usuario_seguido_id)
        if not seguido:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        if str(usuario_logado_id) in seguido.seguidores:
            await usuarioRepository.deixar_de_seguir(usuario_logado_id, usuario_seguido_id)
        else:
            await usuarioRepository.seguir(usuario_logado_id, usuario_seguido_id)
