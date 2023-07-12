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

    @staticmethod
    def model_to_dict(obj, *ignore: str):
        if getattr(obj, '__table__', None) is None:
            return obj
        data = dict()
        for c in obj.__table__.columns:
            if c.name in ignore:
                # 如果字段忽略, 则不进行转换
                continue
            val = getattr(obj, c.name)
            if isinstance(val, datetime):
                data[c.name] = val.strftime("%Y-%m-%d %H:%M:%S")
            else:
                data[c.name] = val
        return data

    @staticmethod
    def failed(msg, code=CustomCode.REGISTER_FAILED, data=None):
        return dict(code=code, msg=str(msg), data=data)

    @staticmethod
    def success(data=None, code=CustomCode.SUCCESS, msg=CustomMessage.SUCCESS, timestamp=int(time.time()), exclude=()):
        return AbandonJSONResponse.encode_json(dict(code=code, msg=msg, data=data, timestamp=timestamp), *exclude)

    @staticmethod
    def encode_json(data: Any, *exclude: str):
        return jsonable_encoder(data, exclude=exclude, custom_encoder={
            datetime: lambda x: str(int(time.time()))
        })


if __name__ == '__main__':
    print(AbandonJSONResponse.encode_json(
        {'code': 200, 'msg': 'Operation successful!', 'data': '2222', 'timestamp': 1687251482}))
