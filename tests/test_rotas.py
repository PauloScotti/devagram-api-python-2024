from bson import ObjectId
from fastapi.testclient import TestClient

import Main
from services import PostagemService as postagem_service
from services.AuthService import AuthService
from utils.ConverterUtil import ConverterUtil

cliente = TestClient(Main.app)
converter = ConverterUtil()

EU = ObjectId()
OUTRO = ObjectId()
ID_POSTAGEM = ObjectId()
ID_COMENTARIO = ObjectId()
cabecalho = {"Authorization": f"Bearer {AuthService().gerar_token_jwt(str(EU))}"}


def postagem_de(dono, autor_do_comentario):
    return converter.postagem_converter(
        {
            "_id": ID_POSTAGEM,
            "usuario_id": dono,
            "legenda": "Oi",
            "curtidas": [],
            "comentarios": [
                {
                    "comentario_id": ID_COMENTARIO,
                    "usuario_id": autor_do_comentario,
                    "comentario": "Bela foto",
                }
            ],
        }
    )


class RepositorioFalso:
    """Guarda a postagem em memória e registra o que foi alterado."""

    def __init__(self, postagem):
        self.postagem = postagem
        self.chamadas = []

    async def buscar_postagem(self, id):
        return self.postagem

    def __getattr__(self, nome):
        async def registrar(*args):
            self.chamadas.append(nome)

        return registrar


def com_postagem(monkeypatch, postagem):
    repositorio = RepositorioFalso(postagem)
    monkeypatch.setattr(postagem_service, "postagemRepository", repositorio)
    return repositorio


def test_rotas_protegidas_exigem_token():
    rotas = [
        ("get", "/api/usuario/me"),
        ("get", "/api/usuario/?filtro=ana"),
        ("get", "/api/postagem/"),
        ("put", f"/api/postagem/curtir/{ID_POSTAGEM}"),
        ("delete", f"/api/postagem/{ID_POSTAGEM}"),
    ]
    for metodo, rota in rotas:
        assert getattr(cliente, metodo)(rota).status_code == 401
        resposta = getattr(cliente, metodo)(
            rota, headers={"Authorization": "Bearer invalido"}
        )
        assert resposta.status_code == 401


def test_busca_exige_ao_menos_dois_caracteres():
    resposta = cliente.get("/api/usuario/?filtro=a", headers=cabecalho)

    assert resposta.status_code == 422


def test_so_o_dono_apaga_a_postagem(monkeypatch):
    repositorio = com_postagem(monkeypatch, postagem_de(OUTRO, OUTRO))
    resposta = cliente.delete(f"/api/postagem/{ID_POSTAGEM}", headers=cabecalho)
    assert resposta.status_code == 403
    assert repositorio.chamadas == []

    repositorio = com_postagem(monkeypatch, postagem_de(EU, OUTRO))
    resposta = cliente.delete(f"/api/postagem/{ID_POSTAGEM}", headers=cabecalho)
    assert resposta.status_code == 200
    assert repositorio.chamadas == ["deletar_postagem"]


def test_so_o_autor_edita_o_comentario(monkeypatch):
    rota = f"/api/postagem/{ID_POSTAGEM}/comentario/{ID_COMENTARIO}"

    # Nem o dono da postagem edita o comentário de outra pessoa.
    repositorio = com_postagem(monkeypatch, postagem_de(EU, OUTRO))
    resposta = cliente.put(rota, headers=cabecalho, data={"comentario": "x"})
    assert resposta.status_code == 403
    assert repositorio.chamadas == []

    repositorio = com_postagem(monkeypatch, postagem_de(OUTRO, EU))
    resposta = cliente.put(rota, headers=cabecalho, data={"comentario": "x"})
    assert resposta.status_code == 200
    assert repositorio.chamadas == ["atualizar_comentario"]


def test_autor_ou_dono_da_postagem_apagam_o_comentario(monkeypatch):
    rota = f"/api/postagem/{ID_POSTAGEM}/comentario/{ID_COMENTARIO}"

    com_postagem(monkeypatch, postagem_de(OUTRO, OUTRO))
    assert cliente.delete(rota, headers=cabecalho).status_code == 403

    for dono, autor in ((EU, OUTRO), (OUTRO, EU)):
        repositorio = com_postagem(monkeypatch, postagem_de(dono, autor))
        assert cliente.delete(rota, headers=cabecalho).status_code == 200
        assert repositorio.chamadas == ["remover_comentario"]


def test_postagem_ou_comentario_inexistente_respondem_404(monkeypatch):
    com_postagem(monkeypatch, None)
    resposta = cliente.delete(f"/api/postagem/{ID_POSTAGEM}", headers=cabecalho)
    assert resposta.status_code == 404

    com_postagem(monkeypatch, postagem_de(EU, EU))
    resposta = cliente.delete(
        f"/api/postagem/{ID_POSTAGEM}/comentario/{ObjectId()}", headers=cabecalho
    )
    assert resposta.status_code == 404
    assert cliente.delete("/api/postagem/abc", headers=cabecalho).status_code == 404


def test_documentacao_disponivel_e_sem_senha_nas_respostas():
    schemas = cliente.get("/openapi.json").json()["components"]["schemas"]

    assert "senha" not in schemas["UsuarioModel"]["properties"]
    assert cliente.get("/reference").status_code == 200
    assert cliente.get("/docs").status_code == 200
