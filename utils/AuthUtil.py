import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_hasher = PasswordHasher()


class AuthUtil:
    def gerar_senha_criptografada(self, senha: str) -> str:
        return _hasher.hash(senha)

    def verificar_senha(self, senha: str, armazenada: str) -> tuple[bool, bool]:
        """Devolve (senha_confere, precisa_regravar).

        As contas antigas guardam a senha em bcrypt. Elas continuam entrando,
        e quem chama regrava com argon2 quando o segundo valor vem True.
        """
        if armazenada.startswith("$2"):
            try:
                # bcrypt só considera os primeiros 72 bytes da senha.
                valida = bcrypt.checkpw(senha.encode()[:72], armazenada.encode())
            except ValueError:
                valida = False
            return valida, valida

        try:
            _hasher.verify(armazenada, senha)
        except (VerificationError, InvalidHashError):
            return False, False
        return True, _hasher.check_needs_rehash(armazenada)
