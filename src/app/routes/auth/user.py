from fastapi import APIRouter

from src.app.customized.customized_response import AbandonJSONResponse
from src.app.dao.auth.user_dao import UserDao
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
