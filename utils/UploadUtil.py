from fastapi import HTTPException, UploadFile

TAMANHO_MAXIMO = 5 * 1024 * 1024
TIPOS_ACEITOS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}


async def ler_imagem(arquivo: UploadFile) -> tuple[bytes, str, str]:
    """Lê o upload em memória e devolve (conteúdo, tipo, extensão)."""
    if arquivo.content_type not in TIPOS_ACEITOS:
        raise HTTPException(
            status_code=400, detail="A imagem precisa ser JPEG, PNG, WebP ou GIF."
        )
    conteudo = await arquivo.read(TAMANHO_MAXIMO + 1)
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(
            status_code=400, detail="A imagem pode ter no máximo 5 MB."
        )
    if not conteudo:
        raise HTTPException(status_code=400, detail="A imagem está vazia.")
    return conteudo, arquivo.content_type, TIPOS_ACEITOS[arquivo.content_type]
