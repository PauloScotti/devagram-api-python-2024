import os
import sys
from pathlib import Path

# Os módulos leem a configuração ao serem importados.
os.environ.setdefault("MONGODB_URL", "mongodb://127.0.0.1:27017")
os.environ.setdefault("JWT_SECRET", "segredo-de-teste-com-mais-de-32-bytes")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
