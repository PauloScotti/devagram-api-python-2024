from decouple import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from routes.AutenticacaoRoute import router as AutenticacaoRoute
from routes.PostagemRoute import router as PostagemRoute
from routes.UsuarioRoute import router as UsuarioRoute

app = FastAPI(
    title="Devagram API",
    version="2.0.0",
    description=(
        "API de uma rede social de fotos: usuários, postagens, curtidas, comentários e seguidores. "
        "Fora o login e o cadastro, as rotas exigem `Authorization: Bearer <token>`."
    ),
)

# CORS_ORIGENS: lista separada por vírgula. Sem ela, qualquer origem é aceita
# (a API autentica por token no cabeçalho, não por cookie).
origens = [o.strip() for o in config("CORS_ORIGENS", default="").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origens or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(UsuarioRoute, tags=["Usuário"], prefix="/api/usuario")
app.include_router(AutenticacaoRoute, tags=["Autenticação"], prefix="/api/auth")
app.include_router(PostagemRoute, tags=["Postagem"], prefix="/api/postagem")


@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "OK!"}


# Swagger UI continua em /docs; a referência Scalar fica em /reference.
@app.get("/reference", include_in_schema=False)
async def referencia_scalar():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title=app.title)
