import asyncio
import json
import time
from collections.abc import Iterable
from copy import deepcopy
from datetime import datetime
from typing import Tuple, List, TypeVar, Any, Callable

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.basic import AbandonBase
from src.app.utils.log_config import logger


class Mapper(object):
    __model__ = AbandonBase

    @classmethod
    async def select_list(cls, *, session: AsyncSession = None, condition: list = None, **kwargs):
        """
        基础model查询条件
        :param session: 查询session
        :param condition: 自定义查询条件
        :param kwargs: 普通查询条件
        :return:
        """
        sql = cls.query_wrapper(condition, **kwargs)
        result = await session.execute(sql)
        return result.scalars().all()

    @staticmethod
    def like(s: str):
        if s:
            return f"%{s}%"
        return s

    @staticmethod
    def rlike(s: str):
        if s:
            return f"{s}%"
        return s

    @staticmethod
    def llike(s: str):
        if s:
            return f"%{s}"
        return s

    @staticmethod
    async def pagination(page: int, size: int, session, sql: str, scalars=True, **kwargs):
        """
        分页查询
        :param scalars:
        :param session:
        :param page:
        :param size:
        :param sql:
        :return:
        """
        data = await session.execute(sql)
        total = data.raw.rowcount
        if total == 0:
            return [], 0
        sql = sql.offset((page - 1) * size).limit(size)
        data = await session.execute(sql)
        if scalars and kwargs.get("_join") is None:
            return data.scalars().all(), total
        return data.all(), total

    @staticmethod
    def update_model(dist, source, update_user=None, not_null=False):
        """
        :param dist:
        :param source:
        :param not_null:
        :param update_user:
        :return:
        """
        changed = []
        for var, value in vars(source).items():
            if not_null:
                if value is None:
                    continue
                if isinstance(value, bool) or isinstance(value, int) or value:
                    # 如果是bool值或者int, false和0也是可以接受的
                    if not hasattr(dist, var):
                        continue
                    if getattr(dist, var) != value:
                        changed.append(var)
                        setattr(dist, var, value)
            else:
                if getattr(dist, var) != value:
                    changed.append(var)
                    setattr(dist, var, value)
        if update_user:
            setattr(dist, 'update_user', update_user)
        setattr(dist, 'updated_at', datetime.now())
        return changed

    @staticmethod
    def delete_model(dist, update_user):
        """
        删除数据，兼容老的deleted_at
        :param dist:
        :param update_user:
        :return:
        """
        if str(dist.__class__.deleted_at.property.columns[0].type) == "DATETIME":
            dist.deleted_at = datetime.now()
        else:
            dist.deleted_at = int(time.time() * 1000)
        dist.updated_at = datetime.now()
        dist.update_user = update_user

    @classmethod
    async def list_with_pagination(cls, page, size, /, *, session=None, **kwargs):
        """
        通过分页获取数据
        :param session:
        :param page:
        :param size:
        :param kwargs:
        :return:
        """
        return await cls.pagination(page, size, session, cls.query_wrapper(**kwargs), **kwargs)

    @classmethod
    def where(cls, param: Any, sentence, condition: list):
        """
        根据where语句的内容，决定是否生成对应的sql
        :param param:
        :param sentence:
        :param condition:
        :return:
        """
        if param is None:
            return cls
        if isinstance(param, bool):
            condition.append(sentence)
            return cls
        if isinstance(param, int):
            condition.append(sentence)
            return cls
        if param:
            condition.append(sentence)
        return cls

    @classmethod
    def query_wrapper(cls, condition=None, **kwargs):
        """
        包装查询条件，支持like, == 和自定义条件(condition)
        :param condition:
        :param kwargs:
        :return:
        """
        conditions = condition if condition else list()
        if getattr(cls.__model__, "deleted_at", None):
            conditions.append(getattr(cls.__model__, "deleted_at") == 0)
        _sort = kwargs.pop("_sort", None)
        _select = kwargs.pop("_select", list())
        _join = kwargs.pop("_join", None)
        # 遍历参数，当参数不为None的时候传递
        for k, v in kwargs.items():
            # 判断是否是like的情况
            like = isinstance(v, str) and (v.startswith("%") or v.endswith("%"))
            if like and v == "%%":
                continue
            # 如果是like模式，则使用Model.字段.like 否则用 Model.字段 等于
            cls.where(v, getattr(cls.__model__, k).like(v) if like else getattr(cls.__model__, k) == v,
                      conditions)
        sql = select(cls.__model__, *_select)
        if isinstance(_join, Iterable):
            for j in _join:
                sql = sql.outerjoin(*j)
        where = sql.where(*conditions)
        if _sort and isinstance(_sort, Iterable):
            for d in _sort:
                where = getattr(where, "order_by")(d)
        return where

    @classmethod
    async def query_record(cls, session: AsyncSession = None, **kwargs):
        sql = cls.query_wrapper(**kwargs)
        result = await session.execute(sql)
        return result.scalars().first()