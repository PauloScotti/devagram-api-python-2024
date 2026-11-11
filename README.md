# Devagram — API (Python)

API de uma rede social de fotos, no estilo Instagram: usuários se cadastram, publicam fotos, seguem outros usuários, curtem e comentam.

Construída com FastAPI e MongoDB. Nasceu como projeto da formação Devaria e foi revisada para servir de referência: senhas com argon2, validação de entrada com pydantic, nenhuma resposta com a senha e documentação OpenAPI navegável.

## Stack

| Camada       | Tecnologia                                          |
| ------------ | --------------------------------------------------- |
| Runtime      | Python 3.12+, FastAPI, Uvicorn                      |
| Banco        | MongoDB com Motor (driver assíncrono)               |
| Autenticação | JWT (HS256, validade de 7 dias), senhas em argon2id |
| Validação    | pydantic 2                                          |
| Documentação | OpenAPI gerado pelo FastAPI: Swagger UI e Scalar    |
| Imagens      | Amazon S3                                           |
| Testes       | pytest                                              |

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # preencha os valores
python Server.py
```

A API sobe em `http://localhost:5000/api`.

| Endereço        | O que é                        |
| --------------- | ------------------------------ |
| `/reference`    | Referência interativa (Scalar) |
| `/docs`         | Swagger UI                     |
| `/openapi.json` | Documento OpenAPI              |

### Variáveis de ambiente

| Variável         | Obrigatória | Para quê                                                                  |
| ---------------- | ----------- | ------------------------------------------------------------------------- |
| `MONGODB_URL`    | sim         | String de conexão do MongoDB                                              |
| `JWT_SECRET`     | sim         | Segredo que assina os tokens                                              |
| `AWS_ACCESS_KEY` | para upload | Chave de acesso de um usuário IAM com permissão de escrita no bucket      |
| `AWS_SECRET_KEY` | para upload | Chave secreta do mesmo usuário                                            |
| `AWS_BUCKET`     | não         | Bucket das fotos (padrão: `devagram-python-ps`)                           |
| `CORS_ORIGENS`   | não         | Origens aceitas, separadas por vírgula. Sem ela, qualquer origem é aceita |
| `PORT`           | não         | Porta do servidor (padrão: 5000)                                          |
| `RELOAD`         | não         | `true` para recarregar ao salvar, em desenvolvimento                      |

## Rotas

| Rota                                              | Método      | O que faz                                    |
| ------------------------------------------------- | ----------- | -------------------------------------------- |
| `/api/auth/login`                                 | POST        | Entrar e receber o token (pública)           |
| `/api/usuario/`                                   | POST        | Criar conta, com foto opcional (pública)     |
| `/api/usuario/me`                                 | GET, PUT    | Ver e atualizar o próprio cadastro           |
| `/api/usuario/?filtro=`                           | GET         | Buscar usuários por nome ou e-mail           |
| `/api/usuario/{id}`                               | GET         | Ver um usuário e as postagens dele           |
| `/api/usuario/seguir/{id}`                        | PUT         | Seguir ou deixar de seguir                   |
| `/api/postagem/`                                  | GET, POST   | Listar postagens e publicar uma foto         |
| `/api/postagem/{usuario_id}`                      | GET         | Postagens de um usuário                      |
| `/api/postagem/curtir/{id}`                       | PUT         | Curtir ou descurtir                          |
| `/api/postagem/comentar/{id}`                     | PUT         | Comentar                                     |
| `/api/postagem/{id}/comentario/{comentario_id}`   | PUT, DELETE | Editar ou apagar um comentário               |
| `/api/postagem/{id}`                              | DELETE      | Apagar uma postagem própria                  |

Fora login e cadastro, todas esperam `Authorization: Bearer <token>`. As respostas seguem o formato `{ "mensagem", "dados", "status" }`; erros vêm como `{ "detail" }`.

## Estrutura

```
routes/        rotas do FastAPI
services/      regras de negócio
repositories/  acesso ao MongoDB
models/        modelos pydantic (validação e documentação)
middlewares/   dependência que valida o token
providers/     integração com o S3
utils/         senha, ids, upload e conversão de documentos
tests/         testes unitários
```

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

## Segurança

- Senhas gravadas com argon2id. Contas antigas, em bcrypt, continuam entrando e têm a senha regravada em argon2 no primeiro login.
- Nenhuma rota devolve a senha, nem como hash — nem no autor de uma postagem.
- Só o dono apaga a postagem; só o autor edita o comentário; apagar comentário cabe ao autor ou ao dono da postagem.
- Busca escapa o texto antes de usar em expressão regular, e ids malformados respondem 404.
- Upload aceita só imagens de até 5 MB, lidas em memória, sem arquivo temporário em disco.
- Erros inesperados não devolvem o texto da exceção ao cliente.
