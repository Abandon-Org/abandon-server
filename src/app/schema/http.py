from typing import Optional, Union
from pydantic import BaseModel, validator

from src.app.exception.error import ParamsError


# 定义一个数据模型，用于接收HTTP请求的相关信息
class HttpRequestForm(BaseModel):
    method: str
    url: str
    # 定义HTTP请求的请求体，可以是字典或列表类型，可选参数，默认为None
    body: Optional[Union[dict, list]] = None
    body_type: str
    # 定义HTTP请求的请求头，可以是字典类型，可选参数，默认为一个空字典
    headers: Optional[dict] = {}

    # 使用pydantic的validator装饰器，对method和url字段进行验证
    @validator('method', 'url')
    def name_not_empty(cls, v):
        # 验证方法：检查字符串是否为空或仅包含空格
        if isinstance(v, str) and len(v.strip()) == 0:
            # 如果为空，抛出自定义异常ParamsError，提示不能为空
            raise ParamsError("不能为空")
        # 如果验证通过，返回原始值v
        return v
