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
        """
        将数据库模型对象转换为字典形式
        :param obj: 数据库模型对象
        :param ignore: 要忽略的属性名称列表
        :return: 字典形式的数据
        """
        if getattr(obj, '__table__', None) is None:
            # 检查对象是否是一个数据库模型对象，如果不是，直接返回对象本身
            return obj

        data = dict()
        for c in obj.__table__.columns:
            if c.name in ignore:
                # 如果属性名在要忽略的属性列表中，则不进行转换
                continue
            val = getattr(obj, c.name)
            if isinstance(val, datetime):
                # 如果属性值是datetime类型，则将属性值转换为指定格式的字符串
                data[c.name] = val.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # 否则，直接使用属性值
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
