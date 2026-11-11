from bson import ObjectId
from fastapi import HTTPException


def para_object_id(id: str, o_que: str = "Registro") -> ObjectId:
    """Converte o id recebido na URL. Id malformado responde 404, não erro 500."""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=404, detail=f"{o_que} não encontrado.")
    return ObjectId(id)
