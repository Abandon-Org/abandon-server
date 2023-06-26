import dataclasses
import json
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import PurePath
from types import GeneratorType
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel
from pydantic.json import ENCODERS_BY_TYPE

SetIntStr = Set[Union[int, str]]  # 定义 SetIntStr 类型为 int 和 str 的集合
DictIntStrAny = Dict[Union[int, str], Any]  # 定义 DictIntStrAny 类型为 int 或 str 作为键，任意类型作为值的字典
TupleIntStr = Tuple[str]  # 定义 TupleIntStr 类型为只包含字符串的元组


class JsonEncoder(json.JSONEncoder):  # 定义 JsonEncoder 类，继承自 json.JSONEncoder 类

    def default(self, o: Any) -> Any:  # 定义 default 方法，接受一个任意类型的参数 o，返回一个任意类型的结果
        if isinstance(o, set):  # 如果 o 是 set 类型
            return list(o)  # 将其转换为列表类型并返回
        if isinstance(o, datetime):  # 如果 o 是 datetime 类型
            # return str(int(o.timestamp()))  # 返回十位时间戳（将 datetime 类型转换为字符串类型）
            return o.strftime("%Y-%m-%d %H:%M:%S")  # 返回格式化的时间字符串
        if isinstance(o, Decimal):  # 如果 o 是 Decimal 类型
            return str(o)  # 将其转换为字符串类型并返回
        if isinstance(o, bytes):  # 如果 o 是 bytes 类型
            return o.decode(encoding='utf-8')  # 将其转换为字符串类型并返回

        return self.default(o)  # 否则递归调用 default 方法


def generate_encoders_by_class_tuples(# 定义 generate_encoders_by_class_tuples 函数，接受一个字典类型的参数 type_encoder_map，返回一个字典类型的结果
        type_encoder_map: Dict[Any, Callable[[Any], Any]]
) -> Dict[Callable[[Any], Any], Tuple[Any, ...]]:
    encoders_by_class_tuples: Dict[Callable[[Any], Any], Tuple[Any, ...]] = defaultdict(
        tuple
    )  # 定义 encoders_by_class_tuples 变量，初始化为空 defaultdict 对象
    for type_, encoder in type_encoder_map.items():  # 遍历 type_encoder_map 中的每一项
        encoders_by_class_tuples[encoder] += (type_,)  # 将 encoder 添加到 encoders_by_class_tuples 中对应类型的元组中
    return encoders_by_class_tuples  # 返回 encoders_by_class_tuples 变量


encoders_by_class_tuples = generate_encoders_by_class_tuples(ENCODERS_BY_TYPE)  # 调用 generate_encoders_by_class_tuples 函数，将 ENCODERS_BY_TYPE 变量作为参数，并将结果赋值给 encoders_by_class_tuples 变量


def jsonable_encoder(  # 定义 jsonable_encoder 函数，接受一个任意类型的参数 obj，以及一些可选参数，返回一个任意类型的结果
        obj: Any,
        include: Optional[Union[SetIntStr, DictIntStrAny, TupleIntStr]] = None,
        exclude: Optional[Union[SetIntStr, DictIntStrAny, TupleIntStr]] = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        custom_encoder: Optional[Dict[Any, Callable[[Any], Any]]] = None,
        sqlalchemy_safe: bool = True,
) -> Any:
    custom_encoder = custom_encoder or {}  # 如果 custom_encoder 是 None，就将其设为一个空字典
    if custom_encoder:  # 如果 custom_encoder 不为空
        if type(obj) in custom_encoder:  # 如果 obj 的类型在 custom_encoder 中
            return custom_encoder[type(obj)](obj)  # 调用 custom_encoder 中对应类型的函数并将 obj 作为参数，返回结果
        else:  # 否则
            for encoder_type, encoder_instance in custom_encoder.items():  # 遍历 custom_encoder 中的每一项
                if isinstance(obj, encoder_type):  # 如果 obj 是 encoder_type 类型的实例
                    return encoder_instance(obj)  # 调用 encoder_instance 函数并将 obj 作为参数，返回结果
    if include is not None and not isinstance(include, (set, dict)):  # 如果 include 不为空且不是集合或字典类型
        include = set(include)  # 将其转换为集合类型
    if exclude is not None and not isinstance(exclude, (set, dict)):  # 如果 exclude 不为空且不是集合或字典类型
        exclude = set(exclude)  # 将其转换为集合类型
    if isinstance(obj, BaseModel):  # 如果 obj 是 BaseModel 的实例
        encoder = getattr(obj.__config__, "json_encoders", {})  # 从 obj.__config__.json_encoders 中获取 encoder 变量，如果没有则设为一个空字典
        if custom_encoder:  # 如果 custom_encoder 不为空
            encoder.update(custom_encoder)  # 将 custom_encoder 添加到 encoder 中
        obj_dict = obj.dict(  # 将 obj 转换为字典类型
            include=include,  # 包含哪些键
            exclude=exclude,  # 排除哪些键
            by_alias=by_alias,  # 是否使用别名
            exclude_unset=exclude_unset,  # 是否排除未设置的键
            exclude_none=exclude_none,  # 是否排除值为 None 的键
            exclude_defaults=exclude_defaults,  # 是否排除默认值的键
        )
        if "__root__" in obj_dict:  # 如果 "__root__" 在 obj_dict 中
            obj_dict = obj_dict["__root__"]  # 则将其赋值给 obj_dict
        return jsonable_encoder(  # 递归调用 jsonable_encoder 函数
            obj_dict,  # 参数为 obj_dict
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
            custom_encoder=encoder,
            sqlalchemy_safe=sqlalchemy_safe,
        )
    if dataclasses.is_dataclass(obj):  # 如果 obj 是 dataclass 的实例
        return dataclasses.asdict(obj)  # 将其转换为字典类型并返回
    if isinstance(obj, Enum):  # 如果 obj 是 Enum 的实例
        return obj.value  # 返回 obj 的 value 属性
    if isinstance(obj, PurePath):  # 如果 obj 是 PurePath 的实例
        return str(obj)  # 将其转换为字符串类型并返回
    if isinstance(obj, (str, int, float, type(None))):  # 如果 obj 是字符串、整数、浮点数或 None 类型
        return obj  # 直接返回 obj
    if isinstance(obj, dict):  # 如果 obj 是字典类型
        encoded_dict = {}  # 定义 encoded_dict 变量，初始化为空字典
        for key, value in obj.items():  # 遍历 obj 中的每一项
            if (
                    (
                            not sqlalchemy_safe  # 如果 sqlalchemy_safe 为 False
                            or (not isinstance(key, str))  # 或者 key 不是字符串类型
                            or (not key.startswith("_sa"))  # 或者 key 不是以 "_sa" 开头的字符串
                    )
                    and (value is not None or not exclude_none)  # 并且 value 不是 None 或者 exclude_none 为 False
                    and ((include and key in include) or not exclude or key not in exclude)  # 并且 key 包含在 include 中或者 exclude 为 None 或者 key 不在 exclude 中
            ):
                encoded_key = jsonable_encoder(  # 将 key 转换为 JSON 格式
                    key,
                    exclude=exclude,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_value = jsonable_encoder(  # 将 value 转换为 JSON 格式
                    value,
                    by_alias=by_alias,
                    exclude=exclude,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_dict[encoded_key] = encoded_value  # 将转换后的键值对添加到 encoded_dict 中
        return encoded_dict  # 返回 encoded_dict 变量
    if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):  # 如果 obj 是列表、集合、冻结集合、生成器或元组类型
        encoded_list = []  # 定义 encoded_list 变量，初始化为空列表
        for item in obj:  # 遍历 obj 中的每一项
            encoded_list.append(  # 将转换后的项添加到 encoded_list 中
                jsonable_encoder(
                    item,
                    include=include,
                    exclude=exclude,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
            )
        return encoded_list  # 返回 encoded_list 变量

    if type(obj) in ENCODERS_BY_TYPE:  # 如果 obj 的类型在 ENCODERS_BY_TYPE 中
        return ENCODERS_BY_TYPE[type(obj)](obj)  # 调用 ENCODERS_BY_TYPE 中对应类型的函数并将 obj 作为参数，返回结果
    for encoder, classes_tuple in encoders_by_class_tuples.items():  # 遍历 encoders_by_class_tuples 中的每一项
        if isinstance(obj, classes_tuple):  # 如果 obj 是 classes_tuple 中的任意一种类型的实例
            return encoder(obj)  # 调用 encoder
