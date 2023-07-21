from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.routes.auth import user
from src.app.routes.request import http

abandon = FastAPI()

# 注册路由
abandon.include_router(user.router)
abandon.include_router(http.router)

abandon.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
