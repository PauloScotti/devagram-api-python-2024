from datetime import datetime, timedelta, timezone

import jwt

from services.AuthService import AuthService

auth = AuthService()
SEGREDO = "segredo-de-teste-com-mais-de-32-bytes"


def test_assina_e_le_o_id_do_usuario():
    token = auth.gerar_token_jwt("65a1f0c2e4b0a1b2c3d4e5f6")

    assert auth.decodificar_token_jwt(token) == "65a1f0c2e4b0a1b2c3d4e5f6"


def test_token_tem_validade():
    payload = jwt.decode(
        auth.gerar_token_jwt("abc"), SEGREDO, algorithms=["HS256"]
    )

    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


def test_rejeita_token_adulterado_expirado_ou_de_outra_chave():
    expirado = jwt.encode(
        {
            "usuario_id": "abc",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=10),
        },
        SEGREDO,
        algorithm="HS256",
    )
    outra_chave = jwt.encode(
        {
            "usuario_id": "abc",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        "outra-chave-tambem-com-mais-de-32-bytes",
        algorithm="HS256",
    )

    assert auth.decodificar_token_jwt(auth.gerar_token_jwt("abc") + "x") is None
    assert auth.decodificar_token_jwt(expirado) is None
    assert auth.decodificar_token_jwt(outra_chave) is None
    assert auth.decodificar_token_jwt("nao-e-um-token") is None


def test_rejeita_token_sem_validade_ou_sem_assinatura():
    sem_validade = jwt.encode({"usuario_id": "abc"}, SEGREDO, algorithm="HS256")
    sem_assinatura = jwt.encode(
        {
            "usuario_id": "abc",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        None,
        algorithm="none",
    )

    assert auth.decodificar_token_jwt(sem_validade) is None
    assert auth.decodificar_token_jwt(sem_assinatura) is None


def test_rejeita_payload_cujo_id_nao_e_texto():
    token = jwt.encode(
        {
            "usuario_id": {"$ne": None},
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        SEGREDO,
        algorithm="HS256",
    )

    assert auth.decodificar_token_jwt(token) is None
