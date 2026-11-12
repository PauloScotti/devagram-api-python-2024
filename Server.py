import uvicorn
from decouple import config

if __name__ == "__main__":
    uvicorn.run(
        "Main:app",
        host="0.0.0.0",
        port=config("PORT", default=5000, cast=int),
        reload=config("RELOAD", default=False, cast=bool),
    )
