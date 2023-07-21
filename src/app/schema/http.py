from typing import Optional, Union

from fastapi import Body
from pydantic import BaseModel, validator

from src.app.exception.error import ParamsError


class HttpRequestForm(BaseModel):
    method: str
    url: str
    body: Optional[Union[dict, str]] = Body(None),
    # body样式为：{"body": "xx", "body_type": "json"}
    headers: Optional[dict]

    @validator('method', 'url')
    def name_not_empty(cls, v):
        if isinstance(v, str) and len(v.strip()) == 0:
            raise ParamsError("不能为空")
        return v
