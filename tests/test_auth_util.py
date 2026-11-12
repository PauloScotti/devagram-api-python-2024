import bcrypt

from utils.AuthUtil import AuthUtil

auth = AuthUtil()


def test_gera_hash_argon2_diferente_a_cada_chamada():
    primeiro = auth.gerar_senha_criptografada("segredo-forte")
    segundo = auth.gerar_senha_criptografada("segredo-forte")

    assert primeiro.startswith("$argon2id$")
    assert primeiro != segundo


def test_confere_senha_certa_e_rejeita_errada():
    armazenada = auth.gerar_senha_criptografada("segredo-forte")

    assert auth.verificar_senha("segredo-forte", armazenada) == (True, False)
    assert auth.verificar_senha("errada", armazenada) == (False, False)


def test_senha_antiga_em_bcrypt_entra_e_pede_para_regravar():
    armazenada = bcrypt.hashpw(b"1234", bcrypt.gensalt(rounds=4)).decode()

    assert auth.verificar_senha("1234", armazenada) == (True, True)
    assert auth.verificar_senha("4321", armazenada) == (False, False)


def test_o_proprio_hash_nao_serve_como_senha():
    armazenada = auth.gerar_senha_criptografada("segredo-forte")

    assert auth.verificar_senha(armazenada, armazenada) == (False, False)


def test_valor_armazenado_em_formato_desconhecido_nao_estoura():
    assert auth.verificar_senha("1234", "texto-qualquer") == (False, False)
    assert auth.verificar_senha("1234", "$2b$invalido") == (False, False)
