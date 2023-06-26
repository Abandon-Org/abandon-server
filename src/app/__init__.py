from fastapi import FastAPI
from src.app.routes.auth import user

abandon = FastAPI()


# 注册路由
abandon.include_router(user.router)