import io
import logging
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from decouple import config

log = logging.getLogger(__name__)


class AWSProvider:
    def upload_imagem(self, chave: str, conteudo: bytes, tipo: str) -> Optional[str]:
        """Envia a imagem para o S3 e devolve a URL pública, ou None se falhar."""
        bucket = config("AWS_BUCKET", default="") or "devagram-python-ps"
        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=config("AWS_ACCESS_KEY"),
                aws_secret_access_key=config("AWS_SECRET_KEY"),
            )
            s3_client.upload_fileobj(
                io.BytesIO(conteudo), bucket, chave, ExtraArgs={"ContentType": tipo}
            )
            return f"https://{bucket}.s3.amazonaws.com/{chave}"
        except (BotoCoreError, ClientError, Exception):  # noqa: BLE001
            # O cadastro segue sem a foto; o motivo fica só no log do servidor.
            log.exception("Falha ao enviar imagem para o S3")
            return None
