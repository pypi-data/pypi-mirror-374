from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import CORSConfig


def add_cors_middleware(app: FastAPI, *, config: CORSConfig) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allow_origins,
        allow_methods=config.allow_methods,
        allow_headers=config.allow_headers,
        allow_credentials=config.allow_credentials,
        expose_headers=config.expose_headers,
    )
