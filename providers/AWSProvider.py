import boto3
from botocore.exceptions import ClientError
from decouple import config


class AWSProvider:

    def upload_arquivo_s3(self, caminho_para_salvar, caminho_do_arquivo, bucket='devagram-python-ps'):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY'),
            aws_secret_access_key=config('AWS_SECRET_KEY')
        )

        try:
            s3_client.upload_file(caminho_do_arquivo, bucket, caminho_para_salvar)

            url = s3_client.generate_presigned_url(
                'get_object',
                ExpiresIn=0,
                Params={'Bucket': bucket, 'Key': caminho_para_salvar}
            )

            return str(url).split('?')[0]

        except ClientError as erro:
            print(erro)
            return False
