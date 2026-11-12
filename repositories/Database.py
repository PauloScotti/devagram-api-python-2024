import motor.motor_asyncio
from decouple import config

# Um único cliente para a aplicação inteira; a conexão só abre no primeiro uso.
cliente = motor.motor_asyncio.AsyncIOMotorClient(config("MONGODB_URL"))
database = cliente.devagram
