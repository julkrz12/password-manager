from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .db import Base, engine
from .routes import auth, vault, tools


def create_app() -> FastAPI:
    app = FastAPI(title='Password Manager MVP', version='1.0.0')

    # init DB
    Base.metadata.create_all(bind=engine)

    app.include_router(auth.router)
    app.include_router(vault.router)
    app.include_router(tools.router)

    # static frontend
    static_dir = Path(__file__).resolve().parents[2] / 'frontend'
    app.mount('/static', StaticFiles(directory=static_dir), name='static')

    @app.get('/')
    def index():
        return FileResponse(static_dir / 'index.html')

    return app


app = create_app()
