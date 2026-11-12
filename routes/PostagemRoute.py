from typing import Annotated, List

from bson import ObjectId
from fastapi import APIRouter, Depends, Form, UploadFile

from dtos.ResponseDTO import ResponseDTO
from middlewares.JWTMiddleware import verificar_token
from models.ComentarioModel import ComentarioAtualizarModel, ComentarioCriarModel
from models.PostagemModel import PostagemCriarModel, PostagemModel
from services.PostagemService import PostagemService
from utils.IdUtil import para_object_id

router = APIRouter()
postagemService = PostagemService()

UsuarioLogado = Annotated[ObjectId, Depends(verificar_token)]


def id_postagem(postagem_id: str) -> ObjectId:
    return para_object_id(postagem_id, "Postagem")


def id_comentario(comentario_id: str) -> ObjectId:
    return para_object_id(comentario_id, "Comentário")


@router.post(
    "/",
    summary="Criar postagem com foto",
    status_code=201,
    response_model=ResponseDTO[PostagemModel],
)
async def rota_criar_postagem(
    usuario_logado: UsuarioLogado,
    postagem: Annotated[PostagemCriarModel, Form()],
    foto: UploadFile,
):
    nova_postagem = await postagemService.cadastrar_postagem(
        postagem.legenda, foto, usuario_logado
    )
    return ResponseDTO(
        mensagem="Postagem criada com sucesso!", dados=nova_postagem, status=201
    )


@router.get(
    "/",
    summary="Listar postagens",
    response_model=ResponseDTO[List[PostagemModel]],
    dependencies=[Depends(verificar_token)],
)
async def listar_postagens():
    postagens = await postagemService.listar_postagens()
    return ResponseDTO(
        mensagem="Postagens listadas com sucesso!", dados=postagens, status=200
    )


@router.get(
    "/{usuario_id}",
    summary="Listar as postagens de um usuário",
    response_model=ResponseDTO[List[PostagemModel]],
    dependencies=[Depends(verificar_token)],
)
async def listar_postagens_usuario(usuario_id: str):
    postagens = await postagemService.listar_postagens_usuario(
        para_object_id(usuario_id, "Usuário")
    )
    return ResponseDTO(
        mensagem="Postagens do usuário listadas com sucesso!",
        dados=postagens,
        status=200,
    )


@router.put(
    "/curtir/{postagem_id}",
    summary="Curtir ou descurtir uma postagem",
    response_model=ResponseDTO[PostagemModel],
)
async def curtir_descurtir_postagem(postagem_id: str, usuario_logado: UsuarioLogado):
    postagem = await postagemService.curtir_descurtir(
        id_postagem(postagem_id), usuario_logado
    )
    return ResponseDTO(
        mensagem="Postagem curtida/descurtida com sucesso!", dados=postagem, status=200
    )


@router.put(
    "/comentar/{postagem_id}",
    summary="Comentar em uma postagem",
    response_model=ResponseDTO[PostagemModel],
)
async def comentar_postagem(
    postagem_id: str,
    usuario_logado: UsuarioLogado,
    comentario_model: Annotated[ComentarioCriarModel, Form()],
):
    postagem = await postagemService.criar_comentario(
        id_postagem(postagem_id), usuario_logado, comentario_model.comentario
    )
    return ResponseDTO(
        mensagem="Comentário criado com sucesso!", dados=postagem, status=200
    )


@router.delete(
    "/{postagem_id}",
    summary="Apagar uma postagem própria",
    response_model=ResponseDTO[str],
)
async def deletar_postagem(postagem_id: str, usuario_logado: UsuarioLogado):
    await postagemService.deletar_postagem(id_postagem(postagem_id), usuario_logado)
    return ResponseDTO(mensagem="Postagem deletada com sucesso!", dados="", status=200)


@router.delete(
    "/{postagem_id}/comentario/{comentario_id}",
    summary="Apagar um comentário",
    response_model=ResponseDTO[PostagemModel],
)
async def deletar_comentario(
    postagem_id: str, comentario_id: str, usuario_logado: UsuarioLogado
):
    postagem = await postagemService.deletar_comentario(
        id_postagem(postagem_id), usuario_logado, id_comentario(comentario_id)
    )
    return ResponseDTO(
        mensagem="Comentário deletado com sucesso!", dados=postagem, status=200
    )


@router.put(
    "/{postagem_id}/comentario/{comentario_id}",
    summary="Editar um comentário próprio",
    response_model=ResponseDTO[PostagemModel],
)
async def atualizar_comentario(
    postagem_id: str,
    comentario_id: str,
    usuario_logado: UsuarioLogado,
    comentario_model: Annotated[ComentarioAtualizarModel, Form()],
):
    postagem = await postagemService.atualizar_comentario(
        id_postagem(postagem_id),
        usuario_logado,
        id_comentario(comentario_id),
        comentario_model.comentario,
    )
    return ResponseDTO(
        mensagem="Comentário atualizado com sucesso!", dados=postagem, status=200
    )
