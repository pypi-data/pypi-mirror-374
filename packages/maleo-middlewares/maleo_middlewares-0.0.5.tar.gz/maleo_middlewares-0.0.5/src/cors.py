from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from maleo.dtos.config.middleware import CORSMiddlewareConfig


def add_cors_middleware(app: FastAPI, *, configuration: CORSMiddlewareConfig) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=configuration.allow_origins,
        allow_methods=configuration.allow_methods,
        allow_headers=configuration.allow_headers,
        allow_credentials=configuration.allow_credentials,
        expose_headers=configuration.expose_headers,
    )
