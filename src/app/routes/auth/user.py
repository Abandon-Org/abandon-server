from typing import List

from fastapi import APIRouter
from starlette import status

from src.app.customized.customized_response import AbandonJSONResponse
from src.app.dao.auth.user_dao import UserDao
from src.app.exception.request import AuthException
from src.app.middleware.my_jwt import AbandonJWT
from src.app.schema.user import UserDto, UserForm

router = APIRouter(prefix="/auth")


# router注册的函数都会自带/auth，所以url是/auth/register
@router.post("/register")
async def register(user: UserDto):
    try:
        user = await UserDao.register_user(**user.dict())
        user = AbandonJSONResponse.model_to_dict(user, "password")
        expire, token = AbandonJWT.get_token(user)
        return AbandonJSONResponse.success(dict(token=token, expire=expire, usr_info=user))
    except Exception as e:
        return AbandonJSONResponse.failed(e)


@router.post("/login")
async def login(data: UserForm):
    try:
        user = await UserDao.login(data.username, data.password)
        user = AbandonJSONResponse.model_to_dict(user, "password")
        expire, token = AbandonJWT.get_token(user)
        return AbandonJSONResponse.success(dict(token=token, expire=expire, usr_info=user))
    except Exception as e:
        return AbandonJSONResponse.failed(e)


@router.get("/listUser")
async def list_users():
    try:
        users = await UserDao.list_users()  # 获取用户列表
        user_list: List[dict] = [AbandonJSONResponse.model_to_dict(user, "password") for user in users]
        # 使用列表推导式遍历用户列表，将每个用户转换为字典形式，并过滤掉密码字段
        # 最终得到一个包含所有用户的字典列表
        return AbandonJSONResponse.success(dict(user_list=user_list))
    except Exception as e:
        return AbandonJSONResponse.failed(str(e))


@router.get("/query")
async def query_user_info(token: str):
    try:
        if not token:
            raise AuthException(status.HTTP_200_OK, "token不存在")
        user_info = AbandonJWT.parse_token(token)
        user = await UserDao.query_user(user_info['id'])
        if user is None:
            return AbandonJSONResponse.failed("用户不存在")
        return AbandonJSONResponse.success(
            dict(token=token, expire=("password",), usr_info=AbandonJSONResponse.model_to_dict(user, "password")))
    except Exception as e:
        return AbandonJSONResponse.failed(e)
