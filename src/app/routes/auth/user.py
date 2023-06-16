from fastapi import APIRouter

from src.app.custom.custom_msg import CustomMessage
from src.app.custom.custom_code import CustomCode

router = APIRouter(prefix="/auth")


# router注册的函数都会自带/auth，所以url是/auth/register
@router.post("/register")
async def register():
    data: dict = {"token": "xxxxx", "user": {}}
    return dict({"code": CustomCode.TESTCODE, "msg": CustomMessage.TESTMESSAGE, "data": data})


@router.post("/login")
async def login():
    return "登陆成功"
