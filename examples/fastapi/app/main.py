from app.routers import login
from fastapi import FastAPI

APP_NAME = "Pyencrypt FastAPI Demo"
APP_VERSION = "1.0.0"

DEBUG = True
HOST = "127.0.0.1"
PORT = 8000


def create_app() -> FastAPI:
    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description="A FastAPI example demo application using pyencrypt.",
        debug=DEBUG,
    )

    app.include_router(login.router)
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug",
    )
