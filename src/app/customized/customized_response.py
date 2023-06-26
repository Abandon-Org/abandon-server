import time
from datetime import datetime

from fastapi.responses import JSONResponse  # 导入 FastAPI 的 JSONResponse 响应类
from typing import Any

from src.app.custom.custom_code import CustomCode  # 导入自定义的响应码类
from src.app.custom.custom_msg import CustomMessage  # 导入自定义的响应信息类
from src.app.middleware.encoder import jsonable_encoder


class AbandonJSONResponse(JSONResponse):
    """
    定义一个继承自 JSONResponse 的类，用于自定义响应
    """

    # @staticmethod  # 静态方法装饰器，用于声明 success 方法为类方法，而不是对象方法
    # def success(data=None, code=CustomCode.SUCCESS, msg=CustomMessage.SUCCESS, timestamp=int(time.time()), exclude=()):
    #     # 定义 success 方法，接受三个参数，data 表示要返回的数据，code 表示响应码，msg 表示响应信息
    #     return AbandonJSONResponse.encode_json(dict(code=code, msg=msg, data=data, timestamp=timestamp), *exclude)
    #     # 返回一个 JSONResponse 对象，其中包含响应码、响应信息、数据和时间戳
    @staticmethod
    def success(data=None, code=CustomCode.SUCCESS, msg=CustomMessage.SUCCESS, timestamp=int(time.time()), exclude=()):
        return AbandonJSONResponse.encode_json(dict(code=code, msg=msg, data=data, timestamp=timestamp), *exclude)

    @staticmethod
    def encode_json(data: Any, *exclude: str):
        return jsonable_encoder(data, exclude=exclude, custom_encoder={
            datetime: lambda x: str(int(time.time()))
        })


if __name__ == '__main__':
    print(AbandonJSONResponse.encode_json({'code': 200, 'msg': 'Operation successful!', 'data': '2222', 'timestamp': 1687251482}))