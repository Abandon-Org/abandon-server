from fastapi import APIRouter

from src.app.customized.customized_response import AbandonJSONResponse
from src.app.middleware.my_jwt import AbandonJWT

router = APIRouter(prefix="/auth")


# router注册的函数都会自带/auth，所以url是/auth/register
@router.post("/register")
async def register():
    usr_info: dict = {'这是一个usr': 1}
    expire, token = AbandonJWT.get_token(usr_info)
    return AbandonJSONResponse.success(dict(token=token, expire=expire, usr_info=usr_info))


@router.post("/login")
async def login():
    return "登陆成功"
