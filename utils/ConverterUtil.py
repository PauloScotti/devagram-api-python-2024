from models.PostagemModel import PostagemModel
from models.UsuarioModel import UsuarioModel


class ConverterUtil:
    # A senha nunca entra aqui: o hash só sai do banco para o login
    # (UsuarioRepository.buscar_credenciais).
    def usuario_converter(self, usuario) -> UsuarioModel:
        seguidores = [str(p) for p in usuario.get("seguidores", [])]
        seguindo = [str(p) for p in usuario.get("seguindo", [])]
        return UsuarioModel(
            id=str(usuario["_id"]),
            nome=usuario["nome"],
            email=usuario["email"],
            foto=usuario.get("foto") or "",
            seguidores=seguidores,
            seguindo=seguindo,
            total_seguidores=len(seguidores),
            total_seguindo=len(seguindo),
        )

    def postagem_converter(self, postagem) -> PostagemModel:
        curtidas = [str(p) for p in postagem.get("curtidas", [])]
        comentarios = [
            {
                "comentario": c["comentario"],
                "comentario_id": str(c["comentario_id"]),
                "usuario_id": str(c["usuario_id"]),
            }
            for c in postagem.get("comentarios", [])
        ]
        autores = postagem.get("usuario") or []
        return PostagemModel(
            id=str(postagem["_id"]),
            usuario_id=str(postagem["usuario_id"]),
            foto=postagem.get("foto") or "",
            legenda=postagem.get("legenda", ""),
            data=str(postagem.get("data", "")),
            curtidas=curtidas,
            comentarios=comentarios,
            usuario=self.usuario_converter(autores[0]) if autores else None,
            total_curtidas=len(curtidas),
            total_comentarios=len(comentarios),
        )
